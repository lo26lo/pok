"""Debug complet du processus d'augmentation"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.augmentation import load_card_data, extract_card_number
from glob import glob
import os

# Charger le YAML
yaml_path = "models/cards_database.yaml"
print(f"📋 Chargement YAML: {yaml_path}")
card_dict, class_map = load_card_data(yaml_path)
print(f"✅ {len(class_map)} cartes chargées dans class_map")

# Simuler ce que fait augmentation.py
BASE_IMAGES_DIR = "images"
print(f"\n📁 Recherche images dans: {BASE_IMAGES_DIR}")

image_paths = []
image_paths += glob(os.path.join(BASE_IMAGES_DIR, "*.jpg"))
image_paths += glob(os.path.join(BASE_IMAGES_DIR, "*.png"))

print(f"✅ {len(image_paths)} images trouvées")
print(f"\n🔍 Analyse des 10 premières images:")

matched = 0
not_matched = 0

for i, path in enumerate(image_paths[:10]):
    base_name = os.path.splitext(os.path.basename(path))[0]
    card_number = extract_card_number(base_name)
    
    in_map = card_number in class_map if card_number else False
    
    print(f"\n{i+1}. Fichier: {os.path.basename(path)}")
    print(f"   Base name: {base_name}")
    print(f"   Extrait: '{card_number}'")
    print(f"   Dans class_map? {in_map}")
    
    if in_map:
        class_id = class_map[card_number] - 1  # YOLO: première classe devient 0
        print(f"   ✅ Class ID: {class_id}")
        matched += 1
    else:
        print(f"   ❌ Ignoré (card_number={card_number}, in_map={in_map})")
        if card_number:
            # Chercher clés similaires
            similar = [k for k in list(class_map.keys())[:20] if card_number.lower() in k.lower() or k.lower() in card_number.lower()]
            if similar:
                print(f"   💡 Clés similaires: {similar[:5]}")
        not_matched += 1

print(f"\n📊 Résumé (sur 10 premières images):")
print(f"   ✅ Matchées: {matched}")
print(f"   ❌ Non matchées: {not_matched}")

# Test complet
print(f"\n🔄 Test sur TOUTES les images...")
total_matched = 0
total_not_matched = 0
not_matched_samples = []

for path in image_paths:
    base_name = os.path.splitext(os.path.basename(path))[0]
    card_number = extract_card_number(base_name)
    
    if card_number is None or card_number not in class_map:
        total_not_matched += 1
        if len(not_matched_samples) < 5:
            not_matched_samples.append((base_name, card_number))
    else:
        total_matched += 1

print(f"\n📊 RÉSULTAT FINAL:")
print(f"   Total images: {len(image_paths)}")
print(f"   ✅ Matchées: {total_matched}")
print(f"   ❌ Non matchées: {total_not_matched}")

if not_matched_samples:
    print(f"\n❌ Exemples non matchés:")
    for base_name, card_num in not_matched_samples:
        print(f"   • {base_name} → extrait: '{card_num}'")
