#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
card_grader.py — F02 : estimation de l'état de la carte (grading)
=================================================================

Estime l'état d'une carte depuis son crop webcam (bbox YOLO) et pondère le
prix affiché (Near Mint vs Played).

Métriques retenues (réalistes avec une webcam — cf. fiche F02) :
- **Centrage** : largeur des 4 bordures mesurée par les profils de
  gradients (l'arête du cadre intérieur est l'edge dominant dans la bande
  de bordure). Ratios gauche/(gauche+droite) et haut/(haut+bas) —
  50/50 = parfait.
- **Coins** : heuristique de blanchiment — un coin abîmé (fibres du carton
  exposées) est nettement plus clair que la bordure ; on mesure la
  proportion de pixels anormalement clairs dans chaque coin par rapport à
  la luminance médiane de la bordure.
- **Rayures de surface** : hors périmètre v1 (résolution webcam
  insuffisante pour être fiable — décision de design, cf. journal).

L'estimation est **best effort** : `grade()` ne lève jamais, renvoie None
si le crop est inexploitable, et la détection continue sans grading.

Usage :
    >>> grader = CardGrader()
    >>> result = grader.grade(crop_bgr)
    >>> result.label, result.price_factor, result.centering_lr
    ('NM', 1.0, 0.52)
"""
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np

# Résolution d'analyse (ratio carte ~600:825)
_W, _H = 240, 330

# Bande de recherche du cadre intérieur : de 2 % à 22 % du bord
_BAND_MIN, _BAND_MAX = 0.02, 0.22

# Coins : taille du patch analysé et rayon de l'arrondi masqué
# (fractions du petit côté) — les coins d'un crop serré contiennent du FOND
# au-delà de l'arrondi de la carte, qu'il ne faut pas compter comme dégât
_CORNER_FRACTION = 0.12
_CORNER_RADIUS_FRACTION = 0.08
# Blanchiment (fibres exposées) : pixel « abîmé » = très clair ET désaturé.
# Signature universelle d'un coin abîmé, quelle que soit la couleur de la
# bordure (jaune, argent, noire) — indéterminé sur bordure blanche.
_WHITE_L_MIN = 210.0          # luminance Lab (échelle cv2, 0-255)
_WHITE_CHROMA_MAX = 25.0      # distance à (a=128, b=128)

# Barème : (score minimal, label, facteur de prix)
CONDITION_SCALE = [
    (0.85, "NM", 1.00),   # Near Mint
    (0.70, "EX", 0.85),   # Excellent
    (0.55, "GD", 0.70),   # Good
    (0.00, "PL", 0.50),   # Played
]


@dataclass
class GradeResult:
    """Résultat de l'estimation d'état d'une carte."""
    centering_lr: float          # gauche/(gauche+droite), 0.5 = parfait
    centering_tb: float          # haut/(haut+bas), 0.5 = parfait
    centering_score: float       # [0, 1], 1 = parfaitement centré
    corners_score: float         # [0, 1], 1 = coins intacts
    score: float                 # score global [0, 1]
    label: str                   # NM / EX / GD / PL
    price_factor: float          # pondération du prix affiché

    @property
    def centering_text(self) -> str:
        """Centrage au format habituel des gradeurs : « 55/45 » (G/D)."""
        left = round(self.centering_lr * 100)
        return f"{left}/{100 - left}"


def condition_from_score(score: float) -> Tuple[str, float]:
    """Label et facteur de prix pour un score global [0, 1]."""
    for threshold, label, factor in CONDITION_SCALE:
        if score >= threshold:
            return label, factor
    return CONDITION_SCALE[-1][1], CONDITION_SCALE[-1][2]


class CardGrader:
    """
    Estimateur d'état best effort sur crop BGR.

    Args:
        centering_weight: poids du centrage dans le score global
                          (le reste va aux coins)
    """

    def __init__(self, centering_weight: float = 0.6):
        if not 0 <= centering_weight <= 1:
            raise ValueError("centering_weight doit être dans [0, 1]")
        self.centering_weight = centering_weight

    # ---------- API ----------

    def grade(self, crop_bgr: np.ndarray) -> Optional[GradeResult]:
        """
        Estime l'état d'une carte. Ne lève JAMAIS (best effort).

        Args:
            crop_bgr: crop BGR de la carte (bbox YOLO, cadrage serré)

        Returns:
            GradeResult, ou None si le crop est inexploitable.
        """
        try:
            if crop_bgr is None or crop_bgr.size == 0 \
                    or min(crop_bgr.shape[:2]) < 48:
                return None
            img = cv2.resize(crop_bgr, (_W, _H),
                             interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)

            borders = self._measure_borders(gray)
            if borders is None:
                return None
            left, right, top, bottom = borders

            centering_lr = left / max(1e-6, left + right)
            centering_tb = top / max(1e-6, top + bottom)
            deviation = 2.0 * max(abs(centering_lr - 0.5),
                                  abs(centering_tb - 0.5))
            centering_score = float(np.clip(1.0 - deviation, 0.0, 1.0))

            lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab).astype(np.float32)
            corners_score = self._corners_score(lab, borders)

            score = (self.centering_weight * centering_score
                     + (1.0 - self.centering_weight) * corners_score)
            label, factor = condition_from_score(score)

            return GradeResult(
                centering_lr=float(centering_lr),
                centering_tb=float(centering_tb),
                centering_score=centering_score,
                corners_score=float(corners_score),
                score=float(score),
                label=label,
                price_factor=factor,
            )
        except Exception:
            return None  # best effort : le grading ne casse jamais la détection

    # ---------- Centrage ----------

    @staticmethod
    def _first_edge(profile: np.ndarray, lo: int, hi: int,
                    from_end: bool = False, rel_threshold: float = 0.5) -> Optional[int]:
        """
        Position du PREMIER edge significatif (≥ rel_threshold × max de la
        bande) en scannant depuis l'extérieur de la carte — c'est la
        transition bordure→cadre, avant les edges du texte/artwork.
        Retourne la distance au bord correspondant.
        """
        if hi <= lo:
            return None
        band = profile[lo:hi]
        if band.max() <= 0:
            return None
        significant = np.where(band >= rel_threshold * band.max())[0]
        if len(significant) == 0:
            return None
        idx = lo + int(significant[-1] if from_end else significant[0])
        return (len(profile) - idx) if from_end else idx

    def _measure_borders(self, gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Largeur des 4 bordures (px) : premier edge significatif du profil
        de gradient dans la bande [2 %, 22 %] de chaque bord, en scannant
        depuis l'extérieur. Profils moyennés sur le tiers central (évite
        coins et illustration).
        """
        h, w = gray.shape
        gx = np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3))
        gy = np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3))

        rows = slice(h // 3, 2 * h // 3)
        cols = slice(w // 3, 2 * w // 3)
        profile_x = gx[rows, :].mean(axis=0)     # edges verticaux
        profile_y = gy[:, cols].mean(axis=1)     # edges horizontaux

        x_lo, x_hi = int(_BAND_MIN * w), int(_BAND_MAX * w)
        y_lo, y_hi = int(_BAND_MIN * h), int(_BAND_MAX * h)

        left = self._first_edge(profile_x, x_lo, x_hi)
        right = self._first_edge(profile_x, w - x_hi, w - x_lo,
                                 from_end=True)
        top = self._first_edge(profile_y, y_lo, y_hi)
        bottom = self._first_edge(profile_y, h - y_hi, h - y_lo,
                                  from_end=True)

        if None in (left, right, top, bottom):
            return None
        return left, right, top, bottom

    # ---------- Coins ----------

    @staticmethod
    def _corner_mask(size: int, radius: int, border_x: int,
                     border_y: int) -> np.ndarray:
        """
        Masque booléen (True = pixel analysé) d'un patch de coin
        haut-gauche :
        - exclut la zone au-delà de l'arrondi de la carte (du FOND dans un
          crop serré) ;
        - restreint à la bande de bordure (zone en L) — au-delà commence le
          cadre imprimé, dont la couleur diffère légitimement.
        Les autres coins s'obtiennent par miroir du patch avant application.
        """
        ys, xs = np.mgrid[0:size, 0:size]
        inside_arc = (xs - radius) ** 2 + (ys - radius) ** 2 <= radius ** 2
        on_card = (xs >= radius) | (ys >= radius) | inside_arc
        # Bande de bordure stricte (marge -2 : ne pas mordre sur le cadre
        # imprimé ni sur la transition anti-aliasée)
        bx = max(3, border_x - 2)
        by = max(3, border_y - 2)
        in_border = (xs < bx) | (ys < by)
        return on_card & in_border

    @staticmethod
    def _whitened_fraction(pixels: np.ndarray) -> float:
        """Proportion de pixels « blanchis » : très clairs ET désaturés."""
        L = pixels[:, 0]
        chroma = np.hypot(pixels[:, 1] - 128.0, pixels[:, 2] - 128.0)
        return float(((L > _WHITE_L_MIN) & (chroma < _WHITE_CHROMA_MAX)).mean())

    def _corners_score(self, lab: np.ndarray,
                       borders: Tuple[int, int, int, int]) -> float:
        """
        Score des coins [0, 1] : proportion de pixels blanchis (fibres
        exposées) dans la bande de bordure de chaque coin, arrondi de la
        carte masqué. Indéterminé (neutre) sur bordure déjà blanche.
        """
        h, w = lab.shape[:2]
        left, right, top, bottom = borders

        # Couleur de référence : anneau de bordure (hors coins). Si la
        # bordure est elle-même blanche (vieux sets), le blanchiment est
        # indétectable -> neutre.
        band = max(2, min(left, right, top, bottom))
        ring = np.concatenate([
            lab[:band, w // 4: 3 * w // 4].reshape(-1, 3),      # haut
            lab[-band:, w // 4: 3 * w // 4].reshape(-1, 3),     # bas
            lab[h // 4: 3 * h // 4, :band].reshape(-1, 3),      # gauche
            lab[h // 4: 3 * h // 4, -band:].reshape(-1, 3),     # droite
        ])
        if self._whitened_fraction(ring) > 0.5:
            return 1.0  # bordure blanche : coin indéterminé, ne pas pénaliser

        s = max(12, int(_CORNER_FRACTION * min(h, w)))
        radius = max(4, int(_CORNER_RADIUS_FRACTION * min(h, w)))

        # Patchs réorientés pour que le coin de la carte soit en haut-gauche,
        # avec les largeurs de bordure (horizontale, verticale) de chaque coin
        patches = [
            (lab[:s, :s], left, top),                       # haut-gauche
            (lab[:s, -s:][:, ::-1], right, top),            # haut-droite
            (lab[-s:, :s][::-1, :], left, bottom),          # bas-gauche
            (lab[-s:, -s:][::-1, ::-1], right, bottom),     # bas-droite
        ]

        damages = []
        for patch, border_x, border_y in patches:
            mask = self._corner_mask(s, radius, border_x, border_y)
            pixels = patch[mask]
            if len(pixels) < 20:
                continue  # coin indéterminé : ne pas pénaliser (best effort)
            damages.append(self._whitened_fraction(pixels))
        if not damages:
            return 1.0

        # 30 % de pixels blanchis dans un coin = coin très abîmé
        worst = min(1.0, max(damages) / 0.30)
        mean = min(1.0, (sum(damages) / len(damages)) / 0.30)
        damage = 0.7 * worst + 0.3 * mean
        return float(np.clip(1.0 - damage, 0.0, 1.0))
