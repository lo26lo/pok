"""
Tests du GUI Qt (PySide6) — exécutés offscreen, y compris en CI.

Nécessite pyside6 + pytest-qt ; skip proprement si absents.
"""
import os
import sys
import time

import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from gui_qt.app import MainWindow, VIEWS          # noqa: E402
from gui_qt.theme import THEMES, build_qss        # noqa: E402


@pytest.fixture
def window(qtbot, tmp_path, monkeypatch):
    # Config isolée: ne pas écrire le gui_config.json du projet
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir()
    import shutil
    project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shutil.copy(os.path.join(project, "config", "paths.json"),
                tmp_path / "config" / "paths.json")
    monkeypatch.chdir(project)

    win = MainWindow()
    # Rediriger la persistance du thème vers un fichier temporaire
    win.config.path = tmp_path / "gui_config.json"
    qtbot.addWidget(win)
    return win


class TestShell:
    def test_eleven_views_navigable(self, window, qtbot):
        assert window.stack.count() == len(VIEWS) == 11
        for i, (view_id, _) in enumerate(VIEWS):
            window.sidebar.setCurrentRow(i)
            qtbot.wait(10)
            assert window.stack.currentIndex() == i

    def test_theme_toggle_and_persist(self, window):
        initial = window.theme_name
        window.toggle_theme()
        assert window.theme_name != initial
        # Persisté dans la config
        assert window.config.get("ui_theme") == window.theme_name
        window.toggle_theme()
        assert window.theme_name == initial

    def test_qss_generated_for_both_themes(self):
        for name, palette in THEMES.items():
            qss = build_qss(palette)
            assert "QMainWindow" in qss
            assert palette['accent'] in qss


class TestBridge:
    def _wait_done(self, window, qtbot, results, keys, timeout=15):
        deadline = time.time() + timeout
        while time.time() < deadline and not any(k in results for k in keys):
            qtbot.wait(20)

    def test_subprocess_streams_to_log_panel(self, window, qtbot):
        results = {}

        def work(runner):
            results['rc'] = runner.stream(
                [sys.executable, "-c", "print('qt stream test')"])

        window.bridge.run("Test", work,
                          on_success=lambda: results.setdefault('ok', True))
        self._wait_done(window, qtbot, results, ('ok',))

        assert results.get('rc') == 0 and results.get('ok') is True
        assert "qt stream test" in window.log_panel.toPlainText()
        assert not window.bridge.is_running

    def test_failure_reaches_on_error(self, window, qtbot):
        from gui.task_runner import TaskError
        results = {}

        def work(runner):
            raise TaskError("échec de test")

        window.bridge.run("Test", work, on_error=lambda m: results.setdefault('err', m))
        self._wait_done(window, qtbot, results, ('err',))
        assert results.get('err') == "échec de test"

    def test_busy_state_updates_statusbar(self, window, qtbot):
        release = []

        def slow(runner):
            while not release:
                time.sleep(0.01)

        window.bridge.run("SlowOp", slow)
        qtbot.wait(50)
        assert window.stop_button.isEnabled()
        assert "SlowOp" in window.status_label.text()

        release.append(True)
        deadline = time.time() + 10
        while time.time() < deadline and window.bridge.is_running:
            qtbot.wait(20)
        qtbot.wait(50)
        assert not window.stop_button.isEnabled()
        assert window.status_label.text() == "Ready"


class TestDetectionViewParity:
    """Parité vagues 3 & 4 : la vue Détection Qt expose F01/F02/F03/F10."""

    def test_detection_config_carries_identify_and_grade(self, window, tmp_path):
        from core.detection_manager import DetectionConfig
        view = window.views["detection"]
        model = tmp_path / "m.pt"
        model.write_bytes(b"x")
        view.model_path.set_text(str(model))
        view.identify_cards.setChecked(True)
        view.grade_cards.setChecked(True)
        # DetectionConfig valide sans charger de vrai modèle (post_init tolère)
        import core.detection_manager as dm

        class Cfg(DetectionConfig):
            def __post_init__(self):
                pass
        monkey = dm.DetectionConfig
        dm.DetectionConfig = Cfg
        try:
            cfg = view._make_config()
        finally:
            dm.DetectionConfig = monkey
        assert cfg.identify_cards and cfg.grade_cards

    def test_snapshot_label_present(self, window):
        view = window.views["detection"]
        assert "snapshot" in view.snapshot_label.text().lower() \
            or "💾" in view.snapshot_label.text()

    def test_open_scans_folder_creates_dir(self, window, monkeypatch):
        import gui_qt.views.detection as det_mod
        opened = {}
        monkeypatch.setattr(det_mod.QDesktopServices, "openUrl",
                            lambda url: opened.setdefault("url", url))
        window.views["detection"].open_scans_folder()
        from core.utils import PATHS
        from pathlib import Path
        assert Path(PATHS['directories']['output_collection_scans']).exists()
        assert "url" in opened


class TestAugmentationParams:
    """F06 : les paramètres calibrés sont passés à la génération."""

    def test_default_flags(self, window):
        view = window.views["augmentation"]
        flags = view._param_flags()
        assert flags[:2] == ["--intensity", "1.00"]
        assert "--transforms" in flags
        # toutes catégories cochées -> pas de --categories
        assert "--categories" not in flags

    def test_subset_categories_flag(self, window):
        view = window.views["augmentation"]
        for cat, box in view.category_boxes.items():
            box.setChecked(cat in ("blur", "noise"))
        flags = view._param_flags()
        assert "--categories" in flags
        cats = flags[flags.index("--categories") + 1]
        assert set(cats.split(",")) == {"blur", "noise"}

    def test_intensity_reflected(self, window):
        view = window.views["augmentation"]
        view.intensity.setValue(150)
        assert view._param_flags()[1] == "1.50"


class TestPriceHistoryDialog:
    def test_dialog_opens_and_lists_cards(self, window, tmp_path):
        from gui_qt.price_history_dialog import (
            PriceHistoryDialog, format_history_label, sparkline_points)
        from core.price_cache import PriceCache
        db = tmp_path / "p.db"
        cache = PriceCache(db)
        cache.put("sv08_019", 0.5, 1.0)
        cache.put("sv08_019", 0.7, 1.2)
        dialog = PriceHistoryDialog(window, db_path=str(db))
        assert dialog.card_combo.count() == 1
        # sparkline pure helpers
        assert sparkline_points([]) == []
        pts = sparkline_points([1.0, 2.0], width=100, height=50, pad=10)
        assert pts[0][1] > pts[-1][1]      # min plus bas que max
        assert "actuellement" in format_history_label(cache.history("sv08_019"))

    def test_alert_crud_via_dialog(self, window, tmp_path, monkeypatch):
        from gui_qt.price_history_dialog import PriceHistoryDialog
        from core.price_cache import PriceCache
        db = tmp_path / "p.db"
        cache = PriceCache(db)
        cache.put("sv08_019", 1.0, 2.0)
        dialog = PriceHistoryDialog(window, db_path=str(db))
        dialog.card_combo.setCurrentIndex(0)
        dialog.threshold.setValue(1.5)
        dialog.direction.setCurrentText("above")
        dialog._set_alert()
        assert len(cache.list_alerts()) == 1
        assert dialog.alerts_list.count() == 1


class TestSettingsView:
    def test_settings_save_roundtrip(self, window, qtbot, tmp_path, monkeypatch):
        from gui.config import GuiConfig
        import gui_qt.views.settings as settings_module

        # Rediriger GuiConfig de la vue vers un fichier temporaire
        cfg_path = tmp_path / "settings_test.json"
        real_cfg = GuiConfig

        class TmpConfig(real_cfg):
            def __init__(self, path=str(cfg_path)):
                super().__init__(path)

        monkeypatch.setattr(settings_module, "GuiConfig", TmpConfig)

        view = window.views["settings"]
        widget, kind = view._widgets["default_epochs"]
        widget.setValue(123)
        # Neutraliser la popup
        monkeypatch.setattr(window, "notify_info", lambda *a: None)
        view.save()

        assert TmpConfig().get("default_epochs") == 123
