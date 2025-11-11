#!/usr/bin/env python3
"""
Script de visualisation des bounding boxes sur une mosaïque
Charge une image de mosaïque et son label YOLO, puis dessine les bbox avec noms de cartes
"""
import cv2
import numpy as np
from pathlib import Path
import sys
import random
import yaml

def load_card_names(yaml_path: Path = Path("models/cards_database.yaml")) -> dict:
    """
    Charge les noms de cartes depuis cards_database.yaml
    
    Returns:
        {card_id: card_name}
    """
    if not yaml_path.exists():
        print(f"⚠️  {yaml_path} introuvable, utilisation des class_id")
        return {}
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Structure: {metadata: ..., cards: {card_id: {name: ..., ...}}}
    cards_data = data.get('cards', {})
    
    card_names = {}
    for card_id, card_info in cards_data.items():
        card_names[card_id] = card_info.get('name', card_id)
    
    return card_names


def load_class_mapping(dataset_yaml_path: Path = Path("output/augmented/data.yaml")) -> dict:
    """
    Charge le mapping class_id -> card_id depuis data.yaml
    
    Returns:
        {class_id: card_id}
    """
    if not dataset_yaml_path.exists():
        print(f"⚠️  {dataset_yaml_path} introuvable")
        return {}
    
    with open(dataset_yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # data.yaml contient 'names': ['sv08_001', 'sv08_002', ...]
    # L'index est le class_id
    class_to_card = {}
    if 'names' in data:
        for class_id, card_id in enumerate(data['names']):
            class_to_card[class_id] = card_id
    
    return class_to_card


def draw_bbox_from_yolo(image: np.ndarray, label_path: Path, output_path: Path, 
                        card_names: dict, class_to_card: dict):
    """
    Dessine les bounding boxes depuis un label YOLO avec noms de cartes
    
    Args:
        image: Image numpy array
        label_path: Chemin vers le fichier .txt YOLO
        output_path: Où sauvegarder l'image annotée
        card_names: Dictionnaire {card_id: card_name}
        class_to_card: Dictionnaire {class_id: card_id}
    """
    if not label_path.exists():
        print(f"❌ Label introuvable : {label_path}")
        return
    
    height, width = image.shape[:2]
    
    # Lire les annotations YOLO
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    print(f"📦 {len(lines)} bounding boxes trouvées")
    
    # Couleurs aléatoires pour chaque classe
    colors = {}
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        
        class_id = int(parts[0])
        cx = float(parts[1])
        cy = float(parts[2])
        w = float(parts[3])
        h = float(parts[4])
        
        # Convertir YOLO (normalized) vers pixels
        cx_px = int(cx * width)
        cy_px = int(cy * height)
        w_px = int(w * width)
        h_px = int(h * height)
        
        # Calcul des coins
        x1 = cx_px - w_px // 2
        y1 = cy_px - h_px // 2
        x2 = cx_px + w_px // 2
        y2 = cy_px + h_px // 2
        
        # Couleur par classe
        if class_id not in colors:
            colors[class_id] = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255)
            )
        color = colors[class_id]
        
        # Récupérer le nom de la carte
        card_id = class_to_card.get(class_id, f"class_{class_id}")
        card_name = card_names.get(card_id, card_id)
        
        # Dessiner bbox
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        
        # Label avec fond (nom de carte)
        label_text = card_name[:30]  # Tronquer si trop long
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        
        # Rectangle de fond pour le texte
        cv2.rectangle(image, 
                     (x1, y1 - text_h - baseline - 5), 
                     (x1 + text_w + 5, y1), 
                     color, -1)
        
        # Texte en blanc
        cv2.putText(image, label_text, 
                   (x1 + 2, y1 - baseline - 2), 
                   font, font_scale, (255, 255, 255), thickness)
    
    # Sauvegarder
    cv2.imwrite(str(output_path), image)
    print(f"✅ Image annotée sauvegardée : {output_path}")
    
    return image


def main():
    """Fonction principale"""
    print("=" * 70)
    print("🎨 VISUALISATION DES BOUNDING BOXES SUR MOSAÏQUE")
    print("=" * 70)
    print()
    
    # Charger les noms de cartes
    print("📚 Chargement des noms de cartes...")
    card_names = load_card_names()
    print(f"   ✓ {len(card_names)} noms chargés")
    
    # Charger le mapping class_id -> card_id
    print("🔗 Chargement du mapping classes...")
    class_to_card = load_class_mapping()
    print(f"   ✓ {len(class_to_card)} mappings chargés")
    print()
    
    # Dossiers
    mosaics_dir = Path("output/mosaics")
    images_dir = mosaics_dir / "images"
    labels_dir = mosaics_dir / "labels"
    output_dir = Path("output/mosaic_visualization")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not images_dir.exists():
        print(f"❌ {images_dir} n'existe pas!")
        print("   Veuillez d'abord générer des mosaïques.")
        return
    
    # Trouver toutes les mosaïques
    mosaic_images = sorted(images_dir.glob("layout_*.png"))
    
    if not mosaic_images:
        print(f"❌ Aucune mosaïque trouvée dans {images_dir}")
        return
    
    print(f"📂 {len(mosaic_images)} mosaïques trouvées")
    print()
    
    # Demander quelle mosaïque visualiser (ou toutes)
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'all':
            selected = mosaic_images
            print("🎯 Traitement de TOUTES les mosaïques")
        else:
            try:
                idx = int(sys.argv[1]) - 1
                if 0 <= idx < len(mosaic_images):
                    selected = [mosaic_images[idx]]
                    print(f"🎯 Traitement de la mosaïque #{idx + 1}")
                else:
                    print(f"❌ Index invalide. Utiliser 1-{len(mosaic_images)} ou 'all'")
                    return
            except ValueError:
                print("❌ Argument invalide. Utiliser un nombre (1-n) ou 'all'")
                return
    else:
        # Par défaut, prendre la première
        selected = [mosaic_images[0]]
        print(f"🎯 Traitement de la première mosaïque (utilisez 'all' pour toutes)")
    
    print()
    
    # Traiter les mosaïques sélectionnées
    for mosaic_path in selected:
        print(f"📸 Traitement de {mosaic_path.name}...")
        
        # Charger l'image
        image = cv2.imread(str(mosaic_path))
        if image is None:
            print(f"   ❌ Impossible de charger {mosaic_path}")
            continue
        
        # Trouver le label correspondant
        label_path = labels_dir / f"{mosaic_path.stem}.txt"
        
        # Créer output path
        output_path = output_dir / f"{mosaic_path.stem}_bbox.png"
        
        # Dessiner les bbox
        annotated = draw_bbox_from_yolo(image, label_path, output_path, card_names, class_to_card)
        
        print()
    
    print("=" * 70)
    print("✅ VISUALISATION TERMINÉE")
    print("=" * 70)
    print()
    print(f"📂 Images annotées dans : {output_dir.absolute()}")
    print()
    print("💡 Usage:")
    print(f"   python {Path(__file__).name}           # Première mosaïque")
    print(f"   python {Path(__file__).name} 5         # Mosaïque #5")
    print(f"   python {Path(__file__).name} all       # Toutes les mosaïques")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
