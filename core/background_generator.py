#!/usr/bin/env python3
"""
Générateur procédural de fonds réalistes pour les mosaïques (F04)

Produit des surfaces crédibles sur lesquelles poser des cartes :
- wood    : table en bois (planches, veinage, joints)
- playmat : tapis de jeu (tissu saturé, motif imprimé discret, reflet)
- binder  : page de classeur (grille de pochettes plastiques 3x3, reflets)
- fabric  : tissu / feutrine (fibres, taches de teinte)
- desk    : bureau neutre (surface unie, éclairage directionnel)

Fournit aussi :
- add_drop_shadow()     : ombre portée douce sous une carte (masque alpha flouté)
- apply_camera_effects(): rendu "photo" global (température, exposition,
                          éclairage directionnel, vignettage)

Tout est généré en NumPy/OpenCV : aucun téléchargement, aucune dépendance
réseau, aucun problème de licence. Reproductible via seed.
"""
from typing import Optional, Tuple

import cv2
import numpy as np

# Catégories disponibles (ordre stable pour les tests et la galerie)
CATEGORIES = ("wood", "playmat", "binder", "fabric", "desk")


def _smooth_noise(rng: np.random.Generator, height: int, width: int,
                  cells_y: int, cells_x: int) -> np.ndarray:
    """
    Bruit lisse en [0,1] : grille aléatoire basse résolution agrandie en
    bicubique. cells_y/cells_x contrôlent la fréquence (peu de cellules =
    variations larges ; beaucoup = variations fines). Des cellules très
    asymétriques donnent des stries (veinage bois, fibres).
    """
    cells_y = max(2, int(cells_y))
    cells_x = max(2, int(cells_x))
    grid = rng.random((cells_y, cells_x)).astype(np.float32)
    noise = cv2.resize(grid, (width, height), interpolation=cv2.INTER_CUBIC)
    return np.clip(noise, 0.0, 1.0)


class BackgroundGenerator:
    """Générateur de fonds procéduraux, reproductible via seed."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)

    def generate(self, width: int = 1920, height: int = 1080,
                 category: Optional[str] = None) -> np.ndarray:
        """
        Génère un fond BGR uint8 (height, width, 3).
        category=None → catégorie tirée au hasard.
        """
        if category is None:
            category = CATEGORIES[self.rng.integers(len(CATEGORIES))]
        if category not in CATEGORIES:
            raise ValueError(f"Catégorie inconnue: {category!r} (choix: {CATEGORIES})")

        builder = getattr(self, f"_{category}")
        img = builder(width, height)
        return np.clip(img, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # Textures
    # ------------------------------------------------------------------

    def _wood(self, w: int, h: int) -> np.ndarray:
        rng = self.rng
        # Teintes bois (BGR) : du chêne clair au noyer foncé
        palettes = [(60, 95, 140), (45, 75, 115), (80, 120, 165),
                    (35, 55, 90), (95, 140, 185)]
        base = np.array(palettes[rng.integers(len(palettes))], np.float32)
        base *= rng.uniform(0.85, 1.15)
        img = np.ones((h, w, 3), np.float32) * base

        horizontal = rng.random() < 0.5

        # Veinage : bruit fortement étiré le long des planches
        if horizontal:
            grain = _smooth_noise(rng, h, w, h // 10, 7)
        else:
            grain = _smooth_noise(rng, h, w, 7, w // 10)
        img *= (0.82 + 0.36 * grain)[:, :, None]

        # Planches : variation de teinte par planche + joint sombre
        plank_size = int(rng.integers(160, 340))
        length = h if horizontal else w
        n_planks = length // plank_size + 2
        offsets = rng.uniform(-14, 14, n_planks).astype(np.float32)
        coord = np.arange(length)
        plank_idx = coord // plank_size
        per_pixel = offsets[plank_idx]
        seam = (coord % plank_size) < 3
        if horizontal:
            img += per_pixel[:, None, None]
            img[seam, :, :] *= 0.55
        else:
            img += per_pixel[None, :, None]
            img[:, seam, :] *= 0.55

        # Grain fin
        fine = rng.normal(0, 4.0, (h, w, 1)).astype(np.float32)
        img += cv2.GaussianBlur(fine, (3, 3), 0)[:, :, None]
        return img

    def _playmat(self, w: int, h: int) -> np.ndarray:
        rng = self.rng
        # Couleur saturée sombre (vert, bleu, rouge, violet, noir...)
        hue = rng.uniform(0, 180)
        sat = rng.uniform(120, 230)
        val = rng.uniform(35, 110)
        hsv = np.full((1, 1, 3), (hue, sat, val), np.uint8)
        base = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0].astype(np.float32)
        img = np.ones((h, w, 3), np.float32) * base

        # Trame tissu : bruit fin légèrement flouté
        amp = rng.uniform(5, 11)
        fabric = rng.normal(0, amp, (h, w)).astype(np.float32)
        fabric = cv2.GaussianBlur(fabric, (3, 3), 0)
        img += fabric[:, :, None]

        # Tissage : moiré sinusoïdal discret
        period = rng.uniform(3.0, 6.0)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        weave = np.sin(xx / period) * np.sin(yy / period) * rng.uniform(1.5, 3.5)
        img += weave[:, :, None]

        # Motif imprimé discret (cercle ou cadre central, comme un vrai tapis)
        if rng.random() < 0.7:
            overlay = img.copy()
            lighter = rng.random() < 0.5
            delta = 28.0 if lighter else -28.0
            color = tuple(float(c) for c in np.clip(base + delta, 0, 255))
            thickness = int(rng.integers(4, 12))
            if rng.random() < 0.5:
                radius = int(min(w, h) * rng.uniform(0.20, 0.38))
                cv2.circle(overlay, (w // 2, h // 2), radius, color, thickness)
            else:
                mx = int(w * rng.uniform(0.06, 0.16))
                my = int(h * rng.uniform(0.08, 0.20))
                cv2.rectangle(overlay, (mx, my), (w - mx, h - my), color, thickness)
            alpha = rng.uniform(0.10, 0.25)
            img = img * (1 - alpha) + overlay * alpha

        # Léger reflet diagonal (sheen du néoprène)
        sheen = _smooth_noise(rng, h, w, 2, 3)
        img *= (0.96 + 0.08 * sheen)[:, :, None]
        return img

    def _binder(self, w: int, h: int) -> np.ndarray:
        rng = self.rng
        # Page de classeur : sombre le plus souvent, parfois claire
        pages = [(30, 30, 32), (18, 18, 20), (60, 40, 28), (45, 30, 90), (225, 228, 232)]
        base = np.array(pages[rng.integers(len(pages))], np.float32)
        img = np.ones((h, w, 3), np.float32) * base
        img += rng.normal(0, 3.0, (h, w, 1)).astype(np.float32)

        dark_page = base.mean() < 128
        pocket_delta = 14.0 if dark_page else -14.0

        # Grille de pochettes 3x3, ratio carte (~0.72)
        cols, rows = 3, 3
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.04)
        gap = int(min(w, h) * 0.02)
        cell_w = (w - 2 * margin_x - (cols - 1) * gap) // cols
        cell_h = (h - 2 * margin_y - (rows - 1) * gap) // rows
        # Ajuster au ratio carte sans déborder de la cellule
        pocket_w = min(cell_w, int(cell_h * 0.72))
        pocket_h = min(cell_h, int(pocket_w / 0.72))

        sheen_overlay = np.zeros((h, w), np.float32)
        for r in range(rows):
            for c in range(cols):
                x0 = margin_x + c * (cell_w + gap) + (cell_w - pocket_w) // 2
                y0 = margin_y + r * (cell_h + gap) + (cell_h - pocket_h) // 2
                x1, y1 = x0 + pocket_w, y0 + pocket_h
                # Pochette légèrement plus claire/foncée que la page
                img[y0:y1, x0:x1] += pocket_delta
                # Bord de la pochette
                border = tuple(float(v) for v in np.clip(base - 18, 0, 255))
                cv2.rectangle(img, (x0, y0), (x1, y1), border, 2)
                # Bande de reflet plastique diagonale
                band = np.array([
                    [x0 + int(pocket_w * rng.uniform(0.1, 0.3)), y0],
                    [x0 + int(pocket_w * rng.uniform(0.4, 0.6)), y0],
                    [x0 + int(pocket_w * rng.uniform(0.1, 0.3)), y1],
                    [x0, y1],
                    [x0, y0 + int(pocket_h * rng.uniform(0.5, 0.9))],
                ], np.int32)
                cv2.fillConvexPoly(sheen_overlay, band, rng.uniform(10, 26))

        k = int(min(w, h) * 0.02) | 1
        sheen_overlay = cv2.GaussianBlur(sheen_overlay, (k, k), 0)
        img += sheen_overlay[:, :, None]
        return img

    def _fabric(self, w: int, h: int) -> np.ndarray:
        rng = self.rng
        # Feutrine / nappe : teinte moyenne peu saturée
        hue = rng.uniform(0, 180)
        sat = rng.uniform(20, 110)
        val = rng.uniform(60, 160)
        hsv = np.full((1, 1, 3), (hue, sat, val), np.uint8)
        base = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0].astype(np.float32)
        img = np.ones((h, w, 3), np.float32) * base

        # Fibres : bruit fin étiré dans une direction
        amp = rng.uniform(7, 14)
        fibers = rng.normal(0, amp, (h, w)).astype(np.float32)
        ksize = (1, 15) if rng.random() < 0.5 else (15, 1)
        fibers = cv2.blur(fibers, ksize)
        img += fibers[:, :, None] * 2.5

        # Taches de teinte larges (usure, éclairage)
        blotch = _smooth_noise(rng, h, w, 5, 8)
        img *= (0.90 + 0.20 * blotch)[:, :, None]
        return img

    def _desk(self, w: int, h: int) -> np.ndarray:
        rng = self.rng
        # Surfaces neutres : gris, beige, blanc cassé, anthracite
        neutrals = [(200, 200, 200), (150, 170, 190), (235, 238, 240),
                    (70, 70, 74), (120, 130, 140)]
        base = np.array(neutrals[rng.integers(len(neutrals))], np.float32)
        base *= rng.uniform(0.9, 1.1)
        img = np.ones((h, w, 3), np.float32) * base

        # Éclairage directionnel large (fenêtre / lampe de bureau)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        angle = rng.uniform(0, 2 * np.pi)
        ramp = (xx / w) * np.cos(angle) + (yy / h) * np.sin(angle)
        ramp = (ramp - ramp.min()) / max(1e-6, ramp.max() - ramp.min())
        img *= (0.88 + 0.24 * ramp)[:, :, None]

        # Micro-texture et traces discrètes
        img += rng.normal(0, 2.0, (h, w, 1)).astype(np.float32)
        smudge = _smooth_noise(rng, h, w, 4, 7)
        img += ((smudge - 0.5) * 8.0)[:, :, None]
        return img


def add_drop_shadow(canvas: np.ndarray, overlay: np.ndarray, x: int, y: int,
                    offset: Tuple[int, int] = (8, 12), blur: int = 21,
                    strength: float = 0.45) -> np.ndarray:
    """
    Assombrit le fond sous une carte pour simuler une ombre portée douce.

    À appeler AVANT overlay_on_canvas_vectorized avec les mêmes (x, y).
    L'ombre est le masque alpha de la carte, flouté, décalé de `offset`
    (dx, dy), appliqué en multiplicatif (strength = opacité max de l'ombre).
    Ne modifie jamais la géométrie : les annotations restent valides.
    """
    if overlay.shape[2] == 4:
        mask = overlay[:, :, 3].astype(np.float32) / 255.0
    else:
        mask = np.ones(overlay.shape[:2], np.float32)

    blur = max(3, int(blur)) | 1  # kernel impair obligatoire
    mask = cv2.GaussianBlur(mask, (blur, blur), 0)

    sx, sy = x + int(offset[0]), y + int(offset[1])
    canvas_h, canvas_w = canvas.shape[:2]
    mask_h, mask_w = mask.shape[:2]

    x_start, y_start = max(0, sx), max(0, sy)
    x_end, y_end = min(canvas_w, sx + mask_w), min(canvas_h, sy + mask_h)
    if x_end <= x_start or y_end <= y_start:
        return canvas

    m = mask[y_start - sy:y_end - sy, x_start - sx:x_end - sx]
    roi = canvas[y_start:y_end, x_start:x_end].astype(np.float32)
    roi *= (1.0 - float(strength) * m)[:, :, None]
    canvas[y_start:y_end, x_start:x_end] = roi.astype(np.uint8)
    return canvas


def apply_camera_effects(img: np.ndarray,
                         rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Effets "photo" globaux sur l'image composée finale :
    température de couleur, exposition, éclairage directionnel, vignettage.
    Purement photométrique : les annotations restent valides.
    """
    if rng is None:
        rng = np.random.default_rng()

    out = img.astype(np.float32)
    h, w = out.shape[:2]

    # Température de couleur (chaud/froid) — canaux B et R en opposition
    t = rng.uniform(-0.07, 0.07)
    out[:, :, 0] *= (1.0 + t)
    out[:, :, 2] *= (1.0 - t)

    # Exposition globale
    out *= rng.uniform(0.92, 1.08)

    # Éclairage directionnel léger
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    angle = rng.uniform(0, 2 * np.pi)
    ramp = (xx / w) * np.cos(angle) + (yy / h) * np.sin(angle)
    ramp = (ramp - ramp.min()) / max(1e-6, ramp.max() - ramp.min())
    g = rng.uniform(0.0, 0.08)
    out *= (1.0 - g + 2 * g * ramp)[:, :, None]

    # Vignettage
    strength = rng.uniform(0.05, 0.28)
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    d2 = ((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2
    vignette = 1.0 - strength * (d2 / 2.0)
    out *= vignette[:, :, None]

    return np.clip(out, 0, 255).astype(np.uint8)


def generate_realistic_background(width: int = 1920, height: int = 1080,
                                  category: Optional[str] = None,
                                  seed: Optional[int] = None) -> np.ndarray:
    """Raccourci : un fond réaliste BGR uint8 en un appel."""
    return BackgroundGenerator(seed=seed).generate(width, height, category)
