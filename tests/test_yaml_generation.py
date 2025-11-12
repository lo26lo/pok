"""Test de génération du YAML depuis manifest.csv"""
from pathlib import Path
import csv
import yaml
from datetime import datetime

manifest_path = 'c:/DATA/pok/images/manifest.csv'
cards_data = {}

# Lire manifest
with open(manifest_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Extraire les infos
        card_id = row.get('id', '')  # ex: xyp-XY01
        local_id = row.get('localId', '')  # ex: XY01
        card_name = row.get('name', 'Unknown')  # ex: Chespin
        file_path = row.get('file', '')  # ex: images\xyp_XY01_en.png
        
        if card_id and file_path:
            # Extraire nom fichier sans extension ni langue
            # Ex: images\xyp_XY01_en.png → xyp_XY01
            filename = Path(file_path).stem  # xyp_XY01_en
            internal_id = '_'.join(filename.split('_')[:-1]) if '_' in filename else filename
            
            cards_data[internal_id] = {
                'name': card_name,
                'set': 'XY Black Star Promos',
                'set_full': f"{local_id}/???",
                'type': 'Pokemon',
                'rarity': 'Common',
                'price': None,
                'price_max': None,
                'price_source': '',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }

# Créer YAML
yaml_data = {
    'metadata': {
        'version': '1.0',
        'format': 'YOLO-compatible card database',
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'source': 'Auto-generated from Image Download (xyp)',
        'total_cards': len(cards_data),
        'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation'
    },
    'cards': cards_data
}

# Sauvegarder
yaml_path = Path('c:/DATA/pok/models/cards_database.yaml')
yaml_path.parent.mkdir(exist_ok=True)

with open(yaml_path, 'w', encoding='utf-8') as f:
    yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

print(f"✅ YAML créé avec {len(cards_data)} cartes")
print(f"📋 Premiers IDs: {list(cards_data.keys())[:5]}")
