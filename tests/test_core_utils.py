"""
Tests unitaires du mapping de classes centralisé (core.utils).

Ces tests verrouillent les garanties introduites en v3.4.2 :
- class_id 0-indexés, contigus, stables (ordre du YAML)
- double clé par carte : identifiant complet + numéro court
- cohérence entre utils, mosaïques et augmentation
"""
import pytest

from core.utils import (
    load_card_data,
    build_class_names_list,
    load_prices,
    load_prices_from_yaml,
    extract_card_number,
    get_message,
)


class TestExtractCardNumber:
    @pytest.mark.parametrize("filename,expected", [
        ("sv08_019_en.png", "019"),
        ("sv08_019_en_aug_042.png", "019"),
        ("sv08_019_fr_holo1.png", "019"),
        ("sv08_019_fr_holo2_aug_003.png", "019"),
        ("xyp_XY05_en.png", "XY05"),
        ("pokemon_en_001_xyz.jpg", "001"),
        ("card_123.jpg", "123"),
    ])
    def test_formats(self, filename, expected):
        assert extract_card_number(filename) == expected

    def test_no_number(self):
        assert extract_card_number("rien.png") is None


class TestLoadCardData:
    def test_zero_indexed_contiguous(self, mini_card_db):
        _, class_map = load_card_data(str(mini_card_db))
        ids = sorted(set(class_map.values()))
        assert ids == [0, 1, 2]

    def test_dual_keys_same_id(self, mini_card_db):
        _, class_map = load_card_data(str(mini_card_db))
        # id complet et numéro court pointent vers la même classe
        assert class_map["tst_001"] == class_map["001"]
        assert class_map["tst_XY03"] == class_map["XY03"]

    def test_order_follows_yaml(self, mini_card_db):
        _, class_map = load_card_data(str(mini_card_db))
        assert class_map["tst_001"] == 0
        assert class_map["tst_002"] == 1
        assert class_map["tst_XY03"] == 2

    def test_names_use_underscores(self, mini_card_db):
        card_dict, _ = load_card_data(str(mini_card_db))
        assert card_dict["tst_001"] == "Pika_Chu"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_card_data(str(tmp_path / "absent.yaml"))

    def test_consistency_with_mosaic_generator(self, mini_card_db):
        """Les mosaïques doivent produire exactement le même mapping."""
        from core.mosaic_optimized import MosaicGeneratorOptimized
        gen = MosaicGeneratorOptimized(num_workers=1, use_gpu=False)
        m_dict, m_map = gen.load_card_data(str(mini_card_db))
        u_dict, u_map = load_card_data(str(mini_card_db))
        assert m_map == u_map
        assert m_dict == u_dict

    def test_augmentation_uses_unified_function(self):
        """L'augmentation ne doit plus avoir de copie locale divergente."""
        aug = pytest.importorskip("core.augmentation_albumentations")
        assert aug.load_card_data is load_card_data
        assert aug.extract_card_number is extract_card_number

    def test_real_database_if_present(self):
        from core.utils import PATHS
        import os
        real_db = PATHS['files']['cards_database_yaml']
        if not os.path.exists(real_db):
            pytest.skip("Base réelle absente")
        _, class_map = load_card_data(real_db)
        ids = sorted(set(class_map.values()))
        assert ids[0] == 0
        assert ids == list(range(len(ids)))


class TestBuildClassNamesList:
    def test_ordered_by_id(self, mini_card_db):
        card_dict, class_map = load_card_data(str(mini_card_db))
        names = build_class_names_list(card_dict, class_map)
        assert names == ["Pika_Chu", "Dracaufeu", "Mew"]

    def test_holes_marked_unused(self):
        names = build_class_names_list({"a": "A", "c": "C"}, {"a": 0, "c": 2})
        assert names == ["A", "unused", "C"]

    def test_empty(self):
        assert build_class_names_list({}, {}) == []


class TestLoadPrices:
    def test_default_argument_does_not_crash(self):
        """Régression B2: load_prices() sans argument levait TypeError."""
        prices = load_prices()
        assert isinstance(prices, dict)

    def test_missing_file_returns_empty(self, tmp_path):
        assert load_prices(str(tmp_path / "absent.yaml")) == {}

    def test_mini_db(self, mini_card_db):
        prices = load_prices_from_yaml(str(mini_card_db))
        assert prices["tst_002"]["price"] == 50.00
        assert prices["tst_XY03"]["price"] is None


class TestGetMessage:
    def test_unknown_key_returns_key(self):
        assert get_message("cle.inconnue.xyz") == "cle.inconnue.xyz"

    def test_known_key(self):
        # 'gui.title' existe dans ui_messages.json
        assert isinstance(get_message("gui.title"), str)
