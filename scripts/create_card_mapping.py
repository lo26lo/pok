#!/usr/bin/env python3
"""
Génère models/card_name_to_id.json depuis models/cards_database.yaml

Ce mapping (nom de classe YOLO → card_id) est utilisé par core/card_mapping.py
pour retrouver le prix d'une carte détectée : les data.yaml YOLO contiennent le
nom de la carte (ex: "Xerneas"), la base de prix est indexée par card_id
(ex: "xyp_XY05").

Les noms de classes sont dérivés comme dans core.utils.load_card_data :
nom de la carte avec les espaces remplacés par des underscores.

Usage:
    python scripts/create_card_mapping.py
"""
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_paths():
    config_path = PROJECT_ROOT / "config" / "paths.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_card_mapping():
    paths = load_paths()
    yaml_path = PROJECT_ROOT / paths['files']['cards_database_yaml']
    output_path = PROJECT_ROOT / paths['files']['card_name_to_id_json']

    if not yaml_path.exists():
        print(f"❌ Base de cartes non trouvée: {yaml_path}")
        print("   Créez-la d'abord avec scripts/init_prices.py")
        return 1

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    cards = (data or {}).get('cards', {})
    if not cards:
        print(f"❌ Aucune carte dans {yaml_path}")
        return 1

    mapping = {}
    collisions = []
    for card_id, card_info in cards.items():
        class_name = str(card_info.get('name', '')).replace(' ', '_')
        if not class_name:
            continue
        if class_name in mapping and mapping[class_name] != card_id:
            # Deux cartes portent le même nom: on garde la première (ordre YAML,
            # cohérent avec load_card_data) et on signale la collision
            collisions.append((class_name, mapping[class_name], card_id))
            continue
        mapping[class_name] = card_id

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"✅ {output_path} généré: {len(mapping)} cartes mappées")
    if collisions:
        print(f"⚠️  {len(collisions)} nom(s) en double (première occurrence conservée):")
        for name, kept, skipped in collisions[:10]:
            print(f"   • {name}: {kept} conservé, {skipped} ignoré")
        if len(collisions) > 10:
            print(f"   ... et {len(collisions) - 10} autres")
    return 0


if __name__ == "__main__":
    sys.exit(create_card_mapping())
