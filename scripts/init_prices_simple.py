"""
Script simplifié pour créer le YAML avec les 8 cartes d'entraînement + prix
Format: models/cards_database.yaml
"""

import yaml
from pathlib import Path
from datetime import datetime
import sys
sys.path.append('.')

from core.tcgdex_api import TCGdexAPI

# Définir manuellement les 8 cartes d'entraînement
TRAINING_CARDS = {
    'sv08_019': {'name': 'Exeggcute', 'set': 'Surging Sparks', 'number': '019'},
    'sv08_020': {'name': 'Exeggutor', 'set': 'Surging Sparks', 'number': '020'},
    'sv08_026': {'name': 'Scovillain ex', 'set': 'Surging Sparks', 'number': '026'},
    'sv08_046': {'name': 'Milotic ex', 'set': 'Surging Sparks', 'number': '046'},
    'sv08_051': {'name': 'Black Kyurem ex', 'set': 'Surging Sparks', 'number': '051'},
    'sv08_126': {'name': 'Archaludon ex', 'set': 'Surging Sparks', 'number': '126'},
    'sv08_132': {'name': 'Alolan Exeggutor ex', 'set': 'Surging Sparks', 'number': '132'},
    'sv08_152': {'name': 'Cyrano', 'set': 'Surging Sparks', 'number': '152'},
}

def init_yaml_with_prices():
    """Initialise le YAML avec les 8 cartes d'entraînement + prix"""
    
    print("📋 Cartes à ajouter:")
    for card_id, info in TRAINING_CARDS.items():
        print(f"   • {card_id}: {info['name']}")
    
    # Créer structure YAML
    yaml_data = {
        'metadata': {
            'version': '1.0',
            'format': 'YOLO-compatible card database',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source': 'Training set (8 cards)',
            'total_cards': len(TRAINING_CARDS),
            'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation'
        },
        'cards': {}
    }
    
    # Ajouter cartes
    for card_id, info in TRAINING_CARDS.items():
        yaml_data['cards'][card_id] = {
            'name': info['name'],
            'set': info['set'],
            'set_full': f"{info['number']}/191",
            'type': 'Pokemon',
            'rarity': 'Common',
            'price': None,
            'price_max': None,
            'price_source': '',
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    # Sauvegarder YAML
    yaml_path = Path("models/cards_database.yaml")
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
    
    for idx, (card_id, info) in enumerate(TRAINING_CARDS.items(), 1):
        print(f"[{idx}/{len(TRAINING_CARDS)}] {card_id} ({info['name']})...", end=' ')
        
        try:
            # Recherche par set + numéro
            price, price_max, details = api.search_card_with_prices(
                card_name=info['name'],
                set_name=info['set'],
                card_number=info['number']
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
    
    # Mettre à jour métadonnées
    yaml_data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Sauvegarder avec prix
    print(f"\n💾 Sauvegarde des prix...")
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    
    print(f"\n✅ Terminé!")
    print(f"   📊 {success_count}/{len(TRAINING_CARDS)} cartes avec prix")
    print(f"   💾 Fichier: {yaml_path}")
    print(f"\n💡 Tu peux maintenant utiliser la détection avec prix!")

if __name__ == "__main__":
    print("=" * 60)
    print("  INITIALISATION YAML - 8 CARTES D'ENTRAÎNEMENT")
    print("=" * 60)
    print()
    
    try:
        init_yaml_with_prices()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
