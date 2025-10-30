#!/usr/bin/env python3
"""
Script pour créer une image d'exemple montrant les annotations YOLO
Dessine les bounding boxes et labels sur une mosaïque
"""
import cv2
import os
import sys

def draw_yolo_annotations(image_path, label_path, output_path, class_names=None):
    """
    Dessine les annotations YOLO sur l'image
    """
    # Charger l'image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Impossible de charger l'image : {image_path}")
        return False
    
    h, w = img.shape[:2]
    
    # Lire les annotations
    if not os.path.exists(label_path):
        print(f"❌ Fichier d'annotation non trouvé : {label_path}")
        return False
    
    with open(label_path, 'r') as f:
        lines = f.readlines()
    
    # Couleurs pour les bounding boxes (BGR)
    colors = [
        (0, 255, 0),    # Vert
        (255, 0, 0),    # Bleu
        (0, 0, 255),    # Rouge
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Jaune
        (128, 0, 128),  # Violet
        (0, 128, 128),  # Olive
    ]
    
    print(f"📊 Traitement de {len(lines)} annotations...")
    
    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) != 5:
            continue
        
        class_id = int(parts[0])
        x_center = float(parts[1]) * w
        y_center = float(parts[2]) * h
        box_w = float(parts[3]) * w
        box_h = float(parts[4]) * h
        
        # Calculer les coins du rectangle
        x1 = int(x_center - box_w / 2)
        y1 = int(y_center - box_h / 2)
        x2 = int(x_center + box_w / 2)
        y2 = int(y_center + box_h / 2)
        
        # Choisir une couleur
        color = colors[idx % len(colors)]
        
        # Dessiner le rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        # Dessiner le label (ID de classe)
        label = f"ID:{class_id}"
        if class_names and class_id < len(class_names):
            label = f"{class_id}: {class_names[class_id][:10]}"  # Max 10 chars
        
        # Fond pour le texte
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img, (x1, y1 - text_h - 10), (x1 + text_w + 5, y1), color, -1)
        
        # Texte blanc
        cv2.putText(img, label, (x1 + 2, y1 - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Sauvegarder
    cv2.imwrite(output_path, img)
    print(f"✅ Image annotée sauvegardée : {output_path}")
    return True

def main():
    # Utiliser layout_001 comme exemple
    image_path = os.path.join("output", "yolov8", "images", "layout_001.png")
    label_path = os.path.join("output", "yolov8", "labels", "layout_001.txt")
    output_path = os.path.join("examples", "example_layout_annotated.png")
    
    if not os.path.exists(image_path):
        print(f"❌ Image non trouvée : {image_path}")
        print("⚠️ Générez d'abord des mosaïques avec mosaic.py ou via le GUI")
        return
    
    print(f"🎯 Création d'une image d'exemple avec annotations YOLO...")
    print(f"📄 Image source : {image_path}")
    print(f"📄 Annotations : {label_path}")
    
    success = draw_yolo_annotations(image_path, label_path, output_path)
    
    if success:
        print(f"\n✅ Succès !")
        print(f"📂 Fichier créé : {output_path}")
        print(f"💡 Cette image montre les bounding boxes YOLO sur une mosaïque")
    else:
        print(f"\n❌ Échec de la création de l'image annotée")

if __name__ == "__main__":
    main()
