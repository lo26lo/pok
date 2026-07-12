#!/usr/bin/env python3
"""
Vue « 📊 Evaluation » (F07) : analyse des runs d'entraînement.

- Sélection d'un run de runs/train/ : métriques du meilleur epoch,
  hyperparamètres, real_mAP (F08) si disponible.
- Affichage des artefacts Ultralytics (results.png, matrice de confusion,
  courbes PR/F1, aperçus de validation) sans les recalculer.
- Comparaison A/B entre deux runs (deltas des métriques).
- Galerie des « pires prédictions » : le modèle du run est rejoué sur le
  set réel (F08) ou la val synthétique, images triées par erreurs
  (manqués / faux positifs / mauvaise classe), rendu en planche contact.

Même règle thread-safe que la v3.6 : le travail lourd tourne en thread,
les résultats reviennent par une file pollée sur le thread principal.
"""
import base64
import os
import queue
import threading
from typing import Dict, Optional

import cv2

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:  # environnement headless sans python3-tk
    tk = None

from gui.theme import COLORS

PLOT_MAX_W, PLOT_MAX_H = 840, 540

PLOT_LABELS = {
    "results": "📈 Courbes",
    "confusion_matrix": "🧩 Confusion",
    "confusion_matrix_normalized": "🧩 Confusion (norm.)",
    "PR_curve": "📐 PR",
    "F1_curve": "📐 F1",
    "P_curve": "📐 P",
    "R_curve": "📐 R",
    "labels": "🏷️ Labels",
}


def load_image_fit(path: str, max_w: int = PLOT_MAX_W,
                   max_h: int = PLOT_MAX_H) -> Optional[str]:
    """
    Charge une image et la réduit pour tenir dans (max_w, max_h) en
    conservant le ratio ; retourne des données base64 PNG pour
    tk.PhotoImage. Pur (sans Tk) — testable headless.
    """
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        return None
    h, w = img.shape[:2]
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1.0:
        img = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))),
                         interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        return None
    return base64.b64encode(buf.tobytes()).decode("ascii")


def format_summary(summary: Dict) -> str:
    """Texte multi-lignes du résumé d'un run (pur, testable)."""
    lines = [f"🏃 {summary.get('name', '?')}"]
    if summary.get("epochs_done"):
        best = summary.get("best_epoch")
        lines.append(f"Epochs: {summary['epochs_done']}"
                     + (f" (meilleur: {best})" if best is not None else ""))
    metrics = summary.get("metrics", {})
    order = ["mAP50", "mAP50-95", "precision", "recall", "real_mAP50"]
    for key in order:
        if key in metrics:
            marker = " 🌍" if key.startswith("real_") else ""
            lines.append(f"{key}: {metrics[key]:.3f}{marker}")
    args = summary.get("args", {})
    if args:
        parts = [f"{k}={args[k]}" for k in
                 ("model", "epochs", "batch", "imgsz") if args.get(k)]
        if parts:
            lines.append("⚙️ " + "  ".join(str(p) for p in parts))
    if not metrics and not summary.get("epochs_done"):
        lines.append("(pas de results.csv — run incomplet)")
    return "\n".join(lines)


def format_comparison(summary_a: Dict, summary_b: Dict,
                      deltas: Dict[str, float]) -> str:
    """Texte de comparaison A/B (pur, testable)."""
    if not deltas:
        return "Aucune métrique commune."
    lines = [f"Δ = {summary_b.get('name')} − {summary_a.get('name')}"]
    for key, delta in deltas.items():
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
        lines.append(f"{key}: {arrow} {delta:+.3f}")
    return "\n".join(lines)


if tk is not None:

    class EvaluationView(tk.Frame):
        """Vue Évaluation, à packer dans le container de vue de la GUI."""

        def __init__(self, parent, app=None, colors: Optional[Dict] = None,
                     runs_dir: Optional[str] = None):
            self.colors = colors or (app.colors if app is not None else COLORS)
            super().__init__(parent, bg=self.colors['bg_dark'])
            self.app = app

            from core.run_analyzer import RUNS_DIR
            self.runs_dir = runs_dir or RUNS_DIR

            self._runs = []
            self._summary = None
            self._photo = None                # ref anti garbage-collector
            self._results: "queue.Queue" = queue.Queue()
            self._busy = False

            self._build_ui()
            self.after(100, self._poll_results)
            self.reload_runs()

        # ------------------------------------------------------------ UI

        def _build_ui(self):
            c = self.colors

            tk.Label(self, text="📊 Evaluation des runs",
                     font=('Segoe UI', 16, 'bold'), bg=c['bg_dark'],
                     fg=c['text']).pack(anchor='w', padx=20, pady=(15, 10))

            top = tk.Frame(self, bg=c['bg_dark'])
            top.pack(fill=tk.X, padx=20)

            tk.Label(top, text="Run:", bg=c['bg_dark'], fg=c['text'],
                     font=('Segoe UI', 10)).pack(side=tk.LEFT)
            self.run_var = tk.StringVar()
            self.run_combo = ttk.Combobox(top, textvariable=self.run_var,
                                          state='readonly', width=32)
            self.run_combo.pack(side=tk.LEFT, padx=8)
            self.run_combo.bind("<<ComboboxSelected>>",
                                lambda e: self._on_run_selected())

            tk.Label(top, text="Comparer à:", bg=c['bg_dark'], fg=c['text'],
                     font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(15, 0))
            self.compare_var = tk.StringVar()
            self.compare_combo = ttk.Combobox(top, textvariable=self.compare_var,
                                              state='readonly', width=32)
            self.compare_combo.pack(side=tk.LEFT, padx=8)
            self.compare_combo.bind("<<ComboboxSelected>>",
                                    lambda e: self._on_compare_selected())

            ttk.Button(top, text="🔄", width=4,
                       command=self.reload_runs).pack(side=tk.LEFT, padx=8)

            body = tk.Frame(self, bg=c['bg_dark'])
            body.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            # Colonne gauche : résumé + comparaison + actions
            left = tk.Frame(body, bg=c['bg_card'], width=280)
            left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
            left.pack_propagate(False)

            self.summary_var = tk.StringVar(value="Aucun run sélectionné")
            tk.Label(left, textvariable=self.summary_var, bg=c['bg_card'],
                     fg=c['text'], justify='left', anchor='nw',
                     font=('Consolas', 10), wraplength=250
                     ).pack(fill=tk.X, padx=15, pady=(15, 10))

            self.compare_text_var = tk.StringVar(value="")
            tk.Label(left, textvariable=self.compare_text_var,
                     bg=c['bg_card'], fg=c['accent'], justify='left',
                     anchor='nw', font=('Consolas', 10), wraplength=250
                     ).pack(fill=tk.X, padx=15, pady=(0, 10))

            ttk.Button(left, text="🔍 Pires prédictions",
                       command=self.show_worst_predictions
                       ).pack(fill=tk.X, padx=15, pady=4)

            self.status_var = tk.StringVar(value="")
            tk.Label(left, textvariable=self.status_var, bg=c['bg_card'],
                     fg=c['text_dim'], justify='left', wraplength=250,
                     font=('Segoe UI', 9)).pack(fill=tk.X, padx=15, pady=8)

            # Colonne droite : boutons d'artefacts + zone d'affichage
            right = tk.Frame(body, bg=c['bg_dark'])
            right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.plot_buttons = tk.Frame(right, bg=c['bg_dark'])
            self.plot_buttons.pack(fill=tk.X)

            self.image_label = tk.Label(right, bg=c['bg_card'],
                                        text="Sélectionnez un run",
                                        fg=c['text_dim'])
            self.image_label.pack(fill=tk.BOTH, expand=True, pady=8)

        # ------------------------------------------------------- Actions

        def reload_runs(self):
            from core.run_analyzer import list_runs
            self._runs = list_runs(self.runs_dir)
            names = [r["name"] for r in self._runs]
            self.run_combo["values"] = names
            self.compare_combo["values"] = ["—"] + names
            if names:
                self.run_var.set(names[0])
                self._on_run_selected()
            else:
                self.summary_var.set(
                    f"Aucun run dans {self.runs_dir}\n"
                    "Lancez un entraînement d'abord.")

        def _selected_run(self) -> Optional[Dict]:
            for run in self._runs:
                if run["name"] == self.run_var.get():
                    return run
            return None

        def _on_run_selected(self):
            from core.run_analyzer import run_summary, available_plots
            run = self._selected_run()
            if run is None:
                return
            self._summary = run_summary(run["path"])
            self.summary_var.set(format_summary(self._summary))
            self.compare_text_var.set("")
            self.compare_var.set("—")
            self._rebuild_plot_buttons(available_plots(run["path"]))

        def _on_compare_selected(self):
            from core.run_analyzer import run_summary, compare_runs
            other_name = self.compare_var.get()
            if other_name in ("", "—") or self._summary is None:
                self.compare_text_var.set("")
                return
            other = next((r for r in self._runs if r["name"] == other_name),
                         None)
            if other is None:
                return
            other_summary = run_summary(other["path"])
            deltas = compare_runs(self._summary, other_summary)
            self.compare_text_var.set(
                format_comparison(self._summary, other_summary, deltas))

        def _rebuild_plot_buttons(self, plots: Dict[str, str]):
            for widget in self.plot_buttons.winfo_children():
                widget.destroy()
            if not plots:
                self._show_message("Aucun artefact (results.png…) dans ce run")
                return
            for name, path in plots.items():
                label = PLOT_LABELS.get(name, name)
                ttk.Button(self.plot_buttons, text=label,
                           command=lambda p=path: self._show_plot(p)
                           ).pack(side=tk.LEFT, padx=2, pady=2)
            self._show_plot(next(iter(plots.values())))

        def _show_plot(self, path: str):
            data = load_image_fit(path)
            if data is None:
                self._show_message(f"Illisible: {os.path.basename(path)}")
                return
            self._photo = tk.PhotoImage(data=data)
            self.image_label.config(image=self._photo, text="")

        def _show_message(self, text: str):
            self._photo = None
            self.image_label.config(image="", text=text)

        # --------------------------------------------- Pires prédictions

        def show_worst_predictions(self):
            """Rejoue le modèle du run sur le set réel/val (en thread)."""
            if self._busy:
                return
            if self._summary is None or not self._summary.get("best_model"):
                self.status_var.set("⚠️ Pas de best.pt dans ce run")
                return

            from core.run_analyzer import resolve_eval_source
            source = resolve_eval_source()
            if source is None:
                self.status_var.set(
                    "⚠️ Aucune source d'images : préparez le set réel "
                    "(datasets/real_val) ou générez le dataset fusionné")
                return

            model_path = self._summary["best_model"]
            self._busy = True
            self.status_var.set(
                f"⏳ Analyse de {len(source['images'])} images "
                f"({source['label']})…")

            def worker():
                try:
                    from core.run_analyzer import (rank_worst_images,
                                                   build_worst_sheet)
                    ranked = rank_worst_images(
                        model_path, source["images"], source["labels_dir"],
                        top_k=8, log=lambda m: None)
                    if ranked is None:
                        self._results.put(("status",
                                           "❌ ultralytics non installé"))
                        return
                    sheet = build_worst_sheet(ranked)
                    ok, buf = cv2.imencode(".png", sheet)
                    data = base64.b64encode(buf.tobytes()).decode("ascii")
                    worst = ranked[0]["score"] if ranked else 0
                    self._results.put(("sheet", data,
                                       f"✅ Pires prédictions "
                                       f"({source['label']}) — "
                                       f"pire score: {worst}"))
                except Exception as exc:
                    self._results.put(("status", f"❌ {exc}"))

            threading.Thread(target=worker, daemon=True).start()

        def _poll_results(self):
            """Applique les résultats des workers (thread principal)."""
            try:
                while True:
                    item = self._results.get_nowait()
                    self._busy = False
                    if item[0] == "sheet":
                        _, data, status = item
                        self._photo = tk.PhotoImage(data=data)
                        self.image_label.config(image=self._photo, text="")
                        self.status_var.set(status)
                    else:
                        self.status_var.set(item[1])
            except queue.Empty:
                pass
            try:
                if self.winfo_exists():
                    self.after(150, self._poll_results)
            except tk.TclError:
                pass  # vue détruite

else:  # pragma: no cover - environnement sans tkinter

    class EvaluationView:
        """Stub : tkinter absent (headless). La vue est indisponible."""

        def __init__(self, *args, **kwargs):
            raise ImportError("tkinter n'est pas disponible sur ce systeme")
