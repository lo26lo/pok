"""
Tests du générateur procédural de fonds réalistes (F04).

Vérifie pour chaque catégorie : format, non-uniformité, reproductibilité
par seed ; puis les utilitaires (ombre portée, effets caméra) et
l'intégration du background_mode 3 dans le générateur de mosaïques.
"""
import numpy as np
import pytest

from core.background_generator import (
    CATEGORIES,
    BackgroundGenerator,
    add_drop_shadow,
    apply_camera_effects,
    generate_realistic_background,
)

W, H = 320, 180  # petites images pour des tests rapides


class TestGenerate:
    @pytest.mark.parametrize("category", CATEGORIES)
    def test_shape_dtype_and_variety(self, category):
        img = BackgroundGenerator(seed=1).generate(W, H, category=category)
        assert img.shape == (H, W, 3)
        assert img.dtype == np.uint8
        # Un fond réaliste n'est jamais un aplat uniforme
        assert img.std() > 1.0

    def test_random_category_valid(self):
        img = BackgroundGenerator(seed=2).generate(W, H)
        assert img.shape == (H, W, 3)

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            BackgroundGenerator(seed=3).generate(W, H, category="lava")

    def test_seed_reproducible(self):
        a = generate_realistic_background(W, H, seed=42)
        b = generate_realistic_background(W, H, seed=42)
        np.testing.assert_array_equal(a, b)

    def test_different_seeds_differ(self):
        a = generate_realistic_background(W, H, seed=1)
        b = generate_realistic_background(W, H, seed=2)
        assert not np.array_equal(a, b)


class TestDropShadow:
    def _card(self, w=60, h=90):
        """Carte BGRA opaque au centre, bords transparents."""
        card = np.zeros((h, w, 4), np.uint8)
        card[5:-5, 5:-5, :3] = 200
        card[5:-5, 5:-5, 3] = 255
        return card

    def test_darkens_under_card_only(self):
        canvas = np.full((H, W, 3), 180, np.uint8)
        before = canvas.copy()
        x, y = 100, 40
        out = add_drop_shadow(canvas, self._card(), x, y, offset=(6, 8),
                              blur=9, strength=0.5)
        assert out.shape == before.shape
        # La zone sous la carte est assombrie...
        assert out[y + 45, x + 30].mean() < before[y + 45, x + 30].mean()
        # ... mais un coin éloigné du canvas est intact
        np.testing.assert_array_equal(out[0:10, 0:10], before[0:10, 0:10])

    def test_partially_outside_canvas(self):
        canvas = np.full((H, W, 3), 180, np.uint8)
        # Positions débordant des 4 côtés : ne doit jamais lever d'exception
        for x, y in [(-30, -40), (W - 10, H - 10), (-30, H - 10), (W - 10, -40)]:
            add_drop_shadow(canvas, self._card(), x, y)

    def test_fully_outside_canvas_is_noop(self):
        canvas = np.full((H, W, 3), 180, np.uint8)
        before = canvas.copy()
        out = add_drop_shadow(canvas, self._card(), W + 100, H + 100)
        np.testing.assert_array_equal(out, before)

    def test_bgr_overlay_without_alpha(self):
        canvas = np.full((H, W, 3), 180, np.uint8)
        card = np.full((40, 30, 3), 200, np.uint8)
        out = add_drop_shadow(canvas, card, 50, 50, offset=(5, 5),
                              blur=9, strength=0.5)
        assert out[70, 65].mean() < 180


class TestCameraEffects:
    def test_shape_dtype_preserved(self):
        img = np.full((H, W, 3), 128, np.uint8)
        out = apply_camera_effects(img, rng=np.random.default_rng(0))
        assert out.shape == img.shape
        assert out.dtype == np.uint8

    def test_reproducible_with_rng(self):
        img = generate_realistic_background(W, H, seed=7)
        a = apply_camera_effects(img, rng=np.random.default_rng(5))
        b = apply_camera_effects(img, rng=np.random.default_rng(5))
        np.testing.assert_array_equal(a, b)

    def test_vignette_darkens_corners_vs_center(self):
        img = np.full((H, W, 3), 200, np.uint8)
        # Moyenne sur plusieurs tirages pour lisser les effets directionnels
        corner_deltas = []
        for s in range(5):
            out = apply_camera_effects(img, rng=np.random.default_rng(s)).astype(float)
            corners = (out[0, 0].mean() + out[0, -1].mean()
                       + out[-1, 0].mean() + out[-1, -1].mean()) / 4
            center = out[H // 2, W // 2].mean()
            corner_deltas.append(center - corners)
        assert np.mean(corner_deltas) > 0


class TestMosaicIntegration:
    def test_background_mode_3(self):
        """Le mode 3 du générateur de mosaïques renvoie un fond réaliste."""
        from core.mosaic_optimized import MosaicGeneratorOptimized
        gen = MosaicGeneratorOptimized(num_workers=1, use_gpu=False)
        bg = gen.get_background_optimized(W, H, background_mode=3, fake_images=[])
        assert bg.shape == (H, W, 3)
        assert bg.dtype == np.uint8
        assert bg.std() > 1.0
