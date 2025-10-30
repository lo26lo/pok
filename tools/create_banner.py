#!/usr/bin/env python3
"""
Crée une bannière personnalisée pour le README
"""
import cv2
import numpy as np

def create_banner(output_path="examples/banner.png", width=1200, height=300):
    """
    Crée une bannière moderne pour le projet
    """
    # Créer une image avec dégradé
    banner = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Dégradé bleu foncé -> bleu clair
    for y in range(height):
        ratio = y / height
        # RGB: Bleu foncé (15, 76, 117) -> Bleu clair (0, 120, 215)
        r = int(15 + (0 - 15) * ratio)
        g = int(76 + (120 - 76) * ratio)
        b = int(117 + (215 - 117) * ratio)
        banner[y, :] = [b, g, r]  # BGR pour OpenCV
    
    # Ajouter des éléments décoratifs (lignes diagonales subtiles)
    for i in range(0, width, 100):
        pt1 = (i, 0)
        pt2 = (i + height//2, height)
        cv2.line(banner, pt1, pt2, (255, 255, 255), 1, cv2.LINE_AA)
        # Rendre les lignes très transparentes
        overlay = banner.copy()
        alpha = 0.02
        cv2.addWeighted(overlay, alpha, banner, 1 - alpha, 0, banner)
    
    # Titre principal
    title = "Pokemon Dataset Generator"
    font = cv2.FONT_HERSHEY_DUPLEX  # Police épaisse disponible
    font_scale = 2.5
    thickness = 4
    
    # Mesurer le texte pour le centrer
    (text_w, text_h), _ = cv2.getTextSize(title, font, font_scale, thickness)
    x = (width - text_w) // 2
    y = height // 2 - 20
    
    # Ombre du texte (noir)
    cv2.putText(banner, title, (x + 3, y + 3), font, font_scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    
    # Texte principal (blanc)
    cv2.putText(banner, title, (x, y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)
    
    # Sous-titre
    subtitle = "YOLO Training Dataset Generator for Pokemon Cards"
    font_sub = cv2.FONT_HERSHEY_SIMPLEX
    font_scale_sub = 0.9
    thickness_sub = 2
    
    (text_w_sub, text_h_sub), _ = cv2.getTextSize(subtitle, font_sub, font_scale_sub, thickness_sub)
    x_sub = (width - text_w_sub) // 2
    y_sub = y + 50
    
    cv2.putText(banner, subtitle, (x_sub, y_sub), font_sub, font_scale_sub, (200, 230, 255), thickness_sub, cv2.LINE_AA)
    
    # Version
    version = "v2.0"
    font_version = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(banner, version, (width - 100, height - 20), font_version, 0.8, (200, 230, 255), 2, cv2.LINE_AA)
    
    # Icônes/badges (simulés avec texte)
    badges = "✨ Augmentation  •  🧩 Mosaiques  •  📊 Annotations YOLO"
    (badge_w, badge_h), _ = cv2.getTextSize(badges, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    x_badge = (width - badge_w) // 2
    y_badge = y_sub + 50
    cv2.putText(banner, badges, (x_badge, y_badge), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 220, 255), 1, cv2.LINE_AA)
    
    # Sauvegarder
    cv2.imwrite(output_path, banner)
    print(f"✅ Bannière créée : {output_path}")
    print(f"📐 Dimensions : {width}x{height}")

if __name__ == "__main__":
    create_banner()
