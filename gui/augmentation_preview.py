#!/usr/bin/env python3
"""
Fenêtre de prévisualisation live des augmentations (F06).

Applique le pipeline Albumentations à une carte échantillon EN DIRECT
(aucun sous-processus, aucune écriture disque) : on règle l'intensité,
le nombre de transformations et les catégories, la grille d'aperçus se
rafraîchit avec un debounce. Permet de calibrer visuellement les
paramètres avant de lancer une vraie génération.

Sans dépendance Pillow : les aperçus passent par cv2.imencode(PNG) +
tk.PhotoImage(data=base64), supporté par Tk 8.6+.
"""
import base64
import os
import queue
import random
import threading
from glob import glob
from typing import Dict, List, Optional

import cv2
import numpy as np

# tkinter optionnel : les helpers purs (image_to_photo_data,
# pick_sample_image) restent utilisables/testables sans display ni Tk
try:
    import tkinter as tk
    from tkinter import filedialog, ttk
except ImportError:  # environnement headless sans python3-tk
    tk = None

from gui.theme import COLORS

DEBOUNCE_MS = 350          # délai après le dernier changement de slider
PREVIEW_COUNT = 6          # grille 3x2
THUMB_W, THUMB_H = 210, 285

# Libellés affichés pour les catégories du pool
CATEGORY_LABELS = {
    "brightness": "💡 Luminosité",
    "color": "🎨 Couleurs",
    "blur": "🌫️ Flou / Netteté",
    "noise": "📶 Bruit",
    "environment": "🌤️ Environnement",
    "geometry": "📐 Géométrie",
}


def image_to_photo_data(img_bgr: np.ndarray, width: int = THUMB_W,
                        height: int = THUMB_H) -> str:
    """
    Convertit une image BGR en données base64 PNG pour tk.PhotoImage.
    Pur (sans Tk) — testable sans display.
    """
    thumb = cv2.resize(img_bgr, (width, height), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".png", thumb)
    if not ok:
        raise ValueError("Échec d'encodage PNG de l'aperçu")
    return base64.b64encode(buf.tobytes()).decode("ascii")


def pick_sample_image(images_dir: str,
                      rng: Optional[random.Random] = None) -> Optional[str]:
    """Choisit une image de carte au hasard dans le dossier (None si vide)."""
    paths = sorted(glob(os.path.join(images_dir, "*.png"))
                   + glob(os.path.join(images_dir, "*.jpg")))
    if not paths:
        return None
    return (rng or random).choice(paths)


if tk is not None:

    class AugmentationPreviewDialog(tk.Toplevel):
        """Fenêtre modale de prévisualisation live des augmentations."""

        def __init__(self, parent, colors: Optional[Dict] = None,
                     images_dir: Optional[str] = None):
            super().__init__(parent)
            self.colors = colors or COLORS
            self.title("👁 Augmentation Preview")
            # panneau 260px + 4 colonnes d'aperçus (210px + marges)
            self.geometry("1240x720")
            self.configure(bg=self.colors['bg_dark'])
            self.transient(parent)

            if images_dir is None:
                try:
                    from core.utils import PATHS
                    images_dir = PATHS['directories']['images']
                except Exception:
                    images_dir = "images"
            self.images_dir = images_dir

            self._image: Optional[np.ndarray] = None
            self._image_path: Optional[str] = None
            self._photos: List[tk.PhotoImage] = []   # refs anti garbage-collector
            self._debounce_job: Optional[str] = None
            self._generation = 0                     # invalide les rendus obsolètes
            # Règle v3.6 : AUCUN appel Tk depuis un thread worker (même pas
            # after) — les résultats passent par une file pollée par le
            # thread principal
            self._results: "queue.Queue" = queue.Queue()

            # Paramètres réglables
            self.intensity_var = tk.DoubleVar(value=1.0)
            self.n_transforms_var = tk.IntVar(value=0)   # 0 = aléatoire 3-6
            self.category_vars = {
                key: tk.BooleanVar(value=True) for key in CATEGORY_LABELS
            }

            self._build_ui()
            self.after(100, self._poll_results)

            path = pick_sample_image(self.images_dir)
            if path:
                self._load_image(path)
                self.refresh()
            else:
                self.status_var.set(
                    f"⚠️ Aucune image dans '{self.images_dir}' — utilisez 📂 Choose")

        # ------------------------------------------------------------------ UI

        def _build_ui(self):
            c = self.colors

            # Panneau de contrôle (gauche)
            panel = tk.Frame(self, bg=c['bg_card'], width=260)
            panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
            panel.pack_propagate(False)

            tk.Label(panel, text="⚙️ Paramètres", bg=c['bg_card'], fg=c['text'],
                     font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=15, pady=(15, 10))

            # Intensité
            tk.Label(panel, text="Intensité globale", bg=c['bg_card'],
                     fg=c['text'], font=('Segoe UI', 10)).pack(anchor='w', padx=15)
            self.intensity_label = tk.Label(panel, text="1.00×", bg=c['bg_card'],
                                            fg=c['accent'], font=('Segoe UI', 10, 'bold'))
            self.intensity_label.pack(anchor='w', padx=15)
            tk.Scale(panel, from_=0.1, to=2.0, resolution=0.05,
                     orient=tk.HORIZONTAL, variable=self.intensity_var,
                     command=self._on_param_change, bg=c['bg_card'],
                     fg=c['text'], highlightthickness=0,
                     troughcolor=c['bg_dark']).pack(fill=tk.X, padx=15, pady=(0, 10))

            # Nombre de transformations
            tk.Label(panel, text="Transformations par image\n(0 = aléatoire 3-6)",
                     bg=c['bg_card'], fg=c['text'], justify='left',
                     font=('Segoe UI', 10)).pack(anchor='w', padx=15)
            tk.Scale(panel, from_=0, to=8, orient=tk.HORIZONTAL,
                     variable=self.n_transforms_var,
                     command=self._on_param_change, bg=c['bg_card'],
                     fg=c['text'], highlightthickness=0,
                     troughcolor=c['bg_dark']).pack(fill=tk.X, padx=15, pady=(0, 10))

            # Catégories
            tk.Label(panel, text="Catégories", bg=c['bg_card'], fg=c['text'],
                     font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=15, pady=(5, 2))
            for key, label in CATEGORY_LABELS.items():
                tk.Checkbutton(panel, text=label, variable=self.category_vars[key],
                               command=lambda: self._on_param_change(None),
                               bg=c['bg_card'], fg=c['text'],
                               selectcolor=c['bg_dark'],
                               activebackground=c['bg_card'],
                               font=('Segoe UI', 9)).pack(anchor='w', padx=20)

            # Boutons
            btns = tk.Frame(panel, bg=c['bg_card'])
            btns.pack(fill=tk.X, padx=15, pady=15)
            ttk.Button(btns, text="🔄 Regenerate",
                       command=self.refresh).pack(fill=tk.X, pady=2)
            ttk.Button(btns, text="📂 Choose image...",
                       command=self._choose_image).pack(fill=tk.X, pady=2)
            ttk.Button(btns, text="🎲 Random card",
                       command=self._random_image).pack(fill=tk.X, pady=2)

            self.status_var = tk.StringVar(value="")
            tk.Label(panel, textvariable=self.status_var, bg=c['bg_card'],
                     fg=c['text_dim'], font=('Segoe UI', 9),
                     wraplength=220, justify='left').pack(anchor='w', padx=15)

            # Grille d'aperçus (droite) : original + 6 variantes
            self.grid_frame = tk.Frame(self, bg=c['bg_dark'])
            self.grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                 padx=(5, 10), pady=10)
            self.cells = []
            for idx in range(PREVIEW_COUNT + 1):
                row, col = divmod(idx, 4)
                cell = tk.Frame(self.grid_frame, bg=c['bg_card'])
                cell.grid(row=row, column=col, padx=6, pady=6, sticky='n')
                title = "Original" if idx == 0 else f"Variante {idx}"
                tk.Label(cell, text=title, bg=c['bg_card'], fg=c['text_dim'],
                         font=('Segoe UI', 9)).pack(pady=(4, 0))
                img_label = tk.Label(cell, bg=c['bg_card'])
                img_label.pack(padx=6, pady=6)
                self.cells.append(img_label)

        # ------------------------------------------------------------ Actions

        def _load_image(self, path: str):
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                self.status_var.set(f"⚠️ Image illisible: {os.path.basename(path)}")
                return
            self._image = img
            self._image_path = path
            self.status_var.set(f"🃏 {os.path.basename(path)}")

        def _choose_image(self):
            path = filedialog.askopenfilename(
                parent=self, initialdir=self.images_dir,
                filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if path:
                self._load_image(path)
                self.refresh()

        def _random_image(self):
            path = pick_sample_image(self.images_dir)
            if path:
                self._load_image(path)
                self.refresh()

        def _on_param_change(self, _value):
            """Debounce : replanifie le rafraîchissement à chaque changement."""
            self.intensity_label.config(text=f"{self.intensity_var.get():.2f}×")
            if self._debounce_job is not None:
                self.after_cancel(self._debounce_job)
            self._debounce_job = self.after(DEBOUNCE_MS, self.refresh)

        def get_params(self) -> Dict:
            """Paramètres courants (réutilisables par la config de génération)."""
            categories = [k for k, v in self.category_vars.items() if v.get()]
            n = self.n_transforms_var.get()
            return {
                "intensity": round(self.intensity_var.get(), 2),
                "n_transforms": n if n > 0 else None,
                "categories": categories if categories else None,
            }

        def refresh(self):
            """Régénère les aperçus dans un thread (l'UI reste fluide)."""
            self._debounce_job = None
            if self._image is None:
                return
            params = self.get_params()
            if params["categories"] is None and not any(
                    v.get() for v in self.category_vars.values()):
                self.status_var.set("⚠️ Sélectionnez au moins une catégorie")
                return

            self._generation += 1
            generation = self._generation
            image = self._image.copy()
            self.status_var.set("⏳ Génération…")

            def worker():
                try:
                    from core.augmentation_albumentations import preview_augmentations
                    variants = preview_augmentations(
                        image, count=PREVIEW_COUNT,
                        n_transforms=params["n_transforms"],
                        intensity=params["intensity"],
                        categories=params["categories"])
                    datas = [image_to_photo_data(image)]
                    datas += [image_to_photo_data(v) for v in variants]
                    error = None
                except Exception as exc:      # surface l'erreur dans la fenêtre
                    datas, error = None, str(exc)
                self._results.put((generation, datas, error))

            threading.Thread(target=worker, daemon=True).start()

        def _poll_results(self):
            """Applique les rendus terminés (thread principal uniquement)."""
            try:
                while True:
                    generation, datas, error = self._results.get_nowait()
                    self._apply_previews(generation, datas, error)
            except queue.Empty:
                pass
            try:
                if self.winfo_exists():
                    self.after(100, self._poll_results)
            except tk.TclError:
                pass  # fenêtre détruite

        def _apply_previews(self, generation: int, datas, error):
            if generation != self._generation:
                return  # un rendu plus récent est déjà en route
            if error is not None:
                self.status_var.set(f"❌ {error}")
                return
            self._photos = [tk.PhotoImage(data=d) for d in datas]
            for label, photo in zip(self.cells, self._photos):
                label.config(image=photo)
            name = os.path.basename(self._image_path or "")
            self.status_var.set(f"🃏 {name}\n✅ {PREVIEW_COUNT} variantes")

else:  # pragma: no cover - environnement sans tkinter
    class AugmentationPreviewDialog:
        """Stub : tkinter absent (headless). Le dialog est indisponible."""
        def __init__(self, *args, **kwargs):
            raise ImportError("tkinter n'est pas disponible sur ce systeme")
