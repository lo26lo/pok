"""
Tests de la prévisualisation live des augmentations (F06).

Couvre build_transform_pool (paramétrage sans régression du pipeline de
production), preview_augmentations (en direct, sans sous-processus, image
d'origine intacte, reproductibilité) et les helpers purs du dialog GUI
(conversion PhotoImage, choix d'échantillon) — le dialog Tk lui-même
nécessite un display et relève du smoke test xvfb.
"""
import base64
import random

import numpy as np
import pytest

pytest.importorskip("albumentations")

from core.augmentation_albumentations import (  # noqa: E402
    AUGMENTATION_CATEGORIES,
    AugmentationAlbumentations,
    build_transform_pool,
    preview_augmentations,
)


def _img(w=280, h=380):
    rng = np.random.default_rng(0)
    return (rng.random((h, w, 3)) * 255).astype(np.uint8)


class TestBuildTransformPool:
    def test_full_pool_has_25_transforms(self):
        assert len(build_transform_pool()) == 25

    def test_category_filter(self):
        sizes = {"brightness": 5, "color": 4, "blur": 4, "noise": 3,
                 "environment": 4, "geometry": 5}
        for cat, expected in sizes.items():
            assert len(build_transform_pool(categories=[cat])) == expected
        assert sum(sizes.values()) == 25
        assert set(sizes) == set(AUGMENTATION_CATEGORIES)

    def test_unknown_category_raises(self):
        with pytest.raises(ValueError):
            build_transform_pool(categories=["lava"])

    def test_empty_categories_raises(self):
        with pytest.raises(ValueError):
            build_transform_pool(categories=[])

    @pytest.mark.parametrize("intensity", [0.1, 0.5, 2.0])
    def test_intensity_extremes_build_and_run(self, intensity):
        pool = build_transform_pool(intensity=intensity)
        assert len(pool) == 25
        out = preview_augmentations(_img(), count=1, intensity=intensity,
                                    seed=1)[0]
        assert out.shape == (380, 280, 3)

    def test_production_pipeline_unchanged(self):
        """Le refactor ne change pas le pipeline historique (intensity=1)."""
        aug = AugmentationAlbumentations(num_workers=1, use_gpu=False)
        assert aug._n_range == (3, 6)
        assert sorted(aug._transforms_by_n) == [3, 4, 5, 6]
        out = aug.augment_image(_img())
        assert out.shape == (380, 280, 3)


class TestPreviewAugmentations:
    def test_count_shape_dtype(self):
        outs = preview_augmentations(_img(), count=4, seed=2)
        assert len(outs) == 4
        for out in outs:
            assert out.shape == (380, 280, 3)
            assert out.dtype == np.uint8

    def test_original_image_untouched(self):
        img = _img()
        before = img.copy()
        preview_augmentations(img, count=3, seed=3)
        np.testing.assert_array_equal(img, before)

    def test_seed_reproducible(self):
        img = _img()
        a = preview_augmentations(img, count=3, seed=42)
        b = preview_augmentations(img, count=3, seed=42)
        for x, y in zip(a, b):
            np.testing.assert_array_equal(x, y)

    def test_different_seeds_differ(self):
        img = _img()
        a = preview_augmentations(img, count=3, seed=1)
        b = preview_augmentations(img, count=3, seed=2)
        assert any(not np.array_equal(x, y) for x, y in zip(a, b))

    def test_variants_differ_from_original(self):
        img = _img()
        outs = preview_augmentations(img, count=3, seed=4)
        assert any(not np.array_equal(out, img) for out in outs)

    def test_single_category(self):
        outs = preview_augmentations(_img(), count=2, n_transforms=2,
                                     categories=["brightness"], seed=5)
        assert len(outs) == 2

    def test_n_transforms_clamped_to_pool_size(self):
        # 8 demandées mais pool 'noise' = 3 : ne doit pas lever
        outs = preview_augmentations(_img(), count=1, n_transforms=8,
                                     categories=["noise"], seed=6)
        assert len(outs) == 1


class TestGuiHelpers:
    def test_image_to_photo_data_is_base64_png(self):
        from gui.augmentation_preview import image_to_photo_data
        data = image_to_photo_data(_img(), width=100, height=136)
        raw = base64.b64decode(data)
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"

    def test_pick_sample_image(self, tmp_path):
        from gui.augmentation_preview import pick_sample_image
        import cv2
        assert pick_sample_image(str(tmp_path)) is None
        for name in ["a.png", "b.jpg"]:
            cv2.imwrite(str(tmp_path / name), _img(50, 70))
        picked = pick_sample_image(str(tmp_path), random.Random(0))
        assert picked is not None and picked.endswith((".png", ".jpg"))
