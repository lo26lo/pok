"""
Script pour initialiser le fichier YAML avec les cartes du dataset
Et mettre à jour les prix depuis TCGdex API
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('.')

from core.tcgdex_api import TCGdexAPI

# Charger paths depuis config
def load_paths():
    config_path = Path("config/paths.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PATHS = load_paths()

def init_yaml_with_cards():
    """Initialise le YAML avec les cartes depuis data.yaml"""
    
    # Charger data.yaml
    data_yaml = Path(PATHS['files']['dataset_data_yaml'])
    
    if not data_yaml.exists():
        print("❌ Fichier data.yaml non trouvé!")
        print(f"   Cherché dans: {data_yaml}")
        return
    
    print(f"📋 Lecture de {data_yaml}...")
    with open(data_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    names = data.get('names', [])
    
    if not names:
        print("❌ Aucune carte trouvée dans data.yaml!")
        return
    
    print(f"✅ Trouvé {len(names)} cartes:")
    for name in names:
        print(f"   • {name}")
    
    # Créer structure YAML
    yaml_data = {
        'metadata': {
            'version': '1.0',
            'format': 'YOLO-compatible card database',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Generated from data.yaml',
            'total_cards': len(names),
            'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation'
        },
        'cards': {}
    }
    
    # Ajouter chaque carte
    for card_id in names:
        yaml_data['cards'][card_id] = {
            'name': card_id.replace('_', ' ').title(),  # Nom formaté
            'set': 'Surging Sparks',  # À adapter selon besoin
            'set_full': f"{card_id.split('_')[-1]}/191" if '_' in card_id else "000/191",
            'type': 'Pokemon',
            'rarity': 'Common',
            'price': None,
            'price_max': None,
            'price_source': '',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    # Sauvegarder YAML
    yaml_path = Path(PATHS['files']['cards_database_yaml'])
    yaml_path.parent.mkdir(exist_ok=True)
    
    print(f"\n💾 Sauvegarde dans {yaml_path}...")
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print("✅ YAML créé!")
    
    # Mettre à jour les prix
    print("\n💰 Mise à jour des prix depuis TCGdex...")
    print("   (Cela peut prendre quelques secondes...)\n")
    
    # Initialiser l'API TCGdex
    api = TCGdexAPI(language='en')
    
    success_count = 0
    
    for idx, card_id in enumerate(names, 1):
        # Extraire set et number depuis l'ID
        # Format: sv08_019 = set "sv08", number "019"
        parts = card_id.split('_')
        if len(parts) >= 2:
            set_id = parts[0]  # sv08
            number = parts[1]  # 019
            
            print(f"[{idx}/{len(names)}] {card_id} (set={set_id}, num={number})...", end=' ')
            
            try:
                price, price_max, details = api.search_card_with_prices(
                    card_name="",  # On cherche par set+number
                    set_name=set_id,
                    set_hash=number
                )
                
                if price is not None:
                    yaml_data['cards'][card_id]['price'] = price
                    yaml_data['cards'][card_id]['price_max'] = price_max if price_max else price
                    yaml_data['cards'][card_id]['price_source'] = 'TCGdex'
                    print(f"✅ {price}€")
                    success_count += 1
                else:
                    print("⚠️ Prix non trouvé")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
        else:
            print(f"[{idx}/{len(names)}] {card_id} - ⚠️ Format invalide (attendu: setXX_XXX)")
    
    # Mettre à jour métadonnées
    yaml_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Sauvegarder avec prix
    print(f"\n💾 Sauvegarde des prix...")
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"\n✅ Terminé!")
    print(f"   📊 {success_count}/{len(names)} cartes avec prix")
    print(f"   💾 Fichier: {yaml_path}")
    print(f"\n💡 Tu peux maintenant utiliser la détection avec prix!")


if __name__ == "__main__":
    print("=" * 60)
    print("  INITIALISATION YAML + MISE À JOUR PRIX")
    print("=" * 60)
    print()
    
    try:
        init_yaml_with_cards()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
