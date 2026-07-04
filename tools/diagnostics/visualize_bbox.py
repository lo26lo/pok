import cv2
import os
from pathlib import Path
import random

def draw_yolo_bbox(image, label_path, output_path):
    """Dessine les bounding boxes YOLO sur une image"""
    if not os.path.exists(label_path):
        print(f"⚠️  Pas de label pour {label_path}")
        return False
    
    img = image.copy()
    height, width = img.shape[:2]
    
    # Lire les annotations YOLO
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # Dessiner chaque bbox
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        
        class_id, cx, cy, w, h = parts
        cx, cy, w, h = map(float, [cx, cy, w, h])
        
        # Convertir YOLO (normalisé) en pixels
        x1 = int((cx - w/2) * width)
        y1 = int((cy - h/2) * height)
        x2 = int((cx + w/2) * width)
        y2 = int((cy + h/2) * height)
        
        # Dessiner le rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"Class {class_id}", (x1, y1-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Sauvegarder
    cv2.imwrite(str(output_path), img)
    return True

# Créer le dossier de sortie
output_dir = Path("bbox_visualization")
output_dir.mkdir(exist_ok=True)

img_dir = Path("output/yolov8/images")
label_dir = Path("output/yolov8/labels")

# Trouver des paires image originale + image flippée
print("🔍 Recherche d'images originales et flippées...")

balanced_images = [f for f in img_dir.glob("*_bal*.png") if f.is_file()]
print(f"   {len(balanced_images)} images balancées trouvées")

# Prendre 5 exemples aléatoires
samples = random.sample(balanced_images, min(5, len(balanced_images)))

print(f"\n📊 Visualisation de {len(samples)} images avec bounding boxes...\n")

for img_path in samples:
    img = cv2.imread(str(img_path))
    if img is None:
        print(f"❌ {img_path.name} - corrompue")
        continue
    
    label_path = label_dir / img_path.name.replace('.png', '.txt')
    output_path = output_dir / f"bbox_{img_path.name}"
    
    if draw_yolo_bbox(img, label_path, output_path):
        print(f"✅ {img_path.name} → {output_path}")
    else:
        print(f"⚠️  {img_path.name} - pas de label")

print(f"\n✅ Visualisations sauvegardées dans: {output_dir}")
print("   Ouvrez ces images pour vérifier que les bbox sont bien alignées!")
