"""Debug class_map pour comprendre pourquoi 0 images augmentées"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.augmentation import load_card_data, extract_card_number
import yaml

# Charger le YAML
yaml_path = "models/cards_database.yaml"
card_dict, class_map = load_card_data(yaml_path)

print(f"📊 Total cartes dans class_map: {len(class_map)}")
print(f"\n🔑 Premiers 10 IDs dans class_map:")
for i, key in enumerate(list(class_map.keys())[:10]):
    print(f"   {i+1}. '{key}' → class {class_map[key]}")

# Tester extraction sur fichiers réels
from glob import glob
image_files = glob("images/xyp_*.png")[:5]

print(f"\n📁 Test extraction sur {len(image_files)} fichiers:")
for img_path in image_files:
    filename = Path(img_path).stem  # sans extension
    extracted = extract_card_number(filename)
    in_map = extracted in class_map if extracted else False
    print(f"   {filename}")
    print(f"      → Extrait: '{extracted}'")
    print(f"      → Dans class_map? {in_map}")
    if not in_map and extracted:
        # Chercher clés similaires
        similar = [k for k in class_map.keys() if extracted in k or k in extracted]
        if similar:
            print(f"      → Clés similaires: {similar[:3]}")
