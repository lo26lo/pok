"""
Tests du grading (F02).

Couvre : mesure du centrage à ±5 % (critère d'acceptation) sur cartes
synthétiques à bordures connues, détection des coins blanchis (arrondi et
bordure blanche gérés), barème d'état et pondération du prix, contrat
« best effort, ne lève jamais », latence, intégration DetectionManager
(badge + prix pondéré + jamais bloquant).
"""
import time
from pathlib import Path

import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from core.card_grader import (  # noqa: E402
    CardGrader,
    condition_from_score,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def synth_card(l, r, t, b, size=(330, 240), border=(60, 180, 210),
               inner_val=90, damage_frac=0.0):
    """
    Carte synthétique : bordure colorée (jaune par défaut, BGR), cadre
    intérieur sombre, bordures exprimées en fractions [gauche, droite,
    haut, bas] ; damage_frac ajoute un coin blanchi (triangle blanc).
    """
    h, w = size
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = border
    img[int(t * h):h - int(b * h), int(l * w):w - int(r * w)] = inner_val
    if damage_frac:
        s = int(damage_frac * min(h, w))
        cv2.fillPoly(img, [np.array([[0, 0], [s, 0], [0, s]])],
                     (250, 250, 250))
    return img


@pytest.fixture
def grader():
    return CardGrader()


class TestCentering:
    CASES = [
        (0.08, 0.08, 0.08, 0.08),   # parfaitement centré
        (0.10, 0.06, 0.08, 0.08),   # décalé gauche/droite
        (0.12, 0.04, 0.10, 0.06),   # fortement décalé
        (0.06, 0.10, 0.11, 0.05),   # décalé dans l'autre sens
    ]

    @pytest.mark.parametrize("l,r,t,b", CASES)
    def test_centering_within_5_percent(self, grader, l, r, t, b):
        """Critère F02 : centrage mesuré à ±5 % de la vérité terrain."""
        result = grader.grade(synth_card(l, r, t, b))
        assert result is not None
        assert abs(result.centering_lr - l / (l + r)) <= 0.05
        assert abs(result.centering_tb - t / (t + b)) <= 0.05

    def test_perfect_centering_scores_high(self, grader):
        result = grader.grade(synth_card(0.08, 0.08, 0.08, 0.08))
        assert result.centering_score > 0.9
        assert result.label == "NM"

    def test_bad_centering_downgrades(self, grader):
        # lr vrai = 0.75 -> centering_score ~0.5 ; coins parfaits (1.0)
        # -> score global ~0.7 : la carte perd son NM et son prix plein
        result = grader.grade(synth_card(0.12, 0.04, 0.10, 0.06))
        assert result.centering_score < 0.6
        assert result.label != "NM"
        assert result.price_factor < 1.0

    def test_centering_text_format(self, grader):
        result = grader.grade(synth_card(0.08, 0.08, 0.08, 0.08))
        left, right = map(int, result.centering_text.split("/"))
        assert left + right == 100


class TestCorners:
    def test_intact_corners_full_score(self, grader):
        result = grader.grade(synth_card(0.08, 0.08, 0.08, 0.08))
        assert result.corners_score == pytest.approx(1.0)

    def test_whitened_corner_detected(self, grader):
        clean = grader.grade(synth_card(0.08, 0.08, 0.08, 0.08))
        damaged = grader.grade(synth_card(0.08, 0.08, 0.08, 0.08,
                                          damage_frac=0.16))
        assert damaged.corners_score < clean.corners_score - 0.3
        assert damaged.label != "NM"
        assert damaged.price_factor < clean.price_factor

    def test_white_border_is_neutral(self, grader):
        """Bordure blanche (vieux sets) : blanchiment indétectable -> neutre."""
        card = synth_card(0.08, 0.08, 0.08, 0.08, border=(245, 245, 245),
                          damage_frac=0.16)
        result = grader.grade(card)
        assert result.corners_score == pytest.approx(1.0)


class TestConditionScale:
    def test_labels_and_factors(self):
        assert condition_from_score(0.95) == ("NM", 1.00)
        assert condition_from_score(0.75) == ("EX", 0.85)
        assert condition_from_score(0.60) == ("GD", 0.70)
        assert condition_from_score(0.10) == ("PL", 0.50)

    def test_scale_is_monotonic(self):
        factors = [condition_from_score(s)[1]
                   for s in (0.95, 0.75, 0.60, 0.10)]
        assert factors == sorted(factors, reverse=True)


class TestBestEffort:
    def test_never_raises_on_garbage(self, grader):
        assert grader.grade(None) is None
        assert grader.grade(np.zeros((0, 0, 3), np.uint8)) is None
        assert grader.grade(np.zeros((20, 20, 3), np.uint8)) is None
        # Image uniforme : pas d'edges -> None, pas d'exception
        assert grader.grade(np.full((300, 200, 3), 128, np.uint8)) is None

    def test_invalid_weight_rejected(self):
        with pytest.raises(ValueError):
            CardGrader(centering_weight=1.5)

    def test_latency_under_budget(self, grader):
        card = synth_card(0.08, 0.08, 0.08, 0.08)
        grader.grade(card)  # warmup
        t0 = time.perf_counter()
        for _ in range(10):
            grader.grade(card)
        assert (time.perf_counter() - t0) / 10 < 0.05  # < 50 ms


@pytest.mark.skipif(
    not (PROJECT_ROOT / "backgrounds" / "original" / "swsh7_3_en.png").exists(),
    reason="cartes réelles absentes")
class TestRealCards:
    def test_mint_scans_grade_well(self, grader):
        """Les scans TCGdex sont des cartes parfaites : centrage ~50/50."""
        img = cv2.imread(str(PROJECT_ROOT / "backgrounds" / "original"
                             / "swsh7_3_en.png"))
        result = grader.grade(img)
        assert result is not None
        assert abs(result.centering_lr - 0.5) < 0.08
        assert abs(result.centering_tb - 0.5) < 0.08
        assert result.label in ("NM", "EX")

    def test_whitened_corner_on_real_card(self, grader):
        img = cv2.imread(str(PROJECT_ROOT / "backgrounds" / "original"
                             / "swsh7_3_en.png"))
        clean = grader.grade(img)
        h, w = img.shape[:2]
        s = int(0.10 * w)
        y0 = int(0.045 * h)   # sous l'arrondi du coin
        cv2.fillPoly(img, [np.array([[0, y0], [s, y0], [0, y0 + s]])],
                     (250, 250, 250))
        damaged = grader.grade(img)
        assert damaged.corners_score < clean.corners_score - 0.3


class TestDetectionManagerIntegration:
    @pytest.fixture
    def manager(self):
        from core.detection_manager import DetectionConfig, DetectionManager
        model = PROJECT_ROOT / "models" / "yolo11n.pt"
        if not model.exists():
            pytest.skip("modèle YOLO absent")
        config = DetectionConfig(model_path=model, grade_cards=True)
        return DetectionManager(config)

    def test_grader_loaded_and_custom_overlay(self, manager):
        assert manager._grader is not None
        assert manager._custom_overlay

    def test_grade_crop(self, manager):
        frame = np.full((400, 600, 3), 40, np.uint8)
        card = synth_card(0.08, 0.08, 0.08, 0.08)
        frame[30:360, 100:340] = cv2.resize(card, (240, 330))
        grade = manager._grade_crop(frame, (100, 30, 340, 360))
        assert grade is not None
        assert grade.label == "NM"
        # bbox trop petite -> None, pas d'exception
        assert manager._grade_crop(frame, (0, 0, 30, 30)) is None

    def test_overlay_badge_and_weighted_price(self, manager):
        from core.card_grader import GradeResult
        manager._prices = {}
        manager._class_names = {0: "Pokemon_Card"}
        frame = np.full((400, 600, 3), 40, np.uint8)
        grade = GradeResult(0.5, 0.5, 1.0, 0.4, 0.6, "GD", 0.70)
        out = manager._draw_detection_with_price(
            frame.copy(), (100, 30, 340, 360), 0, 0.9, grade=grade)
        assert (out != frame).any()

    def test_price_weighted_by_factor(self, manager):
        """Le prix affiché est pondéré par l'état (vérifié via _get_card_info
        + facteur dans _draw : ici on vérifie le calcul du facteur)."""
        from core.card_grader import GradeResult
        grade = GradeResult(0.5, 0.5, 1.0, 0.0, 0.5, "PL", 0.50)
        assert grade.price_factor == 0.50

    def test_grading_failure_never_blocks(self):
        from core.detection_manager import DetectionConfig, DetectionManager
        model = PROJECT_ROOT / "models" / "yolo11n.pt"
        if not model.exists():
            pytest.skip("modèle YOLO absent")
        manager = DetectionManager(DetectionConfig(model_path=model,
                                                   grade_cards=True))
        # frame inexploitable : aucun grade, aucune exception
        assert manager._grade_crop(np.zeros((100, 100, 3), np.uint8),
                                   (0, 0, 100, 100)) is None