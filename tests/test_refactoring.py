#!/usr/bin/env python3
"""
Test de validation du refactoring - Code Duplication Removal
Vérifie que les fonctions centralisées fonctionnent correctement
"""
import sys
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test que tous les imports fonctionnent"""
    try:
        from core.utils import (
            safe_print,
            extract_card_number,
            load_card_data,
            resize_cards,
            PATTERN_NEW_FORMAT,
            PATTERN_OLD_FORMAT,
            PATTERN_FALLBACK_1,
            PATTERN_FALLBACK_2,
            CONFIG
        )
        print("✅ Imports depuis core.utils fonctionnent")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_extract_card_number():
    """Test de la fonction extract_card_number"""
    from core.utils import extract_card_number
    
    # Test cas basiques
    tests = [
        ("sv08_019_en.png", "019"),
        ("sv08_019_en_aug_042.png", "019"),
        ("xyp_XY05_en.png", "XY05"),
        ("pokemon_en_001_xyz.jpg", "001"),
        ("card_123.jpg", "123"),
    ]
    
    all_pass = True
    for filename, expected in tests:
        result = extract_card_number(filename)
        if result == expected:
            print(f"✅ extract_card_number('{filename}') = '{result}'")
        else:
            print(f"❌ extract_card_number('{filename}') = '{result}' (attendu: '{expected}')")
            all_pass = False
    
    return all_pass

def test_patterns_exported():
    """Test que les patterns regex sont bien exportés"""
    from core.utils import (
        PATTERN_NEW_FORMAT,
        PATTERN_OLD_FORMAT,
        PATTERN_FALLBACK_1,
        PATTERN_FALLBACK_2
    )
    
    # Vérifier qu'ils sont compilés
    if hasattr(PATTERN_NEW_FORMAT, 'search'):
        print("✅ Les patterns regex sont correctement exportés et compilés")
        return True
    else:
        print("❌ Les patterns ne sont pas des objets regex compilés")
        return False

def test_numpy_version():
    """Test que NumPy < 2.0 est utilisé (requis pour imgaug)"""
    import numpy as np
    
    major_version = int(np.__version__.split('.')[0])
    
    if major_version < 2:
        print(f"✅ NumPy {np.__version__} < 2.0 (compatible imgaug)")
        return True
    else:
        print(f"❌ NumPy {np.__version__} >= 2.0 (incompatible imgaug)")
        return False

def test_config_exported():
    """Test que CONFIG est exporté"""
    from core.utils import CONFIG
    
    required_keys = ['target_size', 'excel_file', 'base_images_dir']
    if all(key in CONFIG for key in required_keys):
        print(f"✅ CONFIG exporté avec clés requises: {required_keys}")
        return True
    else:
        print(f"❌ CONFIG manque des clés requises")
        return False

def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("🧪 Tests de validation du refactoring")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("extract_card_number()", test_extract_card_number),
        ("Patterns regex exportés", test_patterns_exported),
        ("NumPy version < 2.0", test_numpy_version),
        ("CONFIG exporté", test_config_exported),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 Test: {name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
        print()
    
    # Résumé
    print("=" * 60)
    print("📊 Résumé des tests")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Résultat: {passed}/{total} tests réussis ({int(passed/total*100)}%)")
    
    if passed == total:
        print("✅ Tous les tests passent - Refactoring validé!")
        return 0
    else:
        print("❌ Certains tests échouent - Vérifier le refactoring")
        return 1

if __name__ == "__main__":
    sys.exit(main())
