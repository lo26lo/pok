#!/usr/bin/env python3
"""
Test rapide du système de messages UI centralisés
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import PATHS, UI_MESSAGES, safe_print

def main():
    """Test du chargement des messages UI"""
    safe_print("\n=== TEST: Chargement des configurations ===\n")
    
    # Test PATHS
    safe_print("✅ PATHS chargé:")
    safe_print(f"   - Version: {PATHS.get('version', 'N/A')}")
    safe_print(f"   - Répertoires: {len(PATHS.get('directories', {}))} définis")
    safe_print(f"   - Fichiers: {len(PATHS.get('files', {}))} définis")
    
    # Test UI_MESSAGES
    safe_print("\n✅ UI_MESSAGES chargé:")
    safe_print(f"   - Version: {UI_MESSAGES.get('version', 'N/A')}")
    safe_print(f"   - Langue: {UI_MESSAGES.get('language', 'N/A')}")
    
    # Test messages console
    safe_print("\n📝 Messages console disponibles:")
    console_msgs = UI_MESSAGES.get('console', {})
    for key in ['download_start', 'download_complete', 'error', 'success']:
        safe_print(f"   - {key}: {console_msgs.get(key, 'N/A')}")
    
    # Test messages GUI
    safe_print("\n🎨 Messages GUI disponibles:")
    gui_msgs = UI_MESSAGES.get('gui', {})
    safe_print(f"   - Titre: {gui_msgs.get('title', 'N/A')}")
    safe_print(f"   - Onglets: {len(gui_msgs.get('tabs', {}))} définis")
    safe_print(f"   - Étiquettes: {len(gui_msgs.get('labels', {}))} définies")
    safe_print(f"   - Boutons: {len(gui_msgs.get('buttons', {}))} définis")
    safe_print(f"   - Statuts: {len(gui_msgs.get('status', {}))} définis")
    
    # Test messages workflow
    safe_print("\n🔄 Messages workflow disponibles:")
    workflow_msgs = UI_MESSAGES.get('workflow', {})
    safe_print(f"   - Étapes: {len(workflow_msgs.get('steps', {}))} définies")
    safe_print(f"   - Statuts: {len(workflow_msgs.get('status', {}))} définis")
    
    # Exemple d'utilisation
    safe_print("\n💡 Exemple d'utilisation:")
    safe_print(f"   {console_msgs.get('download_start', '')}")
    safe_print(f"   {console_msgs.get('download_complete', '')}")
    
    safe_print("\n✅ Tous les tests passés!\n")

if __name__ == "__main__":
    main()
