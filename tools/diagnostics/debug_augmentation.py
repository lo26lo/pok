#!/usr/bin/env python3
"""Debug combien de cartes dans YAML vs fichiers"""
import yaml
import sys
from pathlib import Path
from glob import glob

# Charger YAML
with open('models/cards_database.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

cards_in_yaml = len(data['cards'])
print(f"✅ Cards in YAML: {cards_in_yaml}")

# Compter fichiers dans images/
images_dir = Path("images")
png_files = list(images_dir.glob("*.png"))
jpg_files = list(images_dir.glob("*.jpg"))
total_files = len(png_files) + len(jpg_files)

print(f"✅ Files in images/: {total_files} ({len(png_files)} PNG + {len(jpg_files)} JPG)")

# Voir exemples de noms
print("\n📝 Exemples de noms de fichiers:")
for f in png_files[:5]:
    print(f"   - {f.name}")

# Voir exemples de card_ids dans YAML
print("\n📝 Exemples de card_ids dans YAML:")
for i, card_id in enumerate(list(data['cards'].keys())[:5]):
    print(f"   - {card_id}")

print(f"\n⚠️  Différence: {total_files} fichiers - {cards_in_yaml} cartes = {total_files - cards_in_yaml}")
