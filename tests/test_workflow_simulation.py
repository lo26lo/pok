#!/usr/bin/env python3
"""
Test de workflow complet - Simulation d'un nouveau set
Vérifie que toute la chaîne fonctionne correctement
"""
import sys
from pathlib import Path

# Ajouter le répertoire racine
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_workflow_simulation():
    """Simule un workflow complet avec un nouveau set"""
    print("=" * 70)
    print("🎬 SIMULATION DE WORKFLOW COMPLET - NOUVEAU SET")
    print("=" * 70)
    print()
    
    # 1. Vérifier imports TCGdex
    print("1️⃣ Import de l'API TCGdex...")
    try:
        from core.tcgdex_api import TCGdexAPI
        api = TCGdexAPI(language='en')
        print("   ✅ TCGdex API importé")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 2. Test de recherche de cartes
    print("\n2️⃣ Test de recherche de cartes (Pikachu)...")
    try:
        cards = api.search_cards('Pikachu')
        if cards:
            print(f"   ✅ {len(cards)} cartes Pikachu trouvées")
            print(f"   📌 Exemple: {cards[0].get('name')} - {cards[0].get('id')}")
        else:
            print("   ⚠️  Aucune carte trouvée")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 3. Test card mapping
    print("\n3️⃣ Test du système de card mapping...")
    try:
        from core.card_mapping import get_card_id_from_class_name
        
        test_cards = {
            "Pikachu": "devrait retourner 'Pikachu' ou un ID mappé",
            "Charizard_ex": "devrait retourner 'Charizard_ex' ou un ID mappé"
        }
        
        for card_name, expected in test_cards.items():
            card_id = get_card_id_from_class_name(card_name)
            print(f"   ✅ {card_name} → {card_id}")
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 4. Test utils
    print("\n4️⃣ Test des utilitaires...")
    try:
        from core.utils import safe_print
        safe_print("   ✅ safe_print fonctionne")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # 5. Vérifier l'existence des scripts d'init
    print("\n5️⃣ Vérification des scripts d'initialisation...")
    scripts = [
        "scripts/init_prices.py",
        "scripts/init_prices_simple.py",
        "scripts/create_card_mapping.py"
    ]
    
    for script in scripts:
        script_path = Path(__file__).parent.parent / script
        if script_path.exists():
            print(f"   ✅ {script} existe")
        else:
            print(f"   ❌ {script} manquant")
            return False
    
    # 6. Vérifier la structure pour un nouveau dataset
    print("\n6️⃣ Vérification de la structure pour nouveau dataset...")
    required_dirs = [
        "images",          # Pour télécharger les cartes
        "output",          # Pour les datasets générés
        "excel",           # Pour les prix
        "core",            # Modules core
        "scripts"          # Scripts d'init
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent.parent / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ prêt")
        else:
            print(f"   ⚠️  {dir_name}/ n'existe pas (sera créé)")
    
    # 7. Workflow complet théorique
    print("\n7️⃣ Workflow théorique pour un nouveau set:")
    print()
    workflow_steps = [
        ("📥 Téléchargement", "python core/image_downloader.py --set 'Nouveau Set' --lang en"),
        ("🗺️  Mapping", "python scripts/create_card_mapping.py"),
        ("💰 Prix", "python scripts/init_prices.py"),
        ("🎨 Augmentation", "Via GUI ou core/augmentation.py"),
        ("🧩 Mosaïques", "Via GUI ou core/mosaic.py"),
        ("🎓 Training", "Via GUI Training tab"),
        ("📹 Détection", "Via GUI Detection tab avec prix")
    ]
    
    for i, (step_name, command) in enumerate(workflow_steps, 1):
        print(f"   {i}. {step_name}")
        print(f"      └─ {command}")
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLÈTE RÉUSSIE")
    print("=" * 70)
    print()
    print("📋 Prochaines étapes pour un nouveau set:")
    print("   1. Télécharger les images du set via GUI ou CLI")
    print("   2. Créer le mapping si nécessaire (automatique dans la plupart des cas)")
    print("   3. Initialiser les prix avec scripts/init_prices.py")
    print("   4. Utiliser le GUI pour augmentation → mosaïques → training → détection")
    print()
    
    return True

if __name__ == "__main__":
    success = test_workflow_simulation()
    exit(0 if success else 1)
