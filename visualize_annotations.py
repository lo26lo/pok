#!/usr/bin/env python3
"""
Visualise les annotations YOLO sur des images du dataset
"""
import cv2
import random
from pathlib import Path
import sys

def draw_yolo_box(img, label_line, class_names=None):
    """Dessine une bounding box YOLO sur l'image"""
    h, w = img.shape[:2]
    parts = label_line.strip().split()
    
    if len(parts) < 5:
        return
    
    class_id = int(parts[0])
    x_center = float(parts[1]) * w
    y_center = float(parts[2]) * h
    box_w = float(parts[3]) * w
    box_h = float(parts[4]) * h
    
    # Calculer les coins
    x1 = int(x_center - box_w / 2)
    y1 = int(y_center - box_h / 2)
    x2 = int(x_center + box_w / 2)
    y2 = int(y_center + box_h / 2)
    
    # Couleur aléatoire basée sur class_id
    color = (
        int((class_id * 50) % 255),
        int((class_id * 100) % 255),
        int((class_id * 150) % 255)
    )
    
    # Dessiner le rectangle
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    
    # Texte
    label = f"Class {class_id}"
    if class_names and class_id < len(class_names):
        label = f"{class_names[class_id]} ({class_id})"
    
    # Background pour le texte
    (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(img, (x1, y1 - text_h - 5), (x1 + text_w, y1), color, -1)
    cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def load_class_names(data_yaml_path):
    """Charge les noms de classes depuis data.yaml"""
    import yaml
    try:
        with open(data_yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('names', [])
    except Exception as e:
        print(f"⚠️  Impossible de charger les noms de classes: {e}")
        return None

def visualize_samples(dataset_dir, num_samples=5):
    """Visualise des échantillons aléatoires du dataset"""
    dataset_path = Path(dataset_dir)
    images_dir = dataset_path / "images"
    labels_dir = dataset_path / "labels"
    data_yaml = dataset_path / "data.yaml"
    
    if not images_dir.exists():
        print(f"❌ Dossier images introuvable: {images_dir}")
        return
    
    # Charger les noms de classes
    class_names = load_class_names(data_yaml) if data_yaml.exists() else None
    
    # Obtenir toutes les images
    all_images = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
    
    if not all_images:
        print(f"❌ Aucune image trouvée dans {images_dir}")
        return
    
    print(f"\n📊 Dataset: {len(all_images)} images")
    print(f"📂 Visualisation de {min(num_samples, len(all_images))} échantillons aléatoires...\n")
    
    # Sélectionner des échantillons aléatoires
    samples = random.sample(all_images, min(num_samples, len(all_images)))
    
    output_dir = dataset_path / "visualizations"
    output_dir.mkdir(exist_ok=True)
    
    for i, img_path in enumerate(samples, 1):
        # Charger l'image
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"⚠️  Impossible de charger: {img_path.name}")
            continue
        
        # Charger les annotations
        label_path = labels_dir / f"{img_path.stem}.txt"
        
        if not label_path.exists():
            print(f"⚠️  {img_path.name} - PAS DE LABEL!")
            continue
        
        # Lire et dessiner les boxes
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            print(f"⚠️  {img_path.name} - LABEL VIDE!")
            continue
        
        for line in lines:
            draw_yolo_box(img, line, class_names)
        
        # Sauvegarder
        output_path = output_dir / f"annotated_{img_path.name}"
        cv2.imwrite(str(output_path), img)
        
        print(f"✅ [{i}/{len(samples)}] {img_path.name}")
        print(f"   - {len(lines)} annotation(s)")
        print(f"   - Sauvegardé: {output_path}")
        print()
    
    print(f"🎨 Visualisations sauvegardées dans: {output_dir}/")
    print(f"\n💡 Ouvrez les images pour vérifier que les bounding boxes sont correctes!")

if __name__ == "__main__":
    dataset_dir = sys.argv[1] if len(sys.argv) > 1 else "output/dataset"
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print("="*70)
    print("🔍 VISUALISATION DES ANNOTATIONS YOLO")
    print("="*70)
    
    visualize_samples(dataset_dir, num_samples)
