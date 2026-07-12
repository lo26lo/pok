"""
Tests de l'historique et des alertes de prix (F09).

Couvre : persistance des alertes entre sessions, cycle de déclenchement
fiable (armée -> déclenchée -> désarmée -> réarmée quand la condition
redevient fausse), directions above/below, alertes évaluées en fin de
préchargement, helpers purs des sparklines (sans Tk).
"""
import time

import pytest

from core.price_cache import PriceCache
from gui.price_history_view import format_history_label, sparkline_points


@pytest.fixture
def cache(tmp_path):
    return PriceCache(tmp_path / "prices.db", ttl_hours=1)


class TestAlertCrud:
    def test_set_and_list(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        alerts = cache.list_alerts()
        assert len(alerts) == 1
        assert alerts[0].card_id == "sv08_019"
        assert alerts[0].threshold == 1.0
        assert alerts[0].armed

    def test_replace_same_direction(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.set_alert("sv08_019", 2.0, "above")
        alerts = cache.list_alerts()
        assert len(alerts) == 1
        assert alerts[0].threshold == 2.0

    def test_both_directions_coexist(self, cache):
        cache.set_alert("sv08_019", 5.0, "above")
        cache.set_alert("sv08_019", 1.0, "below")
        assert len(cache.list_alerts()) == 2

    def test_remove(self, cache):
        cache.set_alert("sv08_019", 5.0, "above")
        cache.set_alert("sv08_019", 1.0, "below")
        assert cache.remove_alert("sv08_019", "above") == 1
        assert len(cache.list_alerts()) == 1
        assert cache.remove_alert("sv08_019") == 1
        assert cache.list_alerts() == []

    def test_invalid_inputs(self, cache):
        with pytest.raises(ValueError):
            cache.set_alert("sv08_019", 1.0, "sideways")
        with pytest.raises(ValueError):
            cache.set_alert("sv08_019", -1.0, "above")

    def test_persistent_across_instances(self, cache, tmp_path):
        cache.set_alert("sv08_019", 1.0, "above")
        reopened = PriceCache(tmp_path / "prices.db")
        assert len(reopened.list_alerts()) == 1

    def test_describe(self, cache):
        assert cache.set_alert("sv08_019", 1.5, "above").describe() \
            == "sv08_019 ≥ 1.50€"
        assert cache.set_alert("sv08_019", 0.5, "below").describe() \
            == "sv08_019 ≤ 0.50€"


class TestAlertTriggering:
    def test_no_trigger_below_threshold(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", 0.5, None)
        assert cache.check_alerts() == []

    def test_trigger_on_crossing(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", 1.5, None)
        triggered = cache.check_alerts()
        assert len(triggered) == 1
        assert triggered[0].price == 1.5
        assert "dépasse" in triggered[0].describe()

    def test_no_repeat_while_condition_holds(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", 1.5, None)
        cache.check_alerts()
        cache.put("sv08_019", 1.8, None)
        assert cache.check_alerts() == []      # désarmée, pas de spam

    def test_rearm_after_condition_clears(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", 1.5, None)
        cache.check_alerts()
        cache.put("sv08_019", 0.8, None)
        assert cache.check_alerts() == []      # réarme silencieusement
        assert cache.list_alerts()[0].armed
        cache.put("sv08_019", 1.2, None)
        assert len(cache.check_alerts()) == 1  # se re-déclenche

    def test_below_direction(self, cache):
        cache.set_alert("sv08_019", 1.0, "below")
        cache.put("sv08_019", 1.5, None)
        assert cache.check_alerts() == []
        cache.put("sv08_019", 0.9, None)
        triggered = cache.check_alerts()
        assert len(triggered) == 1
        assert "passe sous" in triggered[0].describe()

    def test_alert_without_snapshot_ignored(self, cache):
        cache.set_alert("sv08_999", 1.0, "above")
        assert cache.check_alerts() == []

    def test_priceless_snapshot_ignored(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", None, None)
        assert cache.check_alerts() == []

    def test_triggered_at_recorded(self, cache):
        cache.set_alert("sv08_019", 1.0, "above")
        cache.put("sv08_019", 1.5, None)
        before = time.time()
        cache.check_alerts()
        alert = cache.list_alerts()[0]
        assert alert.triggered_at is not None
        assert alert.triggered_at >= before - 1


class TestPreloadChecksAlerts:
    def test_preload_returns_triggered_alerts(self, cache, monkeypatch):
        """Le préchargement (relevé périodique) évalue les alertes."""
        from core import price_cache as mod
        from core import tcgdex_api as api_mod

        cache.set_alert("sv08_019", 1.0, "above")
        monkeypatch.setattr(mod, "PriceCache",
                            lambda db_path=None, **kw: cache)
        monkeypatch.setattr(
            api_mod.TCGdexAPI, "get_card",
            lambda self, cid: {'pricing': {'cardmarket': {'trend': 2.5}}})

        result = mod.preload_prices(card_ids=["sv08_019"], workers=1,
                                    progress_callback=lambda *a: None)
        assert result["priced"] == 1
        assert len(result["alerts"]) == 1
        assert result["alerts"][0].price == 2.5


class TestSparklineHelpers:
    def test_empty_series(self):
        assert sparkline_points([]) == []
        assert sparkline_points([None, None]) == []

    def test_two_points_span_width(self):
        pts = sparkline_points([1.0, 2.0], width=100, height=50, pad=10)
        assert pts[0] == (10.0, 40.0)       # min en bas
        assert pts[-1] == (90.0, 10.0)      # max en haut

    def test_flat_series_mid_height(self):
        pts = sparkline_points([2.0, 2.0, 2.0], width=100, height=50, pad=10)
        assert all(y == 25.0 for _, y in pts)

    def test_single_point(self):
        assert sparkline_points([1.5], width=100, height=50, pad=10) \
            == [(10.0, 25.0)]

    def test_none_values_skipped(self):
        pts = sparkline_points([1.0, None, 3.0], width=100, height=50, pad=10)
        assert len(pts) == 2

    def test_format_history_label(self, cache):
        now = time.time()
        cache.put("sv08_019", 1.0, None, fetched_at=now - 100)
        cache.put("sv08_019", 1.5, None, fetched_at=now)
        label = format_history_label(cache.history("sv08_019"))
        assert "1.50€ actuellement" in label
        assert "min 1.00€" in label
        assert "▲ +0.50€" in label

    def test_format_history_label_empty(self):
        assert format_history_label([]) == "Aucun relevé de prix"
