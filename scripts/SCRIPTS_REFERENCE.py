"""
SCRIPTS_REFERENCE.py - Fichier référence centralisé pour tous les scripts
==========================================================================

Ce fichier DOIT être mis à jour à chaque ajout/modification/suppression de script.
Il sert de catalogue et permet d'exécuter n'importe quel script depuis un point central.

IMPORTANT: Lors de modifications de scripts:
1. Mettre à jour la description dans SCRIPTS_CATALOG
2. Mettre à jour les dépendances si nécessaires
3. Mettre à jour les arguments si la signature change
4. Documenter les changements dans la section CHANGELOG ci-dessous

CHANGELOG:
----------
2025-11-11: Ajout de test_utils_performance.py et test_code_profiling.py (Performance)
2025-11-10: Création du fichier référence centralisé
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Racine du projet
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
TESTS_DIR = PROJECT_ROOT / "tests"
CORE_DIR = PROJECT_ROOT / "core"

# ============================================================================
# CATALOGUE DES SCRIPTS - À MAINTENIR À JOUR
# ============================================================================

SCRIPTS_CATALOG = {
    # --- Scripts de configuration et initialisation ---
    "init_prices": {
        "path": SCRIPTS_DIR / "init_prices.py",
        "description": "Initialise les prix des cartes depuis data.yaml vers Excel",
        "category": "Configuration",
        "dependencies": ["pandas", "openpyxl", "PyYAML"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)", "workflow après téléchargement images"],
        "last_modified": "2025-11-10"
    },
    "init_prices_real": {
        "path": SCRIPTS_DIR / "init_prices_real.py",
        "description": "Initialise les prix réels depuis TCGdex API",
        "category": "Configuration",
        "dependencies": ["pandas", "openpyxl", "requests"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    "init_prices_simple": {
        "path": SCRIPTS_DIR / "init_prices_simple.py",
        "description": "Version simplifiée d'initialisation des prix",
        "category": "Configuration",
        "dependencies": ["pandas", "openpyxl"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts de mapping et données ---
    "create_card_mapping": {
        "path": SCRIPTS_DIR / "create_card_mapping.py",
        "description": "Crée le mapping entre noms de classes YOLO et IDs TCGdex",
        "category": "Data Processing",
        "dependencies": ["PyYAML"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)", "workflow après création dataset"],
        "last_modified": "2025-11-10"
    },
    "create_real_mapping": {
        "path": SCRIPTS_DIR / "create_real_mapping.py",
        "description": "Crée un mapping réel à partir des données disponibles",
        "category": "Data Processing",
        "dependencies": ["PyYAML"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    "read_excel_mapping": {
        "path": SCRIPTS_DIR / "read_excel_mapping.py",
        "description": "Lit et affiche le mapping depuis les fichiers Excel",
        "category": "Data Processing",
        "dependencies": ["pandas", "openpyxl"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts de correction et debugging ---
    "fix_class_mapping": {
        "path": SCRIPTS_DIR / "fix_class_mapping.py",
        "description": "Corrige les problèmes de mapping de classes",
        "category": "Debug",
        "dependencies": ["PyYAML"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    "fix_class_mapping_correct": {
        "path": SCRIPTS_DIR / "fix_class_mapping_correct.py",
        "description": "Version corrigée du script de mapping",
        "category": "Debug",
        "dependencies": ["PyYAML"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    "debug_excel_keys": {
        "path": SCRIPTS_DIR / "debug_excel_keys.py",
        "description": "Debug les clés dans les fichiers Excel",
        "category": "Debug",
        "dependencies": ["pandas", "openpyxl"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts de workflow et traitement ---
    "workflow_optimized": {
        "path": SCRIPTS_DIR / "workflow_optimized.py",
        "description": "Workflow optimisé pour le traitement complet",
        "category": "Workflow",
        "dependencies": ["ultralytics", "opencv-python", "numpy"],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)", "run_script.bat"],
        "last_modified": "2025-11-10"
    },
    "merge_dataset": {
        "path": SCRIPTS_DIR / "merge_dataset.py",
        "description": "Fusionne plusieurs datasets",
        "category": "Data Processing",
        "dependencies": [],
        "arguments": ["--source1", "--source2", "--output"],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts de labels et annotations ---
    "create_yolo_labels_test": {
        "path": SCRIPTS_DIR / "create_yolo_labels_test.py",
        "description": "Crée des labels YOLO de test",
        "category": "Data Processing",
        "dependencies": [],
        "arguments": [],
        "requires_venv": True,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts de migration ---
    "migrate_directories": {
        "path": SCRIPTS_DIR / "migrate_directories.py",
        "description": "Migre les répertoires vers la nouvelle structure",
        "category": "Migration",
        "dependencies": [],
        "arguments": [],
        "requires_venv": False,
        "last_modified": "2025-11-10"
    },
    
    # --- Scripts PowerShell ---
    "cleanup_project": {
        "path": SCRIPTS_DIR / "cleanup_project.ps1",
        "description": "Nettoie le projet (PowerShell)",
        "category": "Maintenance",
        "dependencies": [],
        "arguments": [],
        "requires_venv": False,
        "is_powershell": True,
        "last_modified": "2025-11-10"
    }
}

# ============================================================================
# CATALOGUE DES TESTS - À MAINTENIR À JOUR
# ============================================================================

TESTS_CATALOG = {
    "test_cuda": {
        "path": TESTS_DIR / "test_cuda.py",
        "description": "Teste la disponibilité CUDA/GPU",
        "category": "Hardware",
        "dependencies": ["torch"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat", "test_pytorch_gpu.bat"],
        "last_modified": "2025-11-10"
    },
    "test_project_integrity": {
        "path": TESTS_DIR / "test_project_integrity.py",
        "description": "Teste l'intégrité complète du projet",
        "category": "Integration",
        "dependencies": [],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_workflow_simulation": {
        "path": TESTS_DIR / "test_workflow_simulation.py",
        "description": "Simule le workflow complet",
        "category": "Integration",
        "dependencies": ["opencv-python", "requests"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_detection_prices": {
        "path": TESTS_DIR / "test_detection_prices.py",
        "description": "Teste la détection avec affichage des prix",
        "category": "Features",
        "dependencies": ["ultralytics", "opencv-python", "pandas"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat", "test_detection_with_prices.bat"],
        "last_modified": "2025-11-10"
    },
    "test_full_chain": {
        "path": TESTS_DIR / "test_full_chain.py",
        "description": "Teste la chaîne complète de traitement",
        "category": "Integration",
        "dependencies": ["ultralytics", "opencv-python"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_gpu_training": {
        "path": TESTS_DIR / "test_gpu_training.py",
        "description": "Teste l'entraînement sur GPU",
        "category": "Training",
        "dependencies": ["ultralytics", "torch"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_autobalancer_performance": {
        "path": TESTS_DIR / "test_autobalancer_performance.py",
        "description": "Teste les performances de l'auto-balancer",
        "category": "Performance",
        "dependencies": [],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_holographic_performance": {
        "path": TESTS_DIR / "test_holographic_performance.py",
        "description": "Teste les performances de l'augmentation holographique",
        "category": "Performance",
        "dependencies": ["opencv-python", "numpy"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_mosaic_performance": {
        "path": TESTS_DIR / "test_mosaic_performance.py",
        "description": "Teste les performances de génération de mosaïques",
        "category": "Performance",
        "dependencies": ["opencv-python"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_mapping_debug": {
        "path": TESTS_DIR / "test_mapping_debug.py",
        "description": "Debug le système de mapping",
        "category": "Debug",
        "dependencies": [],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "verify_data_yaml": {
        "path": TESTS_DIR / "verify_data_yaml.py",
        "description": "Vérifie la validité du fichier data.yaml",
        "category": "Validation",
        "dependencies": ["PyYAML"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "verify_detailed": {
        "path": TESTS_DIR / "verify_detailed.py",
        "description": "Vérification détaillée du dataset",
        "category": "Validation",
        "dependencies": [],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "check_corrupted_images": {
        "path": TESTS_DIR / "check_corrupted_images.py",
        "description": "Vérifie les images corrompues",
        "category": "Validation",
        "dependencies": ["opencv-python", "PIL"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_annotations": {
        "path": TESTS_DIR / "test_annotations.py",
        "description": "Teste les annotations",
        "category": "Validation",
        "dependencies": [],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "test_utils_performance": {
        "path": TESTS_DIR / "test_utils_performance.py",
        "description": "Teste les performances des fonctions utilitaires (resize, batch processing)",
        "category": "Performance",
        "dependencies": ["opencv-python", "numpy"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-11"
    },
    "test_code_profiling": {
        "path": TESTS_DIR / "test_code_profiling.py",
        "description": "Profile le code pour identifier les goulots d'étranglement",
        "category": "Performance",
        "dependencies": [],
        "requires_venv": False,
        "called_by": ["Utilisateur (manuel)"],
        "last_modified": "2025-11-11"
    },
    "visualize_annotations": {
        "path": TESTS_DIR / "visualize_annotations.py",
        "description": "Visualise les annotations sur les images",
        "category": "Visualization",
        "dependencies": ["opencv-python"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    },
    "visualize_bbox": {
        "path": TESTS_DIR / "visualize_bbox.py",
        "description": "Visualise les bounding boxes",
        "category": "Visualization",
        "dependencies": ["opencv-python"],
        "requires_venv": True,
        "called_by": ["run_test.bat", "run_all_tests.bat"],
        "last_modified": "2025-11-10"
    }
}

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_venv_python() -> Optional[Path]:
    """Retourne le chemin vers le Python du venv ou None si inexistant."""
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return venv_python
    return None

def check_venv() -> bool:
    """Vérifie si le venv existe et est activé."""
    venv_python = get_venv_python()
    if venv_python is None:
        print("❌ ERREUR: Le venv n'existe pas!")
        print("   Exécutez install_env.bat pour créer l'environnement virtuel.")
        return False
    return True

def list_all_scripts():
    """Affiche tous les scripts disponibles par catégorie."""
    print("\n" + "="*80)
    print("📁 CATALOGUE DES SCRIPTS")
    print("="*80)
    
    categories = {}
    for name, info in SCRIPTS_CATALOG.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))
    
    for cat in sorted(categories.keys()):
        print(f"\n🔹 {cat}")
        print("-" * 80)
        for name, info in sorted(categories[cat], key=lambda x: x[0]):
            status = "🐍 Python" if not info.get("is_powershell") else "⚡ PowerShell"
            venv_req = "✅ venv" if info["requires_venv"] else "❌ no venv"
            print(f"  {name:30s} | {status} | {venv_req} | {info['description']}")

def list_all_tests():
    """Affiche tous les tests disponibles par catégorie."""
    print("\n" + "="*80)
    print("🧪 CATALOGUE DES TESTS")
    print("="*80)
    
    categories = {}
    for name, info in TESTS_CATALOG.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, info))
    
    for cat in sorted(categories.keys()):
        print(f"\n🔹 {cat}")
        print("-" * 80)
        for name, info in sorted(categories[cat], key=lambda x: x[0]):
            print(f"  {name:35s} | {info['description']}")

def run_script(script_name: str, args: List[str] = None) -> int:
    """
    Exécute un script par son nom.
    
    Args:
        script_name: Nom du script (clé dans SCRIPTS_CATALOG)
        args: Arguments optionnels à passer au script
    
    Returns:
        Code de retour du script
    """
    if script_name not in SCRIPTS_CATALOG:
        print(f"❌ Script '{script_name}' inconnu!")
        print(f"   Utilisez --list pour voir les scripts disponibles.")
        return 1
    
    info = SCRIPTS_CATALOG[script_name]
    script_path = info["path"]
    
    if not script_path.exists():
        print(f"❌ Fichier introuvable: {script_path}")
        return 1
    
    # Vérifier si le venv est requis
    if info["requires_venv"]:
        if not check_venv():
            return 1
        python_exe = get_venv_python()
    else:
        python_exe = sys.executable
    
    # Construire la commande
    if info.get("is_powershell"):
        cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
    else:
        cmd = [str(python_exe), str(script_path)]
    
    if args:
        cmd.extend(args)
    
    # Afficher la commande
    print(f"\n▶️  Exécution: {' '.join(cmd)}")
    print(f"📝 Description: {info['description']}")
    print(f"📦 Dépendances: {', '.join(info['dependencies']) if info['dependencies'] else 'Aucune'}")
    if info.get("called_by"):
        print(f"🔗 Appelé par: {', '.join(info['called_by'])}")
    print("-" * 80)
    
    # Exécuter
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return 1

def run_test(test_name: str, args: List[str] = None) -> int:
    """
    Exécute un test par son nom.
    
    Args:
        test_name: Nom du test (clé dans TESTS_CATALOG)
        args: Arguments optionnels à passer au test
    
    Returns:
        Code de retour du test
    """
    if test_name not in TESTS_CATALOG:
        print(f"❌ Test '{test_name}' inconnu!")
        print(f"   Utilisez --list-tests pour voir les tests disponibles.")
        return 1
    
    info = TESTS_CATALOG[test_name]
    test_path = info["path"]
    
    if not test_path.exists():
        print(f"❌ Fichier introuvable: {test_path}")
        return 1
    
    # TOUJOURS utiliser le venv pour les tests
    if not check_venv():
        return 1
    python_exe = get_venv_python()
    
    # Construire la commande
    cmd = [str(python_exe), str(test_path)]
    if args:
        cmd.extend(args)
    
    # Afficher la commande
    print(f"\n🧪 Exécution du test: {test_name}")
    print(f"📝 Description: {info['description']}")
    print(f"📦 Dépendances: {', '.join(info['dependencies']) if info['dependencies'] else 'Aucune'}")
    if info.get("called_by"):
        print(f"🔗 Appelé par: {', '.join(info['called_by'])}")
    print(f"▶️  Commande: {' '.join(cmd)}")
    print("-" * 80)
    
    # Exécuter
    try:
        result = subprocess.run(cmd, cwd=PROJECT_ROOT)
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return 1

def run_all_tests(categories: List[str] = None) -> Dict[str, int]:
    """
    Exécute tous les tests ou seulement ceux d'une catégorie.
    
    Args:
        categories: Liste de catégories à tester (None = toutes)
    
    Returns:
        Dictionnaire {test_name: returncode}
    """
    if not check_venv():
        return {}
    
    results = {}
    tests_to_run = TESTS_CATALOG.items()
    
    if categories:
        tests_to_run = [(name, info) for name, info in tests_to_run 
                       if info["category"] in categories]
    
    print(f"\n{'='*80}")
    print(f"🧪 EXÉCUTION DE {len(tests_to_run)} TESTS")
    print(f"{'='*80}")
    
    for i, (test_name, info) in enumerate(tests_to_run, 1):
        print(f"\n[{i}/{len(tests_to_run)}] Test: {test_name}")
        returncode = run_test(test_name)
        results[test_name] = returncode
        
        if returncode == 0:
            print(f"✅ {test_name} - RÉUSSI")
        else:
            print(f"❌ {test_name} - ÉCHEC (code {returncode})")
    
    # Résumé
    print(f"\n{'='*80}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*80}")
    
    success = sum(1 for r in results.values() if r == 0)
    total = len(results)
    
    print(f"✅ Réussis: {success}/{total}")
    print(f"❌ Échoués: {total - success}/{total}")
    
    if success == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nTests échoués:")
        for test_name, code in results.items():
            if code != 0:
                print(f"  - {test_name} (code {code})")
    
    return results

# ============================================================================
# INTERFACE EN LIGNE DE COMMANDE
# ============================================================================

def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gestionnaire centralisé des scripts et tests du projet Pokémon Dataset Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  
  # Lister tous les scripts
  python SCRIPTS_REFERENCE.py --list
  
  # Lister tous les tests
  python SCRIPTS_REFERENCE.py --list-tests
  
  # Exécuter un script
  python SCRIPTS_REFERENCE.py --run init_prices
  
  # Exécuter un test
  python SCRIPTS_REFERENCE.py --test test_cuda
  
  # Exécuter tous les tests
  python SCRIPTS_REFERENCE.py --run-all-tests
  
  # Exécuter tous les tests d'une catégorie
  python SCRIPTS_REFERENCE.py --run-all-tests --category Integration
        """
    )
    
    parser.add_argument("--list", action="store_true",
                       help="Liste tous les scripts disponibles")
    parser.add_argument("--list-tests", action="store_true",
                       help="Liste tous les tests disponibles")
    parser.add_argument("--run", metavar="SCRIPT",
                       help="Exécute un script spécifique")
    parser.add_argument("--test", metavar="TEST",
                       help="Exécute un test spécifique")
    parser.add_argument("--run-all-tests", action="store_true",
                       help="Exécute tous les tests")
    parser.add_argument("--category", action="append",
                       help="Filtre par catégorie (peut être répété)")
    parser.add_argument("--check-venv", action="store_true",
                       help="Vérifie l'existence du venv")
    parser.add_argument("args", nargs="*",
                       help="Arguments à passer au script/test")
    
    args = parser.parse_args()
    
    # Actions
    if args.check_venv:
        if check_venv():
            print("✅ Le venv existe et est prêt à être utilisé.")
            venv_python = get_venv_python()
            print(f"📍 Python: {venv_python}")
            return 0
        return 1
    
    if args.list:
        list_all_scripts()
        return 0
    
    if args.list_tests:
        list_all_tests()
        return 0
    
    if args.run:
        return run_script(args.run, args.args)
    
    if args.test:
        return run_test(args.test, args.args)
    
    if args.run_all_tests:
        results = run_all_tests(args.category)
        failed = sum(1 for r in results.values() if r != 0)
        return 1 if failed > 0 else 0
    
    # Aucune action: afficher l'aide
    parser.print_help()
    return 0

if __name__ == "__main__":
    sys.exit(main())
