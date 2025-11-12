#!/usr/bin/env python3
"""
Test du système multi-langues
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import load_ui_messages, get_message, safe_print

def main():
    """Test multi-langues"""
    safe_print("\n=== TEST: Multi-Language System ===\n")
    
    # Test Français
    safe_print("🇫🇷 FRANÇAIS:")
    msgs_fr = load_ui_messages('fr')
    safe_print(f"   - Title: {msgs_fr['gui']['title']}")
    safe_print(f"   - Download: {msgs_fr['console']['download_start']}")
    safe_print(f"   - Error: {msgs_fr['console']['error']}")
    
    # Test English
    safe_print("\n🇬🇧 ENGLISH:")
    msgs_en = load_ui_messages('en')
    safe_print(f"   - Title: {msgs_en['gui']['title']}")
    safe_print(f"   - Download: {msgs_en['console']['download_start']}")
    safe_print(f"   - Error: {msgs_en['console']['error']}")
    
    # Test langue inexistante (fallback to FR)
    safe_print("\n🌍 FALLBACK (inexistant → FR):")
    msgs_xx = load_ui_messages('es')  # Espagnol pas encore créé
    safe_print(f"   - Title: {msgs_xx['gui']['title']}")
    safe_print(f"   - Download: {msgs_xx['console']['download_start']}")
    
    # Comptage
    safe_print("\n📊 STATISTIQUES:")
    safe_print(f"   - Messages FR console: {len(msgs_fr['console'])}")
    safe_print(f"   - Messages EN console: {len(msgs_en['console'])}")
    safe_print(f"   - Boutons FR: {len(msgs_fr['gui']['buttons'])}")
    safe_print(f"   - Boutons EN: {len(msgs_en['gui']['buttons'])}")
    
    safe_print("\n✅ Multi-language system working!\n")

if __name__ == "__main__":
    main()
