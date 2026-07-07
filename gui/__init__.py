"""
Package GUI - Pokemon Dataset Generator
=======================================

Modules extraits du monolithe GUI_v3.1_modern.py (refactoring Phase 4) :

- theme         : palette de couleurs et constantes de mise en page
- config        : GuiConfig, accès centralisé à config/gui_config.json
- task_runner   : TaskRunner, exécution d'opérations longues (subprocess ou
                  callable) avec streaming des logs et annulation
- settings_dialog : dialogue de configuration (8 onglets)

Les modules theme, config et task_runner sont indépendants de Tkinter et
testables sans display (voir tests/test_gui_modules.py).
"""

__version__ = "3.6.0"
