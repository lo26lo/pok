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
    Met à jour cards_database.yaml depuis le manifest.csv d'un téléchargement.

    FUSION, pas écrasement : les cartes déjà présentes dans la base (autres
    sets, ou même set retéléchargé) sont conservées avec leurs prix et
    métadonnées ; les nouvelles cartes sont ajoutées EN FIN de base, ce qui
    préserve les class_id YOLO existants (dérivés de l'ordre de déclaration
    par core.utils.load_card_data).

    Format du manifest: id, localId, name, file, source_url
    (ex: xyp-XY01, XY01, Chespin, images\\xyp_XY01_en.png, https://...)

    Args:
        manifest_path: Chemin vers manifest.csv
        set_id: ID du set (ex: sv08, xyp)
        set_name: Nom du set (ex: "Surging Sparks")
        yaml_path: Destination (défaut: PATHS files.cards_database_yaml)

    Returns:
        Nombre total de cartes dans la base après fusion
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

    if yaml_path is None:
        yaml_path = PATHS['files']['cards_database_yaml']
    yaml_path = Path(yaml_path)

    # Charger la base existante pour fusionner (l'ordre des clés = class_id)
    existing_cards = {}
    existing_meta = {}
    if yaml_path.exists():
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                existing = yaml.safe_load(f) or {}
            existing_cards = existing.get('cards') or {}
            existing_meta = existing.get('metadata') or {}
        except Exception:
            # Base illisible : on repart de zéro plutôt que de planter,
            # mais sans toucher au fichier tant que le parsing du manifest
            # n'a pas abouti
            existing_cards = {}

    today = datetime.now().strftime('%Y-%m-%d')
    cards_data = dict(existing_cards)
    for card in cards_from_manifest:
        internal_id = card['internal_id']
        if internal_id in cards_data:
            # Carte déjà connue : rafraîchir le nom/set, GARDER prix et
            # métadonnées existants (position inchangée → class_id stable)
            entry = cards_data[internal_id]
            entry['name'] = card['name']
            entry.setdefault('set', set_name)
            entry['last_updated'] = today
        else:
            cards_data[internal_id] = {
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

    sources = existing_meta.get('source', '')
    if set_id not in sources:
        sources = f"{sources} + {set_id}" if sources else \
            f"Auto-generated from Image Download ({set_id})"
    yaml_data = {
        'metadata': {
            'version': '1.0',
            'format': 'YOLO-compatible card database',
            'last_updated': today,
            'source': sources,
            'total_cards': len(cards_data),
            'comment': 'Bounding boxes are generated dynamically during mosaic/augmentation',
        },
        'cards': cards_data,
    }

    yaml_path.parent.mkdir(parents=True, exist_ok=True)

    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False,
                  default_flow_style=False)

    return len(cards_data)
