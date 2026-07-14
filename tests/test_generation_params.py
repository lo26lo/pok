"""
Tests du branchement des paramètres d'augmentation dans la génération
(backlog F06) et du grading agrégé dans le scan de collection
(backlog F03+F02).

Couvre : persistance des paramètres calibrés (save/load, défauts,
robustesse), priorité CLI > fichier > défauts, alias CLI historiques
(--num_aug/--source/--target) utilisés par la GUI et le workflow,
construction de l'augmenteur paramétré (pool filtré, n fixe, défauts de
production inchangés), et la pondération de la valeur d'inventaire par
l'état F02 (meilleur état observé retenu).
"""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("albumentations")

from core.augmentation_albumentations import (  # noqa: E402
    AUGMENTATION_CATEGORIES,
    AugmentationAlbumentations,
    default_generation_params,
    load_generation_params,
    save_generation_params,
)
from core.collection_scanner import CollectionScanner, EXPORT_COLUMNS  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestGenerationParamsFile:
    def test_save_load_roundtrip(self, tmp_path):
        path = tmp_path / "params.json"
        save_generation_params({"intensity": 1.5, "n_transforms": 4,
                                "categories": ["blur", "noise"]}, path)
        loaded = load_generation_params(path)
        assert loaded["intensity"] == 1.5
        assert loaded["n_transforms"] == 4
        assert loaded["categories"] == ["blur", "noise"]

    def test_missing_file_gives_production_defaults(self, tmp_path):
        loaded = load_generation_params(tmp_path / "absent.json")
        assert loaded == default_generation_params()
        assert loaded["intensity"] == 1.0
        assert loaded["n_transforms"] == 0
        assert loaded["categories"] == list(AUGMENTATION_CATEGORIES)

    def test_corrupt_file_never_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{pas du json", encoding="utf-8")
        assert load_generation_params(path)["intensity"] == 1.0

    def test_values_clamped_and_filtered(self, tmp_path):
        path = tmp_path / "params.json"
        save_generation_params({"intensity": 99.0, "n_transforms": -3,
                                "categories": ["blur", "inconnue"]}, path)
        loaded = load_generation_params(path)
        assert loaded["intensity"] == 2.0            # clamp 0.1-2.0
        assert loaded["n_transforms"] == 0           # négatif -> historique
        assert loaded["categories"] == ["blur"]      # catégorie inconnue filtrée


class TestAugmenterParameters:
    def test_production_defaults_unchanged(self):
        aug = AugmentationAlbumentations(num_workers=1, use_gpu=False)
        assert aug._n_range == (3, 6)
        assert aug.intensity == 1.0
        assert len(aug.categories) == len(AUGMENTATION_CATEGORIES)

    def test_filtered_pool_and_fixed_n(self):
        aug = AugmentationAlbumentations(num_workers=1, use_gpu=False,
                                         intensity=1.5, n_transforms=4,
                                         categories=["blur", "noise"])
        assert aug._n_range == (4, 4)
        # blur (4) + noise (3) = 7 transformations
        assert list(aug._transforms_by_n.keys()) == [4]

    def test_n_clamped_to_pool_size(self):
        aug = AugmentationAlbumentations(num_workers=1, use_gpu=False,
                                         n_transforms=50,
                                         categories=["noise"])   # pool de 3
        assert aug._n_range == (3, 3)

    def test_augment_image_works_with_params(self):
        aug = AugmentationAlbumentations(num_workers=1, use_gpu=False,
                                         intensity=0.5, n_transforms=2,
                                         categories=["brightness"])
        img = (np.random.default_rng(0).random((380, 280, 3)) * 255
               ).astype(np.uint8)
        out = aug.augment_image(img)
        assert out.shape == img.shape
        assert out.dtype == np.uint8


class TestCliInterface:
    """Le CLI accepte les alias historiques utilisés par la GUI/workflow."""

    @staticmethod
    def run_cli(*args):
        return subprocess.run(
            [sys.executable, "core/augmentation_albumentations.py", *args],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=120)

    def test_gui_aliases_accepted(self):
        # Mêmes arguments que GUI_v3.1_modern / workflow_manager
        r = self.run_cli("--num_aug", "2", "--source", "dossier_inexistant",
                         "--target", "augtest")
        assert "unrecognized arguments" not in r.stderr
        assert r.returncode == 0                     # sort proprement (0 image)
        assert "Aucune image" in r.stdout

    def test_explicit_cli_params_logged(self):
        r = self.run_cli("--source", "dossier_inexistant",
                         "--intensity", "0.5", "--transforms", "2",
                         "--categories", "blur,noise")
        assert "intensité 0.5x" in r.stdout
        assert "2 transformations" in r.stdout
        assert "(2/6 catégories)" in r.stdout


def det(card_id="swsh7_003", condition=None, condition_score=None,
        price_factor=None):
    return SimpleNamespace(card_id=card_id, class_name="Pokemon_Card",
                           identify_score=0.9, exact_name=None,
                           condition=condition,
                           condition_score=condition_score,
                           price_factor=price_factor)


class TestScannerGrading:
    PRICES = {"swsh7_003": {"name": "Skiploom", "price": 2.0, "price_max": 4.0}}

    @pytest.fixture
    def scanner(self):
        return CollectionScanner(min_hits=2, prices=self.PRICES)

    def test_value_weighted_by_condition(self, scanner):
        for _ in range(2):
            scanner.observe_frame([det(condition="GD", condition_score=0.6,
                                       price_factor=0.70)])
        card = scanner.inventory[0]
        assert card.condition == "GD"
        assert card.value == pytest.approx(2.0 * 0.70)
        assert scanner.summary()["total_value"] == pytest.approx(1.4)

    def test_best_condition_seen_wins(self, scanner):
        scanner.observe_frame([det(condition="PL", condition_score=0.4,
                                   price_factor=0.50)])
        scanner.observe_frame([det(condition="NM", condition_score=0.9,
                                   price_factor=1.0)])
        scanner.observe_frame([det(condition="GD", condition_score=0.6,
                                   price_factor=0.70)])
        card = scanner.inventory[0]
        assert card.condition == "NM"        # meilleure vue = plus fiable
        assert card.value == pytest.approx(2.0)

    def test_grade_can_improve_after_confirmation(self, scanner):
        for _ in range(2):
            scanner.observe_frame([det(condition="GD", condition_score=0.6,
                                       price_factor=0.70)])
        scanner.observe_frame([det(condition="NM", condition_score=0.9,
                                   price_factor=1.0)])
        assert scanner.inventory[0].condition == "NM"

    def test_without_grading_value_unchanged(self, scanner):
        for _ in range(2):
            scanner.observe_frame([det()])
        card = scanner.inventory[0]
        assert card.condition is None
        assert card.value == pytest.approx(2.0)

    def test_condition_in_exports(self, scanner, tmp_path):
        for _ in range(2):
            scanner.observe_frame([det(condition="EX", condition_score=0.75,
                                       price_factor=0.85)])
        assert EXPORT_COLUMNS[-1] == "condition"
        path = scanner.export_csv(tmp_path / "scan.csv")
        header, row = path.read_text(encoding="utf-8").splitlines()
        assert header.endswith(",condition")
        assert row.endswith(",EX")
        openpyxl = pytest.importorskip("openpyxl")
        xlsx = scanner.export_excel(tmp_path / "scan.xlsx")
        ws = openpyxl.load_workbook(xlsx).active
        rows = [[c.value for c in r] for r in ws.iter_rows()]
        assert rows[1][EXPORT_COLUMNS.index("condition")] == "EX"
        # totaux pondérés par l'état
        assert rows[-1][EXPORT_COLUMNS.index("value")] == pytest.approx(2.0 * 0.85)