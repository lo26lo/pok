"""
Configuration globale du logging (Phase 4).

Un fichier tournant logs/pokemon_gui.log reçoit tout ce qui passe par le
module `logging` : les managers du core (via BaseManager._log) et le
panneau de log du GUI (ModernPokemonGUI.log).
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "pokemon_gui.log"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure le logger racine (idempotent)."""
    root = logging.getLogger()

    # Déjà configuré (relance, tests) → ne pas dupliquer les handlers
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return

    root.setLevel(level)
    LOG_DIR.mkdir(exist_ok=True)

    handler = RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)-7s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'))
    root.addHandler(handler)
