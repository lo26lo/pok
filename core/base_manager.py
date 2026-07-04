"""
BaseManager — plomberie commune des managers du core (refactoring R3).

Factorise les callbacks de log et de progression réimplémentés à
l'identique dans WorkflowManager, TrainingManager et DetectionManager.

Usage:
    class MonManager(BaseManager):
        def __init__(self, config):
            super().__init__()
            self.config = config

        def run(self):
            self._log("démarrage")
            self._update_progress(1, 3, "étape 1...")
"""
import logging
from typing import Callable, Optional


class BaseManager:
    """Callbacks log/progress partagés par les managers du pipeline."""

    def __init__(self):
        self._log_callback: Optional[Callable[[str], None]] = None
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None
        self._logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}")

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """
        Définit la fonction callback pour les logs

        Args:
            callback: Fonction prenant un message string en paramètre
        """
        self._log_callback = callback

    def set_progress_callback(
            self, callback: Callable[[int, int, str], None]) -> None:
        """
        Définit la fonction callback pour la progression

        Args:
            callback: Fonction (current_step, total_steps, message)
        """
        self._progress_callback = callback

    def _log(self, message: str) -> None:
        """Log un message via le logger standard ET le callback GUI"""
        self._logger.info(message)
        if self._log_callback:
            self._log_callback(message)

    def _update_progress(self, current: int, total: int, message: str) -> None:
        """Met à jour la progression via callback"""
        if self._progress_callback:
            self._progress_callback(current, total, message)
