#!/usr/bin/env python3
"""
Pokémon Dataset Generator — interface Qt (PySide6).

Point d'entrée de la nouvelle interface (migration depuis Tkinter,
plan .planning/2026-07-04_migration-pyside6.md). L'ancienne interface
reste disponible via GUI_v3.1_modern.py tant que la parité n'est pas
validée sur poste réel.

Usage:
    python GUI_qt.py
"""
import sys

from gui.logging_setup import setup_logging


def main() -> int:
    setup_logging()  # logs/pokemon_gui.log (rotation 1 Mo x3)

    from PySide6.QtWidgets import QApplication
    from gui_qt.app import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Pokemon Dataset Generator")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
