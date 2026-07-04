"""
Tests des modules du package gui/ indépendants de Tkinter :
GuiConfig, TaskRunner, theme, logging_setup.

(SettingsDialog et ModernPokemonGUI nécessitent un display — ils sont
couverts par le smoke test xvfb, pas par cette suite.)
"""
import sys
import time

import pytest

from gui.config import GuiConfig, DEFAULTS
from gui.task_runner import TaskRunner, TaskError
from gui import theme


# ---------------------------------------------------------------- GuiConfig

class TestGuiConfig:
    def test_defaults_when_missing(self, tmp_path):
        cfg = GuiConfig(str(tmp_path / "absent.json"))
        assert cfg.data == DEFAULTS
        # défauts non partagés (mutation isolée)
        cfg.data["paths"]["output"] = "ailleurs"
        assert DEFAULTS["paths"]["output"] == "output"

    def test_save_and_reload(self, tmp_path):
        path = str(tmp_path / "cfg.json")
        cfg = GuiConfig(path)
        cfg.set("theme", "dark")
        assert cfg.save() is True

        reloaded = GuiConfig(path)
        assert reloaded.get("theme") == "dark"

    def test_corrupted_file_falls_back_to_defaults(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{pas du json", encoding="utf-8")
        cfg = GuiConfig(str(path))
        assert cfg.data == DEFAULTS

    def test_update_preserves_existing_keys(self, tmp_path):
        """Régression: save_settings écrasait paths/last_used."""
        path = str(tmp_path / "cfg.json")
        first = GuiConfig(path)
        first.set("paths", {"output": "custom"})
        first.save()

        second = GuiConfig(path)
        second.update({"holographic_intensity": 0.9})
        second.save()

        final = GuiConfig(path)
        assert final.get("paths") == {"output": "custom"}
        assert final.get("holographic_intensity") == 0.9


# --------------------------------------------------------------- TaskRunner

@pytest.fixture
def runner_env():
    """TaskRunner câblé sur des collecteurs en mémoire (pas de Tk)."""
    logs, ui_calls, lifecycle = [], [], []
    runner = TaskRunner(
        log=logs.append,
        ui_dispatch=ui_calls.append,
        on_start=lambda name: lifecycle.append(("start", name)),
        on_end=lambda: lifecycle.append(("end",)),
    )
    return runner, logs, ui_calls, lifecycle


def _wait(runner, timeout=15):
    runner._thread.join(timeout)
    assert not runner.is_running, "worker toujours en cours"


def _flush_ui(ui_calls):
    """Exécute les callbacks UI comme le ferait le poller du GUI."""
    for fn in list(ui_calls):
        fn()


class TestTaskRunner:
    def test_success_flow(self, runner_env):
        runner, logs, ui_calls, lifecycle = runner_env
        outcome = []

        assert runner.run("Op", lambda r: r.log("travail"),
                          on_success=lambda: outcome.append("ok")) is True
        _wait(runner)
        _flush_ui(ui_calls)

        assert "travail" in logs
        assert outcome == ["ok"]
        assert ("start", "Op") in lifecycle and ("end",) in lifecycle

    def test_task_error_reaches_on_error(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        errors = []

        def worker(r):
            raise TaskError("échec métier")

        runner.run("Op", worker, on_error=errors.append)
        _wait(runner)
        _flush_ui(ui_calls)

        assert errors == ["échec métier"]
        assert any("échec métier" in line for line in logs)

    def test_unexpected_exception_logged(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        errors = []

        def worker(r):
            raise ValueError("boom")

        runner.run("Op", worker, on_error=errors.append)
        _wait(runner)
        _flush_ui(ui_calls)

        assert len(errors) == 1 and "boom" in errors[0]
        assert any("Traceback" in line for line in logs)

    def test_stream_subprocess(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        codes = []

        def worker(r):
            codes.append(r.stream([sys.executable, "-c", "print('sortie test')"]))

        runner.run("Op", worker)
        _wait(runner)

        assert codes == [0]
        assert "sortie test" in logs

    def test_stream_or_fail_raises_on_nonzero(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        errors = []

        def worker(r):
            r.stream_or_fail([sys.executable, "-c", "raise SystemExit(2)"],
                             "commande en échec")

        runner.run("Op", worker, on_error=errors.append)
        _wait(runner)
        _flush_ui(ui_calls)

        assert errors == ["commande en échec"]

    def test_refuses_concurrent_run(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        release = []

        def slow(r):
            while not release:
                time.sleep(0.01)

        assert runner.run("Op1", slow) is True
        assert runner.run("Op2", lambda r: None) is False  # refusé
        release.append(True)
        _wait(runner)

    def test_stop_terminates_process_without_error_popup(self, runner_env):
        runner, logs, ui_calls, _ = runner_env
        errors, successes = [], []

        def worker(r):
            r.stream_or_fail(
                [sys.executable, "-c", "import time; time.sleep(60)"],
                "ne devrait pas s'afficher")

        runner.run("Op", worker,
                   on_success=lambda: successes.append(True),
                   on_error=errors.append)
        # Attendre le démarrage du sous-processus puis stopper
        deadline = time.time() + 10
        while runner._process is None and time.time() < deadline:
            time.sleep(0.02)
        runner.stop()
        _wait(runner)
        _flush_ui(ui_calls)

        assert runner.was_stopped
        # Arrêt volontaire: ni popup d'erreur, ni de succès
        assert errors == [] and successes == []


# ------------------------------------------------------------------- theme

def test_theme_palette_complete():
    required = {'bg_dark', 'bg_sidebar', 'bg_card', 'bg_hover', 'accent',
                'accent_hover', 'success', 'warning', 'error', 'text',
                'text_dim', 'border'}
    assert required <= set(theme.COLORS)
    assert all(v.startswith('#') and len(v) == 7 for v in theme.COLORS.values())


# ---------------------------------------------------------- logging_setup

def test_logging_setup_idempotent(tmp_path, monkeypatch):
    import logging
    from gui import logging_setup

    monkeypatch.setattr(logging_setup, "LOG_DIR", tmp_path)
    monkeypatch.setattr(logging_setup, "LOG_FILE", tmp_path / "test.log")

    root = logging.getLogger()
    before = len(root.handlers)
    logging_setup.setup_logging()
    after_first = len(root.handlers)
    logging_setup.setup_logging()  # 2e appel: aucun handler dupliqué
    assert len(root.handlers) == after_first == before + 1

    logging.getLogger("gui").info("message de test")
    for h in root.handlers[:]:
        if hasattr(h, 'baseFilename') and str(tmp_path) in h.baseFilename:
            h.flush()
            root.removeHandler(h)
            h.close()
    assert "message de test" in (tmp_path / "test.log").read_text(encoding="utf-8")
