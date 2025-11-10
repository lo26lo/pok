import os
from pathlib import Path
import re

# Mapping des cartes vers les class IDs
CARD_TO_CLASS = {
    '019': 0,
    '020': 1,
    '026': 2,
    '046': 3,
    '051': 4,
    '126': 5,
    '132': 6,
    '152': 7
}

images_dir = Path('output/yolov8_test/images')
labels_dir = Path('output/yolov8_test/labels')

# Pattern pour extraire le numéro de carte
pattern = re.compile(r'sv08_(\d{3})_')

count = 0
for img_path in images_dir.glob('*.png'):
    # Extraire le numéro de carte
    match = pattern.search(img_path.name)
    if not match:
        print(f"⚠️  Impossible d'extraire le numéro: {img_path.name}")
        continue
    
    card_num = match.group(1)
    
    if card_num not in CARD_TO_CLASS:
        print(f"⚠️  Carte inconnue: {card_num}")
        continue
    
    class_id = CARD_TO_CLASS[card_num]
    
    # Créer le label YOLO (carte centrée, pleine image)
    # Format: class_id center_x center_y width height (normalisé 0-1)
    label_content = f"{class_id} 0.5 0.5 0.9 0.9\n"
    
    # Sauvegarder le label
    label_path = labels_dir / img_path.name.replace('.png', '.txt')
    with open(label_path, 'w') as f:
        f.write(label_content)
    
    count += 1

print(f"\n✅ {count} labels YOLO créés!")
print(f"📊 8 classes: {list(CARD_TO_CLASS.values())}")
