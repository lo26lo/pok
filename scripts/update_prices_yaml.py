"""
Script pour mettre à jour les prix dans models/cards_database.yaml depuis TCGdex API
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

def update_prices_yaml():
    """Met à jour les prix dans le fichier YAML"""
    import yaml
    from datetime import datetime
    from core.tcgdex_api import TCGdexAPI
    
    yaml_path = Path("models/cards_database.yaml")
    
    print("=" * 70)
    print("  MISE À JOUR DES PRIX (YAML)")
    print("=" * 70)
    print()
    
    # Vérifier que le fichier YAML existe
    if not yaml_path.exists():
        print(f"❌ Fichier YAML non trouvé: {yaml_path}")
        print("   Créez d'abord le fichier avec init_prices.py")
        return False
    
    # Lire le YAML
    print(f"📖 Lecture de {yaml_path}...")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"   ✅ {len(data['cards'])} cartes trouvées")
    except Exception as e:
        print(f"   ❌ Erreur lecture YAML: {e}")
        return False
    
    print()
    
    # Initialiser l'API TCGdex
    print("🔧 Initialisation TCGdex API...")
    api = TCGdexAPI(language='en')
    print("   ✅ API prête")
    print()
    
    # Mettre à jour les prix
    print("💰 Mise à jour des prix...")
    print("   (Cela peut prendre quelques secondes...)")
    print()
    
    success_count = 0
    total = len(data['cards'])
    
    for idx, (card_id, card_info) in enumerate(data['cards'].items(), 1):
        # Extraire set et number depuis card_id (ex: sv08_019)
        parts = card_id.split('_')
        if len(parts) >= 2:
            set_id = parts[0]  # sv08
            number = parts[1]  # 019
            
            print(f"[{idx}/{total}] {card_id} ({card_info['name']})...", end=' ')
            
            try:
                # Rechercher le prix via TCGdex
                price, price_max, details = api.search_card_with_prices(
                    card_name=card_info['name'],
                    set_name=set_id,
                    set_hash=number
                )
                
                if price is not None:
                    data['cards'][card_id]['price'] = price
                    data['cards'][card_id]['price_max'] = price_max if price_max else price
                    data['cards'][card_id]['price_source'] = 'TCGdex'
                    data['cards'][card_id]['last_updated'] = datetime.now().strftime('%Y-%m-%d')
                    print(f"✅ {price}€")
                    success_count += 1
                else:
                    print("⚠️ Prix non trouvé")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
        else:
            print(f"[{idx}/{total}] {card_id} - ⚠️ Format invalide (attendu: setXX_XXX)")
    
    print()
    
    # Mettre à jour les métadonnées
    data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Sauvegarder
    print(f"💾 Sauvegarde des prix...")
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"   ✅ YAML mis à jour!")
    except Exception as e:
        print(f"   ❌ Erreur sauvegarde: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ MISE À JOUR TERMINÉE!")
    print("=" * 70)
    print()
    print(f"   📊 {success_count}/{total} cartes avec prix")
    print(f"   💾 Fichier: {yaml_path}")
    print()
    print("💡 Tu peux maintenant utiliser la détection avec prix!")
    print()
    
    return True


if __name__ == "__main__":
    print()
    
    try:
        success = update_prices_yaml()
        print()
        
        if success:
            print("🎉 Mise à jour réussie!")
        else:
            print("❌ Mise à jour échouée.")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
