"""
Outils autour du manifest.csv produit par le téléchargement d'images.

Extrait de GUI_v3.1_modern.py (migration Qt) pour être partagé entre les
interfaces et les scripts.
"""
import csv
from datetime import datetime
from pathlib import Path

import yaml

try:
    from .utils import PATHS
except ImportError:
    from utils import PATHS


def generate_yaml_from_manifest(manifest_path: str, set_id: str, set_name: str,
                                yaml_path: str = None) -> int:
    """
    Génère cards_database.yaml depuis le manifest.csv d'un téléchargement.

    Format du manifest: id, localId, name, file, source_url
    (ex: xyp-XY01, XY01, Chespin, images\\xyp_XY01_en.png, https://...)

    Args:
        manifest_path: Chemin vers manifest.csv
        set_id: ID du set (ex: sv08, xyp)
        set_name: Nom du set (ex: "Surging Sparks")
        yaml_path: Destination (défaut: PATHS files.cards_database_yaml)

    Returns:
        Nombre de cartes écrites dans la base
    """
    cards_from_manifest = []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            card_id = row.get('id', '')        # ex: xyp-XY01
            local_id = row.get('localId', '')  # ex: XY01
            card_name = row.get('name', 'Unknown')
            file_path = row.get('file', '')

            if card_id and file_path:
                # images\xyp_XY01_en.png → xyp_XY01
                filename = Path(file_path).stem
                internal_id = ('_'.join(filename.split('_')[:-1])
                               if '_' in filename else filename)
                cards_from_manifest.append({
                    'internal_id': internal_id,
                    'local_id': local_id,
                    'name': card_name,
                })

    today = datetime.now().strftime('%Y-%m-%d')
    cards_data = {}
    for card in cards_from_manifest:
        cards_data[card['internal_id']] = {
            'name': card['name'],
            'set': set_name,
            'set_full': f"{card['local_id']}/???",
            'type': 'Pokemon',
            'rarity': 'Common',
            'price': None,
            'price_max': None,
            'price_source': '',
            'last_updated': today,
        }

    yaml_data = {
        'metadata': {
            'version': '1.0',
            'format': 'YOLO-compatible card database',
            'last_updated': today,
            'source': f'Auto-generated from Image Download ({set_id})',
            'total_cards': len(cards_data),
            'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation',
        },
        'cards': cards_data,
    }

    if yaml_path is None:
        yaml_path = PATHS['files']['cards_database_yaml']
    yaml_path = Path(yaml_path)
    yaml_path.parent.mkdir(exist_ok=True)

    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False,
                  default_flow_style=False)

    return len(cards_data)
