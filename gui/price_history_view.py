#!/usr/bin/env python3
"""
Fenêtre « 💹 Price History » (F09).

Affiche l'évolution du prix d'une carte en sparkline (canvas Tk pur, aucune
dépendance graphique) depuis l'historique du cache F10
(models/price_cache.db, table append-only price_snapshots), et gère les
alertes de seuil : notifier quand une carte dépasse (ou passe sous) un prix.

Les alertes sont évaluées à chaque relevé (fin de préchargement) et via le
bouton « 🔔 Check alerts » de cette fenêtre.
"""
from typing import Dict, List, Optional, Sequence, Tuple

# tkinter optionnel : les helpers purs (sparkline_points, format_history_label)
# restent utilisables/testables sans display ni Tk
try:
    import tkinter as tk
    from tkinter import messagebox, ttk
except ImportError:  # environnement headless sans python3-tk
    tk = None

from gui.theme import COLORS

SPARK_W, SPARK_H = 560, 160
SPARK_PAD = 12


def sparkline_points(values: Sequence[float], width: int = SPARK_W,
                     height: int = SPARK_H,
                     pad: int = SPARK_PAD) -> List[Tuple[float, float]]:
    """
    Convertit une série de prix (chronologique) en points (x, y) pour un
    canvas Tk (y inversé). Pur (sans Tk) — testable sans display.

    Série vide -> [] ; un seul point ou série plate -> ligne à mi-hauteur.
    """
    values = [v for v in values if v is not None]
    if not values:
        return []
    lo, hi = min(values), max(values)
    span_x = max(1, len(values) - 1)
    inner_w, inner_h = width - 2 * pad, height - 2 * pad

    points = []
    for i, v in enumerate(values):
        x = pad + i * inner_w / span_x
        if hi == lo:
            y = height / 2.0
        else:
            y = pad + (hi - v) * inner_h / (hi - lo)
        points.append((x, y))
    return points


def format_history_label(entries) -> str:
    """
    Libellé de synthèse d'un historique (liste de PriceEntry, du plus
    récent au plus ancien). Pur — testable sans Tk.
    """
    priced = [e for e in entries if e.price is not None]
    if not priced:
        return "Aucun relevé de prix"
    current = priced[0]
    prices = [e.price for e in priced]
    label = (f"{current.price:.2f}€ actuellement — "
             f"min {min(prices):.2f}€ / max {max(prices):.2f}€ "
             f"sur {len(priced)} relevés")
    if len(priced) > 1:
        first, last = priced[-1], priced[0]
        delta = last.price - first.price
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "＝")
        label += f" ({arrow} {delta:+.2f}€ depuis le {first.date_str})"
    return label


if tk is not None:

    class PriceHistoryDialog(tk.Toplevel):
        """Fenêtre historique des prix + alertes de seuil (F09)."""

        def __init__(self, parent, colors: Optional[Dict] = None,
                     db_path: Optional[str] = None):
            super().__init__(parent)
            self.colors = colors or COLORS
            self.title("💹 Price History")
            self.geometry("640x560")
            self.configure(bg=self.colors['bg_dark'])
            self.transient(parent)

            from core.price_cache import PriceCache, load_prices_with_cache
            self.cache = PriceCache(db_path)
            self._names = {cid: (info.get('name') or '')
                           for cid, info in load_prices_with_cache().items()}

            self._build_ui()
            self._reload_cards()
            self._refresh_alerts()

        # ---------- UI ----------

        def _label(self, parent, text, **kw):
            return tk.Label(parent, text=text, bg=self.colors['bg_dark'],
                            fg=self.colors['text'], **kw)

        def _build_ui(self):
            top = tk.Frame(self, bg=self.colors['bg_dark'])
            top.pack(fill=tk.X, padx=15, pady=(15, 5))

            self._label(top, "Carte :").pack(side=tk.LEFT)
            self.card_var = tk.StringVar()
            self.card_combo = ttk.Combobox(top, textvariable=self.card_var,
                                           width=45, state="readonly")
            self.card_combo.pack(side=tk.LEFT, padx=10)
            self.card_combo.bind("<<ComboboxSelected>>",
                                 lambda e: self._refresh_chart())

            self.canvas = tk.Canvas(self, width=SPARK_W, height=SPARK_H,
                                    bg=self.colors['bg_card'],
                                    highlightthickness=0)
            self.canvas.pack(padx=15, pady=10)

            self.summary_label = self._label(self, "", font=('Segoe UI', 10))
            self.summary_label.pack(padx=15, anchor='w')

            # --- Alertes ---
            alert_frame = tk.LabelFrame(self, text=" 🔔 Alertes de seuil ",
                                        bg=self.colors['bg_dark'],
                                        fg=self.colors['text'])
            alert_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

            row = tk.Frame(alert_frame, bg=self.colors['bg_dark'])
            row.pack(fill=tk.X, padx=10, pady=8)

            self._label(row, "Seuil (€):").pack(side=tk.LEFT)
            self.threshold_var = tk.StringVar()
            tk.Entry(row, textvariable=self.threshold_var, width=8,
                     bg='#FFFFFF', fg='#1a1a1a').pack(side=tk.LEFT, padx=5)

            self.direction_var = tk.StringVar(value="above")
            ttk.Combobox(row, textvariable=self.direction_var, width=8,
                         state="readonly",
                         values=["above", "below"]).pack(side=tk.LEFT, padx=5)

            ttk.Button(row, text="➕ Set Alert",
                       command=self._set_alert).pack(side=tk.LEFT, padx=5)
            ttk.Button(row, text="➖ Remove",
                       command=self._remove_alert).pack(side=tk.LEFT, padx=5)
            ttk.Button(row, text="🔔 Check alerts",
                       command=self._check_alerts).pack(side=tk.LEFT, padx=5)

            self.alerts_list = tk.Listbox(alert_frame, height=6,
                                          bg=self.colors['bg_card'],
                                          fg=self.colors['text'],
                                          highlightthickness=0)
            self.alerts_list.pack(fill=tk.BOTH, expand=True, padx=10,
                                  pady=(0, 10))

        # ---------- Données ----------

        def _selected_card_id(self) -> Optional[str]:
            value = self.card_var.get()
            return value.split(" — ")[0].strip() if value else None

        def _reload_cards(self):
            cards = sorted(self.cache.latest_all().keys())
            labels = [f"{cid} — {self._names.get(cid) or '?'}"
                      for cid in cards]
            self.card_combo['values'] = labels
            if labels:
                self.card_combo.current(0)
                self._refresh_chart()
            else:
                self.summary_label.config(
                    text="Cache vide — préchargez d'abord des prix "
                         "(bouton ⬇ Preload Prices de la vue Detection)")

        def _refresh_chart(self):
            card_id = self._selected_card_id()
            if not card_id:
                return
            entries = self.cache.history(card_id, limit=100)
            self.summary_label.config(text=format_history_label(entries))

            self.canvas.delete("all")
            # chronologique gauche -> droite
            values = [e.price for e in reversed(entries)]
            points = sparkline_points(values)
            if len(points) >= 2:
                flat = [coord for point in points for coord in point]
                self.canvas.create_line(*flat, fill=self.colors['accent'],
                                        width=2, smooth=False)
            for x, y in points[-1:]:
                self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3,
                                        fill=self.colors['success'],
                                        outline="")
            priced = [v for v in values if v is not None]
            if priced:
                self.canvas.create_text(
                    8, 10, anchor='w', fill=self.colors['text_dim'],
                    text=f"max {max(priced):.2f}€")
                self.canvas.create_text(
                    8, SPARK_H - 10, anchor='w', fill=self.colors['text_dim'],
                    text=f"min {min(priced):.2f}€")

        # ---------- Alertes ----------

        def _refresh_alerts(self):
            self.alerts_list.delete(0, tk.END)
            for alert in self.cache.list_alerts():
                state = "armée" if alert.armed else "déclenchée"
                name = self._names.get(alert.card_id) or ""
                self.alerts_list.insert(
                    tk.END, f"{alert.describe()}  [{state}]  {name}")

        def _set_alert(self):
            card_id = self._selected_card_id()
            if not card_id:
                messagebox.showwarning("Alerte", "Sélectionnez une carte",
                                       parent=self)
                return
            try:
                threshold = float(self.threshold_var.get().replace(',', '.'))
                self.cache.set_alert(card_id, threshold,
                                     self.direction_var.get())
            except ValueError as e:
                messagebox.showerror("Alerte", f"Seuil invalide: {e}",
                                     parent=self)
                return
            self._refresh_alerts()

        def _remove_alert(self):
            card_id = self._selected_card_id()
            if card_id:
                self.cache.remove_alert(card_id)
                self._refresh_alerts()

        def _check_alerts(self):
            triggered = self.cache.check_alerts()
            self._refresh_alerts()
            if triggered:
                lines = "\n".join(
                    f"• {t.describe()}" for t in self._with_names(triggered))
                messagebox.showinfo("🔔 Alertes déclenchées", lines,
                                    parent=self)
            else:
                messagebox.showinfo("Alertes",
                                    "Aucun seuil franchi sur les derniers "
                                    "relevés.", parent=self)

        def _with_names(self, triggered):
            for t in triggered:
                t.name = self._names.get(t.alert.card_id) or None
            return triggered

else:

    class PriceHistoryDialog:
        """Stub : tkinter absent (headless). Le dialog est indisponible."""
        def __init__(self, *args, **kwargs):
            raise ImportError("tkinter n'est pas disponible sur ce systeme")
