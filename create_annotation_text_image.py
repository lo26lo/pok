#!/usr/bin/env python3
"""
Crée une image PNG montrant le contenu d'un fichier d'annotation YOLO
"""
import cv2
import numpy as np
import os

def create_text_image(text_content, output_path, width=800, line_height=25):
    """
    Crée une image PNG avec le texte fourni
    """
    lines = text_content.strip().split('\n')
    
    # Calculer la hauteur nécessaire
    height = len(lines) * line_height + 40
    
    # Créer une image blanche
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Fond gris clair
    cv2.rectangle(img, (0, 0), (width, height), (240, 240, 240), -1)
    
    # Titre
    cv2.putText(img, "layout_001.txt - YOLO Annotation Format", 
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Ligne de séparation
    cv2.line(img, (10, 35), (width-10, 35), (100, 100, 100), 2)
    
    # Afficher chaque ligne d'annotation
    y_offset = 60
    for idx, line in enumerate(lines):
        # Alterner les couleurs de fond
        if idx % 2 == 0:
            cv2.rectangle(img, (5, y_offset - 18), (width-5, y_offset + 5), (250, 250, 250), -1)
        
        # Colorer différemment le class_id
        parts = line.split()
        if len(parts) == 5:
            class_id = parts[0]
            coords = ' '.join(parts[1:])
            
            # Class ID en couleur
            cv2.putText(img, f"Class {class_id}:", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 0, 0), 1)
            
            # Coordonnées
            cv2.putText(img, f"  {coords}", (120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 0), 1)
        else:
            cv2.putText(img, line, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        y_offset += line_height
    
    # Note en bas
    note = "Format: class_id x_center y_center width height (normalized 0-1)"
    cv2.putText(img, note, (10, height - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 100), 1)
    
    cv2.imwrite(output_path, img)
    print(f"✅ Image de texte créée : {output_path}")

def main():
    label_path = os.path.join("output", "yolov8", "labels", "layout_001.txt")
    output_path = os.path.join("examples", "example_annotation.png")
    
    if not os.path.exists(label_path):
        print(f"❌ Fichier d'annotation non trouvé : {label_path}")
        return
    
    with open(label_path, 'r') as f:
        content = f.read()
    
    print(f"🎯 Création d'une image montrant l'annotation YOLO...")
    create_text_image(content, output_path)
    print(f"✅ Image créée : {output_path}")

if __name__ == "__main__":
    main()
