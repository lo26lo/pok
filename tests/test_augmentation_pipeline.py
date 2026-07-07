"""
Test de bout en bout du pipeline d'augmentation (Albumentations).

Vérifie sur un mini-dataset de 3 cartes :
- que chaque image générée a un label YOLO avec le bon class_id
- que les images sans mapping sont exclues (pas de class_id aléatoire)
- que data.yaml est écrit avec les noms ordonnés par class_id
"""
import os

import pytest
import yaml

pytest.importorskip("albumentations")

from core.augmentation_albumentations import AugmentationAlbumentations
from core.utils import load_card_data, build_class_names_list


@pytest.fixture
def augmented(tmp_path, mini_card_db, card_images_dir):
    out_dir = tmp_path / "augmented"
    aug = AugmentationAlbumentations(num_workers=1, use_gpu=False)
    total = aug.augment_directory(
        str(card_images_dir), str(out_dir),
        num_aug=2, card_data_path=str(mini_card_db),
    )
    return out_dir, total


def test_generates_expected_count(augmented):
    out_dir, total = augmented
    # 3 cartes connues x 2 augmentations (l'inconnue est exclue)
    assert total == 6
    assert len(os.listdir(out_dir / "images")) == 6
    assert len(os.listdir(out_dir / "labels")) == 6


def test_labels_have_correct_class_ids(augmented, mini_card_db):
    out_dir, _ = augmented
    _, class_map = load_card_data(str(mini_card_db))

    for label_file in (out_dir / "labels").iterdir():
        parts = label_file.read_text().split()
        assert len(parts) == 5, f"format YOLO attendu: {label_file.name}"
        class_id = int(parts[0])
        # retrouver la carte depuis le nom de fichier
        stem = label_file.stem  # ex: tst_001_en_aug_000
        card_key = "_".join(stem.split("_")[:2])  # tst_001 / tst_XY03
        assert class_id == class_map[card_key], label_file.name


def test_unknown_card_excluded(augmented):
    out_dir, _ = augmented
    generated = os.listdir(out_dir / "images")
    assert not any("zzz" in name for name in generated), \
        "l'image sans mapping ne doit produire aucune sortie"


def test_data_yaml_written_and_ordered(augmented, mini_card_db):
    out_dir, _ = augmented
    data_yaml = out_dir / "data.yaml"
    assert data_yaml.exists(), "data.yaml requis par merge_dataset"

    with open(data_yaml, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    card_dict, class_map = load_card_data(str(mini_card_db))
    expected_names = build_class_names_list(card_dict, class_map)
    assert data['names'] == expected_names
    assert data['nc'] == len(expected_names)
