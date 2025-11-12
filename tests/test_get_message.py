#!/usr/bin/env python3
"""
Test de la fonction helper get_message()
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import get_message, safe_print

def main():
    """Test get_message helper"""
    safe_print("\n=== TEST: get_message() Helper ===\n")
    
    # Test accès simple
    safe_print("✅ Messages simples:")
    safe_print(f"   - Title: {get_message('gui.title')}")
    safe_print(f"   - Error: {get_message('console.error')}")
    
    # Test avec formatting
    safe_print("\n✅ Messages avec formatage:")
    msg = get_message('console.download_success', ok=10, total=15)
    safe_print(f"   - {msg}")
    
    msg = get_message('console.set_found', name='Temporal Forces', id='sv05', count=162)
    safe_print(f"   - {msg}")
    
    msg = get_message('console.progress', processed=50, total=100, percent=50)
    safe_print(f"   - {msg}")
    
    # Test boutons
    safe_print("\n✅ Boutons:")
    safe_print(f"   - Start: {get_message('gui.buttons.start_download')}")
    safe_print(f"   - Training: {get_message('gui.buttons.start_training')}")
    
    # Test tabs
    safe_print("\n✅ Onglets:")
    safe_print(f"   - General: {get_message('gui.tabs.general')}")
    safe_print(f"   - Training: {get_message('gui.tabs.training')}")
    
    # Test clé inexistante (fallback)
    safe_print("\n✅ Fallback (clé inexistante):")
    safe_print(f"   - {get_message('gui.nonexistent.key')}")
    
    safe_print("\n✅ Tous les tests passés!\n")

if __name__ == "__main__":
    main()
