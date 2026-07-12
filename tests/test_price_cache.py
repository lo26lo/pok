"""
Tests du cache API hors-ligne (F10).

Couvre : normalisation des identifiants, hit/miss, expiration TTL (entrée
périmée toujours servie), historique append-only (socle F09), purge,
fusion YAML+cache, couche transparente TCGdexAPI.get_card_prices()
(cache frais / API / mode avion), statut de snapshot, sources de
préchargement (base YAML, inventaire F03).
"""
import time

import pytest

from core.price_cache import (
    PriceCache,
    inventory_card_ids,
    load_prices_with_cache,
    normalize_card_id,
    snapshot_status,
    tcgdex_id_candidates,
)
from core.tcgdex_api import TCGdexAPI


@pytest.fixture
def cache(tmp_path):
    return PriceCache(tmp_path / "prices.db", ttl_hours=1)


class TestNormalization:
    def test_tcgdex_id_to_canonical(self):
        assert normalize_card_id("swsh7-3") == "swsh7_003"
        assert normalize_card_id("sv08-019") == "sv08_019"
        assert normalize_card_id("xyp-XY05") == "xyp_XY05"

    def test_canonical_unchanged(self):
        assert normalize_card_id("sv08_019") == "sv08_019"
        assert normalize_card_id("sv04.5_231") == "sv04.5_231"

    def test_tcgdex_candidates(self):
        assert tcgdex_id_candidates("swsh7_003") == ["swsh7-003", "swsh7-3"]
        assert tcgdex_id_candidates("swsh7_123") == ["swsh7-123"]
        assert tcgdex_id_candidates("xyp_XY05") == ["xyp-XY05"]


class TestCacheBasics:
    def test_miss_returns_none(self, cache):
        assert cache.get("sv08_019") is None

    def test_put_then_hit(self, cache):
        cache.put("sv08_019", 0.15, 0.25, "TCGdex(Cardmarket)")
        entry = cache.get("sv08_019")
        assert entry.price == 0.15
        assert entry.price_max == 0.25
        assert entry.source == "TCGdex(Cardmarket)"
        assert not entry.is_stale

    def test_keys_normalized_on_put_and_get(self, cache):
        cache.put("swsh7-3", 1.0, 2.0)
        assert cache.get("swsh7_003").price == 1.0

    def test_priceless_snapshot_allowed(self, cache):
        cache.put("sv08_019", None, None, None)
        entry = cache.get("sv08_019")
        assert entry.price is None

    def test_persistence_across_instances(self, cache, tmp_path):
        cache.put("sv08_019", 0.15, 0.25)
        reopened = PriceCache(tmp_path / "prices.db")
        assert reopened.get("sv08_019").price == 0.15


class TestExpiration:
    def test_fresh_within_ttl(self, cache):
        cache.put("sv08_019", 0.15, 0.25)
        assert not cache.get("sv08_019").is_stale

    def test_stale_after_ttl_but_still_served(self, cache):
        cache.put("sv08_019", 0.15, 0.25, fetched_at=time.time() - 7200)
        entry = cache.get("sv08_019")
        assert entry is not None          # hors-ligne : toujours utilisable
        assert entry.is_stale
        assert entry.date_str             # date visible pour l'affichage

    def test_latest_snapshot_wins(self, cache):
        cache.put("sv08_019", 0.10, 0.20, fetched_at=time.time() - 100)
        cache.put("sv08_019", 0.15, 0.25)
        assert cache.get("sv08_019").price == 0.15


class TestHistoryAndPurge:
    def test_history_newest_first(self, cache):
        now = time.time()
        for i, price in enumerate([1.0, 1.2, 1.1]):
            cache.put("sv08_019", price, None, fetched_at=now - 100 + i)
        prices = [e.price for e in cache.history("sv08_019")]
        assert prices == [1.1, 1.2, 1.0]

    def test_history_is_per_card(self, cache):
        cache.put("sv08_019", 1.0, None)
        cache.put("sv08_020", 2.0, None)
        assert len(cache.history("sv08_019")) == 1

    def test_purge_keeps_most_recent(self, cache):
        now = time.time()
        for i in range(10):
            cache.put("sv08_019", float(i), None, fetched_at=now - 100 + i)
        deleted = cache.purge(keep_per_card=3)
        assert deleted == 7
        prices = [e.price for e in cache.history("sv08_019")]
        assert prices == [9.0, 8.0, 7.0]

    def test_stats(self, cache):
        assert cache.stats()["cards"] == 0
        cache.put("sv08_019", 1.0, None)
        cache.put("sv08_020", 2.0, None)
        stats = cache.stats()
        assert stats["cards"] == 2
        assert stats["snapshots"] == 2
        assert stats["newest"]


class TestMergeWithYaml:
    @pytest.fixture
    def yaml_db(self, tmp_path):
        path = tmp_path / "cards.yaml"
        path.write_text(
            "cards:\n"
            "  sv08_019:\n    name: Exeggcute\n    price: 0.10\n"
            "    price_max: 0.20\n"
            "  sv08_020:\n    name: Exeggutor\n    price: null\n"
            "    price_max: null\n",
            encoding="utf-8")
        return str(path)

    def test_cache_overrides_yaml(self, yaml_db, cache):
        cache.put("sv08_019", 0.55, 0.99, "TCGdex(Cardmarket)")
        merged = load_prices_with_cache(yaml_db, cache.db_path)
        assert merged["sv08_019"]["price"] == 0.55
        assert merged["sv08_019"]["name"] == "Exeggcute"  # nom du YAML gardé
        assert merged["sv08_019"]["price_date"]

    def test_yaml_kept_when_not_cached(self, yaml_db, cache):
        merged = load_prices_with_cache(yaml_db, cache.db_path)
        assert merged["sv08_019"]["price"] == 0.10

    def test_cache_adds_unknown_cards(self, yaml_db, cache):
        cache.put("swsh7_003", 1.5, 2.5)
        merged = load_prices_with_cache(yaml_db, cache.db_path)
        assert merged["swsh7_003"]["price"] == 1.5

    def test_priceless_cache_entry_does_not_erase_yaml(self, yaml_db, cache):
        cache.put("sv08_019", None, None)
        merged = load_prices_with_cache(yaml_db, cache.db_path)
        assert merged["sv08_019"]["price"] == 0.10

    def test_snapshot_status(self, cache):
        assert snapshot_status(cache.db_path) is None
        cache.put("sv08_019", 1.0, None)
        assert "1 prix" in snapshot_status(cache.db_path)


class TestTransparentApiLayer:
    """get_card_prices : cache frais -> API -> cache périmé (mode avion)."""

    @staticmethod
    def api_with(cache, get_card):
        api = TCGdexAPI(cache=cache)
        api.get_card = get_card
        return api

    def test_fresh_cache_short_circuits_network(self, cache):
        cache.put("sv08_019", 0.15, 0.25)
        calls = []
        api = self.api_with(cache, lambda cid: calls.append(cid))
        entry = api.get_card_prices("sv08_019")
        assert entry.price == 0.15
        assert calls == []                  # aucun appel réseau

    def test_api_fetch_populates_cache(self, cache):
        api = self.api_with(
            cache, lambda cid: {'pricing': {'cardmarket': {'trend': 9.9}}})
        entry = api.get_card_prices("sv08_019")
        assert entry.price == 9.9
        assert cache.get("sv08_019").price == 9.9

    def test_airplane_mode_serves_stale(self, cache):
        cache.put("sv08_019", 0.15, 0.25, fetched_at=time.time() - 7200)
        api = self.api_with(cache, lambda cid: None)  # réseau coupé
        entry = api.get_card_prices("sv08_019")
        assert entry.price == 0.15
        assert entry.is_stale

    def test_airplane_mode_unknown_card_none(self, cache):
        api = self.api_with(cache, lambda cid: None)
        assert api.get_card_prices("sv08_999") is None

    def test_padding_variants_tried_on_404(self, cache):
        tried = []

        def get_card(cid):
            tried.append(cid)
            return ({'pricing': {'cardmarket': {'trend': 1.0}}}
                    if cid == "swsh7-3" else None)

        api = self.api_with(cache, get_card)
        entry = api.get_card_prices("swsh7_003")
        assert tried == ["swsh7-003", "swsh7-3"]
        assert entry.price == 1.0

    def test_works_without_cache(self):
        api = TCGdexAPI()
        api.get_card = lambda cid: {'pricing': {'cardmarket': {'trend': 2.0}}}
        entry = api.get_card_prices("sv08_019")
        assert entry.price == 2.0
        assert not entry.is_stale


class TestPreloadSources:
    def test_inventory_card_ids(self, tmp_path):
        csv_path = tmp_path / "scan.csv"
        csv_path.write_text(
            "card_id,name,quantity\n"
            "swsh7_003,Skiploom,1\n"
            "yolo:Exeggcute,Exeggcute,1\n"     # mode dégradé: ignoré
            "sv08_019,Exeggcute,2\n",
            encoding="utf-8")
        assert inventory_card_ids(csv_path) == ["swsh7_003", "sv08_019"]
