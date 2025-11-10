#!/usr/bin/env python3
"""
Test d'intégrité du projet après réorganisation
Vérifie que tous les chemins et imports fonctionnent correctement
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_core_imports():
    """Test que tous les modules core peuvent être importés"""
    print("\n🧪 Test des imports core...")
    try:
        from core.augmentation import Augmenter
        from core.mosaic import MosaicGenerator
        from core.tcgdex_api import TCGdexAPI
        from core.card_mapping import get_card_id_from_class_name
        from core.detection_with_prices import PriceDetector
        from core.workflow_manager import WorkflowManager
        from core.training_manager import TrainingManager
        from core.detection_manager import DetectionManager
        from core.utils import safe_print, load_prices_from_excel
        print("   ✅ Tous les imports core OK")
        return True
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def test_directory_structure():
    """Vérifie que la nouvelle structure de dossiers existe"""
    print("\n📁 Test de la structure des dossiers...")
    required_dirs = [
        "core",
        "tests",
        "scripts",
        "docs/migration",
        "images",
        "output",
        "excel"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = Path(__file__).parent.parent / dir_path
        if full_path.exists():
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ MANQUANT")
            all_ok = False
    
    return all_ok

def test_scripts_exist():
    """Vérifie que les scripts déplacés existent"""
    print("\n📜 Test de l'existence des scripts...")
    scripts = [
        "scripts/init_prices.py",
        "scripts/init_prices_simple.py",
        "scripts/init_prices_real.py",
        "scripts/create_card_mapping.py",
        "scripts/workflow_optimized.py"
    ]
    
    all_ok = True
    for script in scripts:
        full_path = Path(__file__).parent.parent / script
        if full_path.exists():
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} MANQUANT")
            all_ok = False
    
    return all_ok

def test_tests_exist():
    """Vérifie que les tests déplacés existent"""
    print("\n🧪 Test de l'existence des tests...")
    tests = [
        "tests/test_annotations.py",
        "tests/test_detection_prices.py",
        "tests/test_full_chain.py",
        "tests/test_mapping_debug.py",
        "tests/verify_data_yaml.py",
        "tests/check_corrupted_images.py"
    ]
    
    all_ok = True
    for test in tests:
        full_path = Path(__file__).parent.parent / test
        if full_path.exists():
            print(f"   ✅ {test}")
        else:
            print(f"   ❌ {test} MANQUANT")
            all_ok = False
    
    return all_ok

def test_documentation():
    """Vérifie que la documentation existe"""
    print("\n📚 Test de la documentation...")
    docs = [
        "README.md",
        "CHANGELOG.md",
        "HELP.md",
        "docs/FEATURES.md",
        "docs/INTEGRATION_TCGDEX.md"
    ]
    
    all_ok = True
    for doc in docs:
        full_path = Path(__file__).parent.parent / doc
        if full_path.exists():
            print(f"   ✅ {doc}")
        else:
            print(f"   ❌ {doc} MANQUANT")
            all_ok = False
    
    return all_ok

def test_essential_files():
    """Vérifie que les fichiers essentiels sont présents"""
    print("\n📋 Test des fichiers essentiels...")
    files = [
        "GUI_v3.1_modern.py",
        "run_gui_v3.1.bat",
        "install_env.bat",
        "requirements.txt",
        ".gitignore",
        "card_name_to_id.json"
    ]
    
    all_ok = True
    for file in files:
        full_path = Path(__file__).parent.parent / file
        if full_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} MANQUANT")
            all_ok = False
    
    return all_ok

def test_bat_files_reference_correct_paths():
    """Vérifie que les fichiers .bat référencent les bons chemins"""
    print("\n🔧 Test des références dans les fichiers .bat...")
    
    bat_files = {
        "fix_pytorch_5070.bat": "tests/test_cuda.py",
        "test_pytorch_gpu.bat": "tests/test_cuda.py"
    }
    
    all_ok = True
    for bat_file, expected_ref in bat_files.items():
        full_path = Path(__file__).parent.parent / bat_file
        if full_path.exists():
            content = full_path.read_text()
            if expected_ref in content:
                print(f"   ✅ {bat_file} → {expected_ref}")
            else:
                print(f"   ⚠️  {bat_file} ne référence pas {expected_ref}")
                all_ok = False
        else:
            print(f"   ❌ {bat_file} n'existe pas")
            all_ok = False
    
    return all_ok

def main():
    """Exécute tous les tests d'intégrité"""
    print("=" * 70)
    print("🔍 TEST D'INTÉGRITÉ DU PROJET")
    print("=" * 70)
    
    results = []
    
    # Tests
    results.append(("Imports core", test_core_imports()))
    results.append(("Structure des dossiers", test_directory_structure()))
    results.append(("Scripts", test_scripts_exist()))
    results.append(("Tests", test_tests_exist()))
    results.append(("Documentation", test_documentation()))
    results.append(("Fichiers essentiels", test_essential_files()))
    results.append(("Références .bat", test_bat_files_reference_correct_paths()))
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    print("=" * 70)
    print(f"\n🎯 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("✅ Tous les tests sont passés ! Le projet est en bon état.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    exit(main())
