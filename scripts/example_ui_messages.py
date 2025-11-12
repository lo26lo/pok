#!/usr/bin/env python3
"""
Exemple d'utilisation du système de messages UI centralisés
À utiliser comme référence pour les autres scripts
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import PATHS, UI_MESSAGES, safe_print

def example_download_workflow():
    """Exemple de workflow de téléchargement avec messages UI"""
    msgs = UI_MESSAGES['console']
    
    # Démarrage
    safe_print(msgs['download_start'])
    
    # Simulation de travail
    import time
    time.sleep(1)
    
    # Complétion
    safe_print(msgs['download_complete'])

def example_gui_labels():
    """Exemple d'utilisation des labels GUI"""
    gui_msgs = UI_MESSAGES['gui']
    
    safe_print(f"\nTitre application: {gui_msgs['title']}")
    safe_print(f"\nOnglets disponibles:")
    for key, value in gui_msgs['tabs'].items():
        safe_print(f"   - {key}: {value}")

def example_workflow_steps():
    """Exemple d'affichage des étapes de workflow"""
    workflow_msgs = UI_MESSAGES['workflow']
    
    safe_print(f"\nÉtapes du workflow:")
    for key, value in workflow_msgs['steps'].items():
        status = workflow_msgs['status']['pending']
        safe_print(f"   [{status}] {value}")

def main():
    """Démonstration complète"""
    safe_print("=== Démonstration UI Messages ===\n")
    
    example_download_workflow()
    example_gui_labels()
    example_workflow_steps()
    
    safe_print("\n✅ Démonstration terminée!")

if __name__ == "__main__":
    main()
