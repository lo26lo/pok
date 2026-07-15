"""
Tests du mode « scan de collection » (F03).

Couvre : confirmation après min_hits frames, déduplication (une même carte
présentée longtemps n'apparaît qu'une fois), quantité par détections
simultanées, mode dégradé par classe YOLO, prix et agrégats, exports
CSV/Excel (totaux corrects), reset, et le critère d'acceptation
« carte présentée 10 s -> une seule entrée ».
"""
import csv
from types import SimpleNamespace

import pytest

from core.collection_scanner import EXPORT_COLUMNS, CollectionScanner


PRICES = {
    "swsh7_003": {"name": "Skiploom", "price": 0.5, "price_max": 1.0},
    "swsh7_013": {"name": "Trevenant V", "price": 2.0, "price_max": 3.5},
    "sv08_019": {"name": "Exeggcute", "price": None, "price_max": None},
}


def det(card_id=None, cls="Pokemon_Card", score=0.9, name=None):
    """Détection factice (duck-typée sur core.detection_manager.Detection)."""
    return SimpleNamespace(card_id=card_id, class_name=cls,
                           identify_score=score if card_id else None,
                           exact_name=name, confidence=0.9)


@pytest.fixture
def scanner():
    return CollectionScanner(min_hits=3, prices=PRICES)


class TestConfirmation:
    def test_not_confirmed_before_min_hits(self, scanner):
        for _ in range(2):
            assert scanner.observe_frame([det("swsh7_003")]) == []
        assert scanner.inventory == []

    def test_confirmed_at_min_hits(self, scanner):
        scanner.observe_frame([det("swsh7_003")])
        scanner.observe_frame([det("swsh7_003")])
        new = scanner.observe_frame([det("swsh7_003")])
        assert len(new) == 1
        assert new[0].card_id == "swsh7_003"
        assert new[0].name == "Skiploom"

    def test_min_hits_one_confirms_immediately(self):
        scanner = CollectionScanner(min_hits=1, prices=PRICES)
        assert len(scanner.observe_frame([det("swsh7_003")])) == 1

    def test_invalid_min_hits(self):
        with pytest.raises(ValueError):
            CollectionScanner(min_hits=0, prices={})

    def test_intermittent_detections_accumulate(self, scanner):
        # Les hits n'ont pas besoin d'être consécutifs (frames ratées)
        scanner.observe_frame([det("swsh7_003")])
        scanner.observe_frame([])
        scanner.observe_frame([det("swsh7_003")])
        scanner.observe_frame([])
        assert len(scanner.observe_frame([det("swsh7_003")])) == 1


class TestDeduplication:
    def test_card_shown_10s_appears_once(self, scanner):
        """Critère d'acceptation F03 : 10 s ≈ 300 frames -> 1 entrée."""
        for _ in range(300):
            scanner.observe_frame([det("swsh7_003")])
        assert len(scanner.inventory) == 1
        assert scanner.summary()["unique_cards"] == 1

    def test_card_leaves_and_returns_still_once(self, scanner):
        for _ in range(5):
            scanner.observe_frame([det("swsh7_003")])
        for _ in range(10):
            scanner.observe_frame([])  # carte retirée
        for _ in range(5):
            scanner.observe_frame([det("swsh7_003")])
        assert len(scanner.inventory) == 1

    def test_multiple_distinct_cards(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003"), det("swsh7_013")])
        ids = {c.card_id for c in scanner.inventory}
        assert ids == {"swsh7_003", "swsh7_013"}


class TestQuantity:
    def test_two_copies_side_by_side(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003"), det("swsh7_003")])
        assert scanner.inventory[0].quantity == 2
        assert scanner.summary()["total_quantity"] == 2

    def test_quantity_can_grow_after_confirmation(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003")])
        assert scanner.inventory[0].quantity == 1
        scanner.observe_frame([det("swsh7_003")] * 3)
        assert scanner.inventory[0].quantity == 3


class TestDegradedMode:
    def test_dedup_by_yolo_class_without_card_id(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det(cls="Exeggcute")])
        card = scanner.inventory[0]
        assert card.key == "yolo:Exeggcute"
        assert card.card_id is None
        assert card.name == "Exeggcute"

    def test_price_via_class_mapping(self, monkeypatch):
        import core.card_mapping as card_mapping
        monkeypatch.setattr(card_mapping, "load_mapping",
                            lambda: {"Trevenant_V": "swsh7_013"})
        scanner = CollectionScanner(min_hits=1, prices=PRICES)
        scanner.observe_frame([det(cls="Trevenant_V")])
        assert scanner.inventory[0].price == 2.0

    def test_detection_without_key_ignored(self, scanner):
        scanner.observe_frame([SimpleNamespace(card_id=None, class_name=None)])
        assert scanner.frames_seen == 1
        assert scanner.inventory == []


class TestPricesAndSummary:
    def test_total_value_min_max(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003"), det("swsh7_013")])
        s = scanner.summary()
        assert s["total_value"] == pytest.approx(2.5)
        assert s["total_value_max"] == pytest.approx(4.5)
        assert s["unpriced_cards"] == 0

    def test_unpriced_card_counted(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("sv08_019")])
        s = scanner.summary()
        assert s["unpriced_cards"] == 1
        assert s["total_value"] == 0.0

    def test_unknown_card_has_no_price(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("xyp_XY01", name="Chespin [xyp XY01]")])
        card = scanner.inventory[0]
        assert card.price is None
        assert card.name == "Chespin [xyp XY01]"  # nom d'identification

    def test_best_score_tracked(self, scanner):
        scanner.observe_frame([det("swsh7_003", score=0.7)])
        scanner.observe_frame([det("swsh7_003", score=0.95)])
        scanner.observe_frame([det("swsh7_003", score=0.8)])
        assert scanner.inventory[0].best_score == pytest.approx(0.95)

    def test_reset(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003")])
        scanner.reset()
        assert scanner.inventory == []
        assert scanner.frames_seen == 0


class TestExports:
    @pytest.fixture
    def populated(self, scanner):
        for _ in range(3):
            scanner.observe_frame([det("swsh7_003"), det("swsh7_003"),
                                   det("swsh7_013")])
        return scanner

    def test_csv_export(self, populated, tmp_path):
        path = populated.export_csv(tmp_path / "scan.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows[0] == EXPORT_COLUMNS
        assert len(rows) == 3  # entête + 2 cartes
        skiploom = next(r for r in rows if r[0] == "swsh7_003")
        assert skiploom[4] == "2"          # quantité
        assert skiploom[7] == "1.0"        # value = 0.5 * 2

    def test_excel_export_with_totals(self, populated, tmp_path):
        openpyxl = pytest.importorskip("openpyxl")
        path = populated.export_excel(tmp_path / "scan.xlsx")
        ws = openpyxl.load_workbook(path).active
        rows = [[c.value for c in row] for row in ws.iter_rows()]
        assert rows[0] == EXPORT_COLUMNS
        total = rows[-1]
        assert total[0] == "TOTAL"
        assert total[4] == 3                       # 2 + 1 exemplaires
        assert total[7] == pytest.approx(3.0)      # 0.5*2 + 2.0
        assert total[8] == pytest.approx(5.5)      # 1.0*2 + 3.5

    def test_default_paths_created(self, populated, tmp_path, monkeypatch):
        import core.collection_scanner as mod
        monkeypatch.setattr(mod, "DEFAULT_OUTPUT_DIR", str(tmp_path / "scans"))
        csv_path = populated.export_csv()
        assert csv_path.exists()
        assert csv_path.suffix == ".csv"

    def test_empty_inventory_exports(self, scanner, tmp_path):
        path = scanner.export_csv(tmp_path / "empty.csv")
        with open(path, encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows == [EXPORT_COLUMNS]
