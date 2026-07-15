#!/usr/bin/env python3
"""
Effets d'occlusion réalistes pour les mosaïques (F05)

Objectif : apprendre au modèle à gérer les cartes telles qu'on les voit
vraiment — tenues en main, en éventail, sous sleeve — au lieu de cartes
toujours isolées et entières.

Fournit :
- apply_sleeve()             : effet pochette plastique (voile + reflet spéculaire)
- fan_layout()               : positions/angles d'un éventail de cartes
- compute_visible_fractions(): fraction visible de chaque carte après
                               empilement (pour filtrer les annotations)
- add_fingers()              : doigts procéduraux posés sur le bas d'un éventail
- blend_rgba()               : composition alpha d'un overlay BGRA sur un canvas BGR

Tout est procédural (NumPy/OpenCV), sans asset externe, reproductible via rng.
"""
import random
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

# Fraction visible minimale pour qu'une carte occluse reste annotée
MIN_VISIBLE_FRACTION = 0.25

# Teintes de peau (BGR), du clair au foncé
_SKIN_TONES = [
    (150, 190, 235), (130, 170, 220), (110, 150, 200),
    (90, 120, 170), (60, 85, 125), (45, 65, 95),
]


def blend_rgba(canvas: np.ndarray, overlay: np.ndarray, x: int, y: int) -> np.ndarray:
    """Compose un overlay BGRA sur un canvas BGR, avec clipping aux bords."""
    canvas_h, canvas_w = canvas.shape[:2]
    o_h, o_w = overlay.shape[:2]

    x_start, y_start = max(0, x), max(0, y)
    x_end, y_end = min(canvas_w, x + o_w), min(canvas_h, y + o_h)
    if x_end <= x_start or y_end <= y_start:
        return canvas

    region = overlay[y_start - y:y_end - y, x_start - x:x_end - x]
    roi = canvas[y_start:y_end, x_start:x_end].astype(np.float32)
    rgb = region[:, :, :3].astype(np.float32)
    alpha = region[:, :, 3:4].astype(np.float32) / 255.0
    canvas[y_start:y_end, x_start:x_end] = (rgb * alpha + roi * (1 - alpha)).astype(np.uint8)
    return canvas


def apply_sleeve(card: np.ndarray,
                 rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Simule une carte sous sleeve/toploader : léger voile laiteux, bande de
    reflet spéculaire diagonale (sleeve brillante) ou voile mat, liseré de
    bord. Ne change pas les dimensions : les annotations restent valides.
    Retourne une image BGRA.
    """
    if rng is None:
        rng = np.random.default_rng()

    if card.shape[2] == 3:
        out = cv2.cvtColor(card, cv2.COLOR_BGR2BGRA)
    else:
        out = card.copy()

    h, w = out.shape[:2]
    rgb = out[:, :, :3].astype(np.float32)

    # Voile laiteux du plastique
    veil = rng.uniform(0.04, 0.12)
    rgb = rgb * (1 - veil) + 255.0 * veil

    glossy = rng.random() < 0.6
    if glossy:
        # Bande spéculaire diagonale (reflet de lumière sur le plastique)
        band = np.zeros((h, w), np.float32)
        x0 = int(w * rng.uniform(-0.2, 0.7))
        width = int(w * rng.uniform(0.12, 0.30))
        slant = int(w * rng.uniform(0.2, 0.6)) * (1 if rng.random() < 0.5 else -1)
        pts = np.array([
            [x0, 0], [x0 + width, 0],
            [x0 + width + slant, h], [x0 + slant, h],
        ], np.int32)
        cv2.fillConvexPoly(band, pts, float(rng.uniform(35, 80)))
        k = (max(3, int(w * 0.08)) | 1)
        band = cv2.GaussianBlur(band, (k, k), 0)
        rgb += band[:, :, None]
    else:
        # Sleeve mate : légère perte de contraste
        rgb = rgb * 0.94 + rgb.mean() * 0.06

    # Liseré du bord de la sleeve
    cv2.rectangle(rgb, (1, 1), (w - 2, h - 2), (255.0, 255.0, 255.0), 2)
    edge = rgb.copy()
    rgb = rgb * 0.92 + edge * 0.08  # adoucir le liseré

    out[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    return out


def fan_layout(n_cards: int, canvas_w: int, canvas_h: int,
               rng: Optional[np.random.Generator] = None,
               edge_anchor: bool = False
               ) -> List[Tuple[float, float, float]]:
    """
    Calcule un éventail de n cartes comme tenu en main.

    Les centres des cartes sont sur un arc de cercle autour d'un pivot
    (le poignet), chaque carte tournée de son angle sur l'arc.

    Args:
        edge_anchor: éventail TENU DEPUIS LE BORD BAS du canvas — la main
                     entre dans l'image, le bas des cartes peut être coupé
                     (comme une main de joueur au premier plan). Les bboxes
                     clippées et le filtre de visibilité gèrent la découpe.

    Retourne [(angle_deg, center_x, center_y), ...] dans l'ordre
    d'empilement (la dernière carte est au-dessus).
    """
    if rng is None:
        rng = np.random.default_rng()

    radius = rng.uniform(420, 700)
    delta = rng.uniform(9.0, 16.0) * (1 if rng.random() < 0.5 else -1)
    theta0 = rng.uniform(-15.0, 15.0) - delta * (n_cards - 1) / 2.0

    if edge_anchor:
        # Main au bord bas : les centres des cartes sont proches du bord
        # inférieur — le bas des cartes dépasse du canvas (occlusion par
        # le cadre), le haut reste bien visible
        margin_x = int(canvas_w * 0.15)
        anchor_x = rng.uniform(margin_x, canvas_w - margin_x)
        anchor_y = canvas_h * rng.uniform(0.82, 1.02)
    else:
        margin_x, margin_y = int(canvas_w * 0.18), int(canvas_h * 0.28)
        anchor_x = rng.uniform(margin_x, canvas_w - margin_x)
        anchor_y = rng.uniform(margin_y, canvas_h - margin_y)
    pivot_x, pivot_y = anchor_x, anchor_y + radius

    placements = []
    for j in range(n_cards):
        theta = theta0 + j * delta
        rad = np.deg2rad(theta)
        cx = pivot_x + radius * np.sin(rad)
        cy = pivot_y - radius * np.cos(rad)
        placements.append((float(theta), float(cx), float(cy)))
    return placements


def compute_visible_fractions(placements: Sequence[Tuple[np.ndarray, int, int]],
                              canvas_w: int, canvas_h: int,
                              scale: int = 4) -> List[float]:
    """
    Fraction visible de chaque carte après empilement dans l'ordre donné.

    placements : [(alpha_mask uint8 HxW, pos_x, pos_y), ...] — la carte i
    est recouverte par les cartes i+1..n. Le calcul se fait sur un buffer
    d'étiquettes sous-échantillonné (scale) : rapide et suffisant pour
    décider si une annotation doit être conservée. Les pixels hors canvas
    comptent comme non visibles.
    """
    lw, lh = max(1, canvas_w // scale), max(1, canvas_h // scale)
    label = np.full((lh, lw), -1, np.int32)
    totals = []

    for i, (mask, x, y) in enumerate(placements):
        m_h, m_w = mask.shape[:2]
        sw, sh = max(1, m_w // scale), max(1, m_h // scale)
        small = cv2.resize(mask, (sw, sh), interpolation=cv2.INTER_NEAREST) > 127
        totals.append(int(small.sum()))

        sx, sy = int(round(x / scale)), int(round(y / scale))
        x_start, y_start = max(0, sx), max(0, sy)
        x_end, y_end = min(lw, sx + sw), min(lh, sy + sh)
        if x_end <= x_start or y_end <= y_start:
            continue
        region = small[y_start - sy:y_end - sy, x_start - sx:x_end - sx]
        target = label[y_start:y_end, x_start:x_end]
        target[region] = i

    fractions = []
    for i in range(len(placements)):
        visible = int((label == i).sum())
        fractions.append(visible / max(1, totals[i]))
    return fractions


def _make_finger(length: int, width: int, tone: Tuple[int, int, int],
                 rng: np.random.Generator, nail: bool = True) -> np.ndarray:
    """
    Doigt procédural vertical (bout arrondi en haut), image BGRA —
    avec ongle au bout (ellipse plus claire et légèrement rosée).
    """
    h, w = int(length), int(width)
    img = np.zeros((h, w, 4), np.uint8)

    # Forme capsule : cercle au bout + rectangle
    alpha = np.zeros((h, w), np.uint8)
    r = w // 2
    cv2.circle(alpha, (r, r), r - 1, 255, -1)
    cv2.rectangle(alpha, (0, r), (w - 1, h - 1), 255, -1)

    # Couleur avec ombrage latéral (cylindre éclairé)
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)
    shade = 0.78 + 0.30 * np.sqrt(np.clip(1.0 - xx ** 2, 0, 1))
    base = np.array(tone, np.float32) * rng.uniform(0.92, 1.08)
    rgb = np.clip(base[None, None, :] * shade[None, :, None], 0, 255)
    img[:, :, :3] = rgb.astype(np.uint8)

    # Ongle : ellipse claire au bout du doigt (vu de dos de la main)
    if nail and w >= 12:
        nail_color = tuple(int(min(255, c * 1.18 + 20)) for c in tone)
        edge_color = tuple(int(c * 0.88) for c in tone)
        center = (r, int(r * 0.95))
        axes = (max(3, int(w * 0.28)), max(4, int(w * 0.38)))
        cv2.ellipse(img, center, axes, 0, 0, 360, nail_color, -1)
        cv2.ellipse(img, center, axes, 0, 0, 360, edge_color, 1)
        # Lunule discrète à la base de l'ongle
        cv2.ellipse(img, (r, int(r * 1.15)),
                    (max(2, int(w * 0.16)), max(2, int(w * 0.10))),
                    0, 0, 360, tuple(min(255, c + 25) for c in nail_color), -1)

    # Pli de phalange discret
    if h > width * 2:
        y_fold = int(h * rng.uniform(0.45, 0.65))
        cv2.line(img, (2, y_fold), (w - 3, y_fold),
                 tuple(int(c * 0.85) for c in tone), 1)

    # Bords doux
    img[:, :, 3] = cv2.GaussianBlur(alpha, (5, 5), 0)
    return img


def _rotate_bgra(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotation d'une image BGRA avec canvas étendu (aucun rognage)."""
    h, w = image.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    cos_v, sin_v = abs(m[0, 0]), abs(m[0, 1])
    new_w = int(h * sin_v + w * cos_v)
    new_h = int(h * cos_v + w * sin_v)
    m[0, 2] += (new_w - w) / 2
    m[1, 2] += (new_h - h) / 2
    return cv2.warpAffine(image, m, (new_w, new_h), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT,
                          borderValue=(0, 0, 0, 0))


def add_fingers(canvas: np.ndarray, x0: int, y0: int, x1: int, y1: int,
                rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """
    Pose une main procédurale sur le bas de la zone (x0,y0)-(x1,y1) :
    2 à 4 doigts (avec ongles) qui montent depuis le bas, et un POUCE
    plus large posé par-dessus les cartes dans ~70 % des cas — c'est lui
    qu'on voit au premier plan quand on tient un éventail. Occlusion
    photométrique uniquement : les bboxes des cartes ne changent pas.
    """
    if rng is None:
        rng = np.random.default_rng()

    tone = _SKIN_TONES[rng.integers(len(_SKIN_TONES))]
    n_fingers = int(rng.integers(2, 5))
    zone_w = max(1, x1 - x0)
    finger_w = int(np.clip(zone_w * 0.07, 22, 60))
    base_x = int(rng.uniform(x0 + zone_w * 0.2, x0 + zone_w * 0.6))
    base_y = y1  # les doigts montent depuis le bas de la zone

    for k in range(n_fingers):
        length = int(finger_w * rng.uniform(2.6, 4.2))
        # L'ongle des doigts n'est visible que paume vers soi (~50 %)
        finger = _make_finger(length, finger_w, tone, rng,
                              nail=bool(rng.random() < 0.5))
        finger = _rotate_bgra(finger, float(rng.uniform(-18, 18)))

        fx = base_x + int(k * finger_w * rng.uniform(1.05, 1.35))
        fy = base_y - int(finger.shape[0] * rng.uniform(0.55, 0.85))
        canvas = blend_rgba(canvas, finger, fx, fy)

    # Pouce au premier plan : plus large et plus court, incliné vers
    # l'intérieur de l'éventail, ongle toujours visible
    if rng.random() < 0.7:
        thumb_w = int(finger_w * rng.uniform(1.35, 1.6))
        thumb_len = int(thumb_w * rng.uniform(1.9, 2.6))
        thumb = _make_finger(thumb_len, thumb_w, tone, rng, nail=True)
        lean = float(rng.uniform(25, 55)) * (1 if rng.random() < 0.5 else -1)
        thumb = _rotate_bgra(thumb, lean)

        tx = base_x + int(zone_w * rng.uniform(0.05, 0.25))
        ty = base_y - int(thumb.shape[0] * rng.uniform(0.75, 0.95))
        canvas = blend_rgba(canvas, thumb, tx, ty)

    return canvas


def split_into_fans(group: list, rng_random: Optional[random.Random] = None) -> List[list]:
    """Découpe un groupe de cartes en éventails de 3 à 5 cartes."""
    rand = rng_random or random
    fans, remaining = [], list(group)
    while remaining:
        k = min(len(remaining), rand.randint(3, 5))
        fans.append(remaining[:k])
        remaining = remaining[k:]
    return fans
