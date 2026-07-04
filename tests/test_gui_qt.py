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
