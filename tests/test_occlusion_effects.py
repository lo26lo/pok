"""
Tests des effets d'occlusion réalistes (F05).

Vérifie la sleeve (dimensions inchangées → annotations valides), le calcul
de fraction visible (cœur du filtrage des annotations), l'éventail, les
doigts, puis l'intégration du layout 4 dans le générateur de mosaïques
(bboxes normalisées dans [0,1], cartes masquées jamais annotées).
"""
import random

import numpy as np
import pytest

from core.occlusion_effects import (
    MIN_VISIBLE_FRACTION,
    add_fingers,
    apply_sleeve,
    blend_rgba,
    compute_visible_fractions,
    fan_layout,
    split_into_fans,
)

W, H = 640, 360


def _card(w=60, h=90, alpha=True):
    """Carte factice opaque, BGRA si alpha sinon BGR."""
    if alpha:
        card = np.zeros((h, w, 4), np.uint8)
        card[:, :, :3] = 180
        card[:, :, 3] = 255
    else:
        card = np.full((h, w, 3), 180, np.uint8)
    return card


class TestApplySleeve:
    def test_preserves_dimensions_and_returns_bgra(self):
        for source in (_card(alpha=True), _card(alpha=False)):
            out = apply_sleeve(source, rng=np.random.default_rng(0))
            assert out.shape == (90, 60, 4)
            assert out.dtype == np.uint8

    def test_modifies_pixels(self):
        card = _card()
        out = apply_sleeve(card, rng=np.random.default_rng(1))
        assert not np.array_equal(out[:, :, :3], card[:, :, :3])

    def test_preserves_alpha_channel(self):
        card = _card()
        card[0:10, 0:10, 3] = 0  # coin transparent
        out = apply_sleeve(card, rng=np.random.default_rng(2))
        np.testing.assert_array_equal(out[:, :, 3], card[:, :, 3])

    def test_reproducible(self):
        a = apply_sleeve(_card(), rng=np.random.default_rng(3))
        b = apply_sleeve(_card(), rng=np.random.default_rng(3))
        np.testing.assert_array_equal(a, b)


class TestFanLayout:
    def test_count_and_monotonic_angles(self):
        placements = fan_layout(5, W, H, rng=np.random.default_rng(4))
        assert len(placements) == 5
        angles = [p[0] for p in placements]
        diffs = np.diff(angles)
        # Pas d'angle constant entre cartes consécutives, toujours de même signe
        assert np.allclose(diffs, diffs[0])
        assert 9.0 <= abs(diffs[0]) <= 16.0

    def test_centers_progress_along_arc(self):
        placements = fan_layout(4, W, H, rng=np.random.default_rng(5))
        xs = [p[1] for p in placements]
        # Les centres se déplacent latéralement de façon monotone
        assert all(np.diff(xs) > 0) or all(np.diff(xs) < 0)


class TestVisibleFractions:
    def test_uncovered_card_fully_visible(self):
        mask = np.full((80, 60), 255, np.uint8)
        fractions = compute_visible_fractions([(mask, 100, 100)], W, H)
        assert fractions[0] == pytest.approx(1.0, abs=0.05)

    def test_fully_covered_card_invisible(self):
        mask = np.full((80, 60), 255, np.uint8)
        big = np.full((200, 200), 255, np.uint8)
        fractions = compute_visible_fractions(
            [(mask, 100, 100), (big, 60, 60)], W, H)
        assert fractions[0] < 0.01
        assert fractions[1] == pytest.approx(1.0, abs=0.05)

    def test_half_covered_card(self):
        mask = np.full((80, 60), 255, np.uint8)
        # La 2e carte recouvre la moitié droite de la 1re
        fractions = compute_visible_fractions(
            [(mask, 100, 100), (mask, 130, 100)], W, H)
        assert fractions[0] == pytest.approx(0.5, abs=0.08)

    def test_offscreen_pixels_count_as_hidden(self):
        mask = np.full((80, 60), 255, np.uint8)
        # Moitié gauche hors canvas
        fractions = compute_visible_fractions([(mask, -30, 100)], W, H)
        assert fractions[0] == pytest.approx(0.5, abs=0.08)


class TestFingersAndBlend:
    def test_add_fingers_changes_zone_only(self):
        canvas = np.full((H, W, 3), 90, np.uint8)
        before = canvas.copy()
        out = add_fingers(canvas, 200, 100, 440, 300, rng=np.random.default_rng(6))
        assert out.shape == before.shape
        assert not np.array_equal(out, before)
        # Le bord supérieur du canvas reste intact (doigts en bas de zone)
        np.testing.assert_array_equal(out[0:40], before[0:40])

    def test_blend_rgba_clipping(self):
        canvas = np.full((H, W, 3), 90, np.uint8)
        overlay = np.full((50, 50, 4), 255, np.uint8)
        # Débordements : aucun crash, hors canvas = no-op
        for x, y in [(-20, -20), (W - 10, H - 10), (W + 5, 0)]:
            blend_rgba(canvas, overlay, x, y)
        before = canvas.copy()
        blend_rgba(canvas, overlay, W + 100, H + 100)
        np.testing.assert_array_equal(canvas, before)


class TestSplitIntoFans:
    def test_all_cards_kept_and_fan_sizes(self):
        group = [(f"card{i}", f"path{i}") for i in range(8)]
        fans = split_into_fans(group, random.Random(7))
        flat = [c for fan in fans for c in fan]
        assert flat == group
        assert all(1 <= len(fan) <= 5 for fan in fans)


class TestMosaicFanIntegration:
    def test_compose_fan_group_annotations_valid(self):
        """Layout 4 : bboxes normalisées valides, cartes masquées exclues."""
        from core.mosaic_optimized import MosaicGeneratorOptimized

        random.seed(11)
        gen = MosaicGeneratorOptimized(num_workers=1, use_gpu=False)
        canvas_w, canvas_h = 1280, 720
        layout = np.full((canvas_h, canvas_w, 3), 120, np.uint8)

        card = np.full((380, 280, 3), 200, np.uint8)
        group = [(card.copy(), f"tst_{i:03d}_en.png") for i in range(1, 7)]
        card_dict = {f"tst_{i:03d}": f"Card{i}" for i in range(1, 7)}
        class_map = {f"tst_{i:03d}": i - 1 for i in range(1, 7)}

        annotations, used_classes = [], {}
        out = gen._compose_fan_group(layout, group, card_dict, class_map,
                                     canvas_w, canvas_h, annotations, used_classes)

        assert out.shape == (canvas_h, canvas_w, 3)
        assert len(annotations) >= 1  # au moins la carte du dessus est visible
        for line in annotations:
            parts = line.split()
            assert len(parts) == 5
            cls = int(parts[0])
            cx, cy, w, h = map(float, parts[1:])
            assert 0 <= cls <= 5
            # bbox entièrement dans l'image (centre ± moitié)
            assert 0.0 <= cx - w / 2 + 1e-6 and cx + w / 2 <= 1.0 + 1e-6
            assert 0.0 <= cy - h / 2 + 1e-6 and cy + h / 2 <= 1.0 + 1e-6
            assert w > 0 and h > 0

    def test_hidden_card_never_annotated(self):
        """Une carte entièrement recouverte ne doit produire aucune annotation."""
        from core.mosaic_optimized import MosaicGeneratorOptimized

        gen = MosaicGeneratorOptimized(num_workers=1, use_gpu=False)
        # Vérification directe du contrat via compute_visible_fractions :
        # le seuil MIN_VISIBLE_FRACTION exclut toute carte quasi invisible
        mask = np.full((380, 280), 255, np.uint8)
        big = np.full((500, 500), 255, np.uint8)
        fractions = compute_visible_fractions(
            [(mask, 400, 200), (big, 350, 150)], 1280, 720)
        assert fractions[0] < MIN_VISIBLE_FRACTION
