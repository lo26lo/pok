"""
Package gui_qt — interface PySide6 (Qt 6) du Pokemon Dataset Generator.

Migration depuis Tkinter (plan .planning/2026-07-04_migration-pyside6.md).
Le pipeline (core/) et les modules agnostiques (gui/task_runner, gui/config)
sont consommés tels quels ; seule la couche d'affichage est nouvelle.

Point d'entrée : GUI_qt.py à la racine du projet.
"""

__version__ = "1.0.0"
