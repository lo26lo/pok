"""
QtTaskBridge — adapte gui.task_runner.TaskRunner au monde Qt.

Les signaux Qt étant thread-safe (connexions en file entre threads),
la file manuelle de callbacks du GUI Tkinter devient inutile :
- log(str)        → signal `logged`
- ui_dispatch(fn) → signal `dispatched` (exécuté sur le thread principal)
- on_start/on_end → signaux `started` / `finished`
"""
from PySide6.QtCore import QObject, Signal

from gui.task_runner import TaskRunner, TaskError  # noqa: F401 (TaskError ré-exporté)


class QtTaskBridge(QObject):
    logged = Signal(str)
    dispatched = Signal(object)   # callable à exécuter sur le thread UI
    started = Signal(str)
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.runner = TaskRunner(
            log=self.logged.emit,
            ui_dispatch=self.dispatched.emit,
            on_start=self.started.emit,
            on_end=self.finished.emit,
        )
        # Les callables émis depuis les workers arrivent ici sur le thread UI
        self.dispatched.connect(lambda fn: fn())

    # Raccourcis
    @property
    def is_running(self) -> bool:
        return self.runner.is_running

    def run(self, name, worker, on_success=None, on_error=None) -> bool:
        return self.runner.run(name, worker,
                               on_success=on_success, on_error=on_error)

    def stop(self) -> None:
        self.runner.stop()

    def log(self, message: str) -> None:
        self.logged.emit(message)
