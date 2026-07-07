"""
TaskRunner — exécution centralisée des opérations longues du GUI.

Remplace les ~12 blocs copiés-collés « Popen → lecture stdout →
messagebox → end_operation » de GUI_v3.1_modern.py (refactoring R2).

Principes:
- UNE seule opération à la fois (l'équivalent de l'ancien is_running)
- le worker s'exécute dans un thread daemon; il ne touche JAMAIS aux
  widgets: les callbacks de fin sont replanifiés sur le thread UI via
  ui_dispatch (typiquement lambda fn: root.after(0, fn))
- les sous-processus sont lancés via runner.stream(cmd) qui streame
  stdout ligne à ligne vers le callback de log (thread-safe côté GUI)
- stop() termine le sous-processus en cours et marque l'arrêt volontaire

Indépendant de Tkinter → testable sans display (tests/test_gui_modules.py).
"""
import subprocess
import threading
from typing import Callable, List, Optional


class TaskError(Exception):
    """Échec fonctionnel d'une tâche (message destiné à l'utilisateur)."""


class TaskRunner:
    def __init__(self,
                 log: Callable[[str], None],
                 ui_dispatch: Callable[[Callable[[], None]], None],
                 on_start: Optional[Callable[[str], None]] = None,
                 on_end: Optional[Callable[[], None]] = None):
        """
        Args:
            log: fonction de log thread-safe (ex: ModernPokemonGUI.log)
            ui_dispatch: planifie un callable sur le thread UI
                         (ex: lambda fn: root.after(0, fn))
            on_start: appelé (thread appelant) au démarrage, reçoit le nom
            on_end: appelé (via ui_dispatch) à la fin, succès ou non
        """
        self.log = log
        self._ui = ui_dispatch
        self._on_start = on_start
        self._on_end = on_end

        self._thread: Optional[threading.Thread] = None
        self._process: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()
        self._stopped = False

    # ------------------------------------------------------------------ état

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def was_stopped(self) -> bool:
        """True si la dernière tâche a été interrompue par stop()."""
        return self._stopped

    # ------------------------------------------------------------- exécution

    def run(self,
            name: str,
            worker: Callable[["TaskRunner"], None],
            on_success: Optional[Callable[[], None]] = None,
            on_error: Optional[Callable[[str], None]] = None) -> bool:
        """
        Lance `worker(runner)` dans un thread daemon.

        Le worker signale un échec en levant TaskError(message).
        on_success / on_error(message) sont exécutés sur le thread UI.

        Returns:
            False si une tâche est déjà en cours (rien n'est lancé).
        """
        if self.is_running:
            self.log("⚠️ Une opération est déjà en cours!")
            return False

        self._stopped = False
        if self._on_start:
            self._on_start(name)

        def _wrapper():
            error_message: Optional[str] = None
            try:
                worker(self)
            except TaskError as exc:
                error_message = str(exc)
            except Exception as exc:  # défaut inattendu: log complet
                import traceback
                self.log(traceback.format_exc())
                error_message = f"Erreur inattendue: {exc}"

            stopped = self._stopped
            if error_message is not None and not stopped:
                self.log(f"❌ {error_message}")
                if on_error:
                    self._ui(lambda: on_error(error_message))
            elif error_message is None and not stopped and on_success:
                self._ui(on_success)

            if self._on_end:
                self._ui(self._on_end)

        self._thread = threading.Thread(target=_wrapper, daemon=True)
        self._thread.start()
        return True

    def stream(self, command: List[str], cwd: Optional[str] = None) -> int:
        """
        Exécute un sous-processus en streamant stdout vers le log.

        À appeler DEPUIS un worker. Encodage utf-8 tolérant (Windows).

        Returns:
            Code retour du processus, ou -1 s'il a été stoppé via stop().
        """
        with self._lock:
            if self._stopped:
                return -1
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                cwd=cwd,
            )
            process = self._process

        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.rstrip())
            process.wait()
        finally:
            with self._lock:
                self._process = None

        return -1 if self._stopped else process.returncode

    def stream_or_fail(self, command: List[str], error_message: str,
                       cwd: Optional[str] = None) -> None:
        """stream() + TaskError si le code retour est non nul."""
        returncode = self.stream(command, cwd=cwd)
        if self._stopped:
            raise TaskError("Opération arrêtée")
        if returncode != 0:
            raise TaskError(error_message)

    # ------------------------------------------------------------------ stop

    def stop(self) -> None:
        """Interrompt la tâche en cours (terminate puis kill du processus)."""
        self._stopped = True
        with self._lock:
            process = self._process
        if process is None or process.poll() is not None:
            return
        try:
            self.log("⏹ Arrêt de l'opération en cours...")
            process.terminate()
            process.wait(timeout=5)
            self.log("✅ Opération arrêtée")
        except Exception:
            try:
                process.kill()
                self.log("✅ Opération arrêtée (forcé)")
            except Exception as exc:
                self.log(f"❌ Erreur d'arrêt: {exc}")
