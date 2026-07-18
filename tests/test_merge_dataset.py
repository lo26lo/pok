"""
Tests du merge de dataset (scripts/merge_dataset.py) :
fonctions unitaires + fusion complète sur une arborescence temporaire.
"""
import sys
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import merge_dataset  # noqa: E402


def _make_tree(base: Path, name: str, stems: list, class_id: int,
               with_labels: bool = True):
    """Crée un dossier images/ + labels/ avec des fichiers factices."""
    images = base / name / "images"
    labels = base / name / "labels"
    images.mkdir(parents=True)
    labels.mkdir(parents=True)
    for stem in stems:
        (images / f"{stem}.png").write_bytes(b"\x89PNG fake")
        if with_labels:
            (labels / f"{stem}.txt").write_text(f"{class_id} 0.5 0.5 1.0 1.0\n")
    return base / name


class TestCopyFiles:
    def test_copies_images_and_labels(self, tmp_path):
        src = _make_tree(tmp_path, "src", ["a", "b"], class_id=0)
        dst_img = tmp_path / "dst/images"
        dst_lbl = tmp_path / "dst/labels"
        dst_img.mkdir(parents=True)
        dst_lbl.mkdir(parents=True)

        count = merge_dataset.copy_files(src / "images", src / "labels",
                                         dst_img, dst_lbl)
        assert count == 2
        assert sorted(p.name for p in dst_img.iterdir()) == ["a.png", "b.png"]
        assert sorted(p.name for p in dst_lbl.iterdir()) == ["a.txt", "b.txt"]

    def test_missing_source_returns_zero(self, tmp_path):
        count = merge_dataset.copy_files(tmp_path / "absent/images",
                                         tmp_path / "absent/labels",
                                         tmp_path, tmp_path)
        assert count == 0


class TestSplitGroupKey:
    def test_strips_variant_suffixes(self):
        assert merge_dataset.split_group_key("sv08_019_en_aug_003") == "sv08_019_en"
        assert merge_dataset.split_group_key("sv08_019_en_bal7") == "sv08_019_en"
        assert merge_dataset.split_group_key("sv08_019_en_holo1_aug_003") == "sv08_019_en"

    def test_mosaics_are_their_own_group(self):
        assert merge_dataset.split_group_key("L1_B0_T0_layout_042") == "L1_B0_T0_layout_042"


class TestTrainValSplit:
    def test_split_ratio(self, tmp_path):
        src = _make_tree(tmp_path, "data", [f"img{i}" for i in range(10)], 0)
        train, val = merge_dataset.create_train_val_split(src / "images",
                                                          train_ratio=0.8)
        assert len(train) == 8
        assert len(val) == 2
        # pas de recouvrement
        assert not set(train) & set(val)
        # chemins absolus (requis par YOLO)
        assert all(Path(p).is_absolute() for p in train + val)

    def test_variants_never_split_across_train_and_val(self, tmp_path):
        # 5 cartes source × 4 variantes augmentées : les variantes d'une
        # même carte doivent rester dans le MÊME split (anti-fuite)
        stems = [f"c{i}_en_aug_{j:03d}" for i in range(5) for j in range(4)]
        src = _make_tree(tmp_path, "data", stems, 0)
        train, val = merge_dataset.create_train_val_split(src / "images",
                                                          train_ratio=0.8)
        assert len(train) + len(val) == 20
        assert val, "le split doit garder un set de validation"
        train_groups = {merge_dataset.split_group_key(Path(p).stem) for p in train}
        val_groups = {merge_dataset.split_group_key(Path(p).stem) for p in val}
        assert not train_groups & val_groups


class TestExtractClassInfo:
    def test_counts_instances(self, tmp_path):
        labels = tmp_path / "labels"
        labels.mkdir()
        (labels / "a.txt").write_text("0 0.5 0.5 1 1\n1 0.5 0.5 1 1\n")
        (labels / "b.txt").write_text("1 0.5 0.5 1 1\n")
        counts = merge_dataset.extract_class_info(labels)
        assert counts == {0: 1, 1: 2}


class TestCreateDataYaml:
    def test_names_padded_with_unused(self, tmp_path):
        merge_dataset.create_data_yaml(tmp_path, {0: "Pika", 2: "Mew"})
        with open(tmp_path / "data.yaml", encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data['names'] == ["Pika", "unused", "Mew"]
        assert data['nc'] == 3
        assert data['train'] == 'train.txt'
        assert data['val'] == 'val.txt'


class TestFullMerge:
    def test_merge_end_to_end(self, tmp_path, monkeypatch):
        """Fusion complète augmented + mosaics dans un CWD temporaire."""
        out = tmp_path / "output"
        aug = _make_tree(out, "augmented", ["c1_en", "c2_en"], class_id=0)
        _make_tree(out, "mosaics", ["m1", "m2", "m3"], class_id=1)

        # data.yaml du dossier augmenté (source des noms de classes)
        with open(aug / "data.yaml", 'w', encoding='utf-8') as f:
            yaml.dump({'nc': 2, 'names': ['Pika_Chu', 'Mew']}, f)

        monkeypatch.chdir(tmp_path)
        merge_dataset.merge_dataset()

        dataset = out / "dataset"
        assert len(list((dataset / "images").iterdir())) == 5
        assert len(list((dataset / "labels").iterdir())) == 5
        assert (dataset / "train.txt").exists()
        assert (dataset / "val.txt").exists()

        with open(dataset / "data.yaml", encoding='utf-8') as f:
            data = yaml.safe_load(f)
        # les noms proviennent du data.yaml augmenté, pas de "class_N"
        assert data['names'] == ['Pika_Chu', 'Mew']

        n_train = len((dataset / "train.txt").read_text().splitlines())
        n_val = len((dataset / "val.txt").read_text().splitlines())
        assert n_train + n_val == 5
