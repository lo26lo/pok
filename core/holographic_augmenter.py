#!/usr/bin/env python3
"""
Module d'augmentation holographique pour cartes Pokémon brillantes
Simule les effets visuels des cartes holographiques (rainbow, glare, texture)
"""
import cv2
import numpy as np
import random

# Import safe_print - gère import relatif ET absolu
try:
    from .utils import safe_print
except ImportError:
    # Exécution directe du script
    from utils import safe_print


class HolographicAugmenter:
    """Ajoute des effets holographiques réalistes aux cartes"""
    
    def __init__(self):
        self.rainbow_colors = [
            (148, 0, 211),    # Violet
            (75, 0, 130),     # Indigo
            (0, 0, 255),      # Bleu
            (0, 255, 0),      # Vert
            (255, 255, 0),    # Jaune
            (255, 127, 0),    # Orange
            (255, 0, 0)       # Rouge
        ]
    
    def create_rainbow_gradient(self, width, height, angle=45, intensity=0.3):
        """
        Crée un overlay arc-en-ciel
        
        Args:
            width: Largeur de l'image
            height: Hauteur de l'image
            angle: Angle du gradient (en degrés)
            intensity: Intensité de l'effet (0-1)
        
        Returns:
            Image RGB avec gradient arc-en-ciel
        """
        # Créer une image vide
        rainbow = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Angle en radians
        angle_rad = np.deg2rad(angle)
        
        # Créer le gradient
        for i in range(height):
            for j in range(width):
                # Position relative selon l'angle
                pos = (j * np.cos(angle_rad) + i * np.sin(angle_rad))
                pos = pos / (width * np.cos(angle_rad) + height * np.sin(angle_rad))
                
                # Mapper à la couleur
                color_idx = int(pos * (len(self.rainbow_colors) - 1))
                color_idx = max(0, min(color_idx, len(self.rainbow_colors) - 1))
                
                # Interpolation entre deux couleurs
                next_idx = min(color_idx + 1, len(self.rainbow_colors) - 1)
                t = (pos * (len(self.rainbow_colors) - 1)) - color_idx
                
                color1 = np.array(self.rainbow_colors[color_idx])
                color2 = np.array(self.rainbow_colors[next_idx])
                
                rainbow[i, j] = color1 * (1 - t) + color2 * t
        
        # Appliquer l'intensité
        rainbow = (rainbow * intensity).astype(np.uint8)
        
        return rainbow
    
    def add_dynamic_glare(self, image, num_glares=3, intensity=0.5):
        """
        Ajoute des reflets dynamiques (glare)
        
        Args:
            image: Image source
            num_glares: Nombre de reflets
            intensity: Intensité des reflets
        
        Returns:
            Image avec reflets
        """
        h, w = image.shape[:2]
        glare = np.zeros((h, w), dtype=np.float32)
        
        for _ in range(num_glares):
            # Position aléatoire
            cx = random.randint(0, w)
            cy = random.randint(0, h)
            
            # Taille aléatoire
            radius = random.randint(50, 150)
            
            # Créer un gradient radial
            for i in range(h):
                for j in range(w):
                    dist = np.sqrt((j - cx)**2 + (i - cy)**2)
                    if dist < radius:
                        glare[i, j] = max(glare[i, j], 
                                         (1 - dist / radius) * intensity)
        
        # Appliquer le glare
        glare_3ch = cv2.cvtColor((glare * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        result = cv2.addWeighted(image, 1.0, glare_3ch, 0.5, 0)
        
        return result
    
    def add_holographic_pattern(self, image, pattern_type='lines', intensity=0.2):
        """
        Ajoute une texture holographique
        
        Args:
            image: Image source
            pattern_type: Type de motif ('lines', 'dots', 'waves')
            intensity: Intensité du motif
        
        Returns:
            Image avec texture holographique
        """
        h, w = image.shape[:2]
        pattern = np.zeros((h, w), dtype=np.float32)
        
        if pattern_type == 'lines':
            # Lignes diagonales
            for i in range(h):
                for j in range(w):
                    if (i + j) % 10 < 3:
                        pattern[i, j] = intensity
        
        elif pattern_type == 'dots':
            # Points hexagonaux
            for i in range(0, h, 15):
                for j in range(0, w, 15):
                    offset = (i // 15) % 2 * 7
                    cv2.circle(pattern, (j + offset, i), 3, intensity, -1)
        
        elif pattern_type == 'waves':
            # Ondes
            for i in range(h):
                for j in range(w):
                    wave = np.sin((i + j) / 10.0) * intensity
                    pattern[i, j] = max(0, wave)
        
        # Appliquer le pattern
        pattern_3ch = cv2.cvtColor((pattern * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        result = cv2.addWeighted(image, 1.0, pattern_3ch, 0.3, 0)
        
        return result
    
    def add_chromatic_aberration(self, image, strength=5):
        """
        Ajoute une aberration chromatique (effet prisme)
        
        Args:
            image: Image source
            strength: Force de l'aberration
        
        Returns:
            Image avec aberration chromatique
        """
        h, w = image.shape[:2]
        
        # Séparer les canaux
        b, g, r = cv2.split(image)
        
        # Décaler légèrement chaque canal
        M_red = np.float32([[1, 0, strength], [0, 1, 0]])
        M_blue = np.float32([[1, 0, -strength], [0, 1, 0]])
        
        r_shifted = cv2.warpAffine(r, M_red, (w, h))
        b_shifted = cv2.warpAffine(b, M_blue, (w, h))
        
        # Recombiner
        result = cv2.merge([b_shifted, g, r_shifted])
        
        return result
    
    def apply_holographic_effect(self, image, intensity='medium'):
        """
        Applique un effet holographique complet
        
        Args:
            image: Image source
            intensity: 'light', 'medium', 'heavy'
        
        Returns:
            Image avec effet holographique
        """
        if intensity == 'light':
            rainbow_intensity = 0.15
            glare_intensity = 0.3
            glare_count = 1
            pattern_intensity = 0.1
            aberration = 2
        elif intensity == 'heavy':
            rainbow_intensity = 0.5
            glare_intensity = 0.7
            glare_count = 5
            pattern_intensity = 0.3
            aberration = 8
        else:  # medium
            rainbow_intensity = 0.3
            glare_intensity = 0.5
            glare_count = 3
            pattern_intensity = 0.2
            aberration = 5
        
        h, w = image.shape[:2]
        
        # 1. Arc-en-ciel
        rainbow_angle = random.randint(0, 180)
        rainbow = self.create_rainbow_gradient(w, h, rainbow_angle, rainbow_intensity)
        result = cv2.addWeighted(image, 1.0, rainbow, 0.4, 0)
        
        # 2. Reflets
        result = self.add_dynamic_glare(result, glare_count, glare_intensity)
        
        # 3. Texture
        pattern_type = random.choice(['lines', 'dots', 'waves'])
        result = self.add_holographic_pattern(result, pattern_type, pattern_intensity)
        
        # 4. Aberration chromatique
        if random.random() > 0.5:
            result = self.add_chromatic_aberration(result, aberration)
        
        # 5. Saturation légèrement augmentée
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255).astype(np.uint8)
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return result
    
    def augment_directory(self, input_dir, output_dir, num_variations=3):
        """
        Applique l'effet holographique à toutes les images d'un dossier
        
        Args:
            input_dir: Dossier source
            output_dir: Dossier destination
            num_variations: Nombre de variations par image
        """
        import os
        from pathlib import Path
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        image_files = list(input_path.glob("*.png")) + \
                      list(input_path.glob("*.jpg")) + \
                      list(input_path.glob("*.jpeg"))
        
        safe_print(f"🌈 Génération d'effets holographiques sur {len(image_files)} images...")
        
        for idx, img_path in enumerate(image_files, 1):
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            for var in range(num_variations):
                intensity = random.choice(['light', 'medium', 'heavy'])
                img_holo = self.apply_holographic_effect(img, intensity)
                
                # Sauvegarder
                output_name = f"{img_path.stem}_holo{var+1}{img_path.suffix}"
                output_file = output_path / output_name
                cv2.imwrite(str(output_file), img_holo)
            
            if idx % 10 == 0:
                safe_print(f"   Progression: {idx}/{len(image_files)}")
        
        safe_print(f"✅ {len(image_files) * num_variations} images holographiques générées!")


def main():
    """Fonction de test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Augmentation holographique")
    parser.add_argument("input", help="Dossier d'entrée ou fichier image")
    parser.add_argument("output", help="Dossier de sortie")
    parser.add_argument("--variations", type=int, default=3, 
                        help="Nombre de variations par image")
    args = parser.parse_args()
    
    augmenter = HolographicAugmenter()
    
    from pathlib import Path
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Traiter un seul fichier
        img = cv2.imread(str(input_path))
        img_holo = augmenter.apply_holographic_effect(img, 'medium')
        cv2.imwrite(args.output, img_holo)
        safe_print(f"✅ Image holographique générée: {args.output}")
    else:
        # Traiter un dossier
        augmenter.augment_directory(args.input, args.output, args.variations)


if __name__ == "__main__":
    main()
