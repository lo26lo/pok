"""
Tests fonctionnels de l'auto-balancer (stratégie augment portée
d'imgaug — abandonné, incompatible NumPy 2.x — vers albumentations).
"""
import sys
from pathlib import Path

import pytest

cv2 = pytest.importorskip("cv2")
pytest.importorskip("albumentations")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.auto_balancer_optimized import DatasetBalancerOptimized  # noqa: E402


def _make_dataset(root: Path, per_class: dict) -> Path:
    """Crée images/ + labels/ avec `per_class = {class_id: n_images}`."""
    images = root / "images"
    labels = root / "labels"
    images.mkdir(parents=True)
    labels.mkdir()
    rng = np.random.default_rng(0)
    for class_id, count in per_class.items():
        for i in range(count):
            stem = f"c{class_id}_{i}"
            img = (rng.random((96, 72, 3)) * 255).astype(np.uint8)
            cv2.imwrite(str(images / f"{stem}.png"), img)
            (labels / f"{stem}.txt").write_text(
                f"{class_id} 0.500000 0.500000 0.900000 0.900000\n")
    return root


class TestAnalyze:
    def test_counts_images_not_occurrences(self, tmp_path):
        ds = _make_dataset(tmp_path / "ds", {0: 2})
        # une image avec 3 instances de la classe 0 ne compte qu'une fois
        (ds / "labels" / "c0_0.txt").write_text(
            "0 0.2 0.2 0.1 0.1\n0 0.5 0.5 0.1 0.1\n0 0.8 0.8 0.1 0.1\n")
        balancer = DatasetBalancerOptimized(str(ds), num_workers=1)
        dist = balancer.analyze()
        assert len(dist[0]) == 2


class TestAugmentStrategy:
    def test_balances_minority_class_with_valid_labels(self, tmp_path):
        ds = _make_dataset(tmp_path / "ds", {0: 4, 1: 1})
        balancer = DatasetBalancerOptimized(str(ds), target_count=4,
                                            strategy="augment", num_workers=1)
        balancer.balance()

        bal_images = sorted((ds / "images").glob("c1_*_bal*.png"))
        assert len(bal_images) == 3, [p.name for p in bal_images]

        for img_path in bal_images:
            label = ds / "labels" / f"{img_path.stem}.txt"
            assert label.exists(), f"label manquant pour {img_path.name}"
            parts = label.read_text().split()
            assert len(parts) == 5
            assert int(parts[0]) == 1
            cx, cy, w, h = map(float, parts[1:])
            # bbox valide, transformée mais raisonnable (flip/scale ±10 %)
            assert 0 <= cx - w / 2 + 1e-6 and cx + w / 2 <= 1 + 1e-6
            assert 0 <= cy - h / 2 + 1e-6 and cy + h / 2 <= 1 + 1e-6
            assert 0.6 <= w <= 1.0 and 0.6 <= h <= 1.0

    def test_refresh_split_files_after_balance(self, tmp_path):
        ds = _make_dataset(tmp_path / "ds", {0: 3, 1: 1})
        img = lambda stem: str((ds / "images" / f"{stem}.png").resolve())
        (ds / "train.txt").write_text("\n".join([img("c0_0"), img("c0_1"),
                                                 img("c0_2")]))
        (ds / "val.txt").write_text(img("c1_0"))

        balancer = DatasetBalancerOptimized(str(ds), target_count=3,
                                            strategy="augment", num_workers=1)
        balancer.balance()

        train = (ds / "train.txt").read_text().splitlines()
        val = (ds / "val.txt").read_text().splitlines()
        # les variantes de c1_0 (image de val) rejoignent la VAL (anti-fuite)
        assert img("c1_0") in val
        assert all("c1_0_bal" in Path(p).stem or p == img("c1_0")
                   for p in val), val
        assert len(val) == 3  # source + 2 variantes
        assert len(train) == 3
