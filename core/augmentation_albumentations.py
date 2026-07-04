#!/usr/bin/env python3
"""
Module d'augmentation de données OPTIMISÉ pour cartes Pokémon
Version Albumentations - Compatible NumPy 2.x
Performances: 30-50% plus rapide que imgaug + 25 augmentations (vs 19)

Avantages vs imgaug:
- Compatible NumPy 2.x (plus de blocage)
- 30-50% plus rapide (optimisé C++)
- Support natif bounding boxes YOLO
- Nouvelles augmentations exclusives (Shadow, SunFlare, Perspective, etc.)
- Maintenu activement (vs imgaug abandonné 2020)
"""
import os
import sys
import cv2
import numpy as np
from glob import glob
import re
import random
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from typing import List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import albumentations as A

# Import utils for paths + mapping de classes centralisé (source unique de vérité)
try:
    from .utils import (load_paths, PATHS, safe_print, load_card_data,
                        extract_card_number, build_class_names_list)
except ImportError:
    from utils import (load_paths, PATHS, safe_print, load_card_data,
                       extract_card_number, build_class_names_list)

# Détection GPU optionnelle pour resize
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        DEVICE = torch.device('cuda')
        safe_print("✅ GPU détecté pour augmentation!")
    else:
        DEVICE = torch.device('cpu')
        safe_print("ℹ️  GPU non disponible, utilisation CPU optimisé")
except ImportError:
    CUDA_AVAILABLE = False
    DEVICE = None
    safe_print("ℹ️  PyTorch non installé, utilisation CPU optimisé")

# Configuration par défaut
DEFAULT_NUM_AUG = 30
DEFAULT_SOURCE = "images"
DEFAULT_TARGET = "augmented"
TARGET_SIZE = (280, 380)

# Configuration des dossiers (from paths.json)
BASE_IMAGES_DIR = PATHS['directories']['images']
AUG_OUTPUT_DIR = PATHS['directories']['output_augmented']
AUG_IMAGES_DIR = PATHS['directories']['output_augmented_images']
AUG_LABELS_DIR = PATHS['directories']['output_augmented_labels']


class AugmentationAlbumentations:
    """
    Augmenteur de données optimisé avec Albumentations
    
    25 augmentations organisées en 6 catégories:
    - Luminosité & Contraste (5)
    - Couleurs (4)
    - Flou & Netteté (4)
    - Bruit (3)
    - Effets environnement (4)
    - Distorsions géométriques (5)
    """
    
    def __init__(self, num_workers: Optional[int] = None, use_gpu: bool = True):
        """
        Initialise l'augmenteur
        
        Args:
            num_workers: Nombre de workers (None = auto)
            use_gpu: Utiliser GPU pour resize si disponible
        """
        self.num_workers = num_workers or max(1, mp.cpu_count() - 2)
        self.use_gpu = use_gpu and CUDA_AVAILABLE
        
        # Pipeline d'augmentation Albumentations (3 à 6 transformations aléatoires)
        # SomeOf applique N transformations aléatoires parmi la liste
        transform_pool = [
            
            # ═══════════════════════════════════════════════════════════════
            # 1. LUMINOSITÉ & CONTRASTE (5 augmentations)
            # Simule différentes conditions d'éclairage
            # ═══════════════════════════════════════════════════════════════
            
            # Ajuste luminosité et contraste globaux
            A.RandomBrightnessContrast(
                brightness_limit=0.15,      # ±15% luminosité
                contrast_limit=0.15,        # ±15% contraste
                p=1.0
            ),
            
            # Correction gamma (simule exposition)
            A.RandomGamma(
                gamma_limit=(70, 130),      # 0.7x à 1.3x
                p=1.0
            ),
            
            # CLAHE - Égalisation adaptative (EXCLUSIF Albumentations)
            # Améliore le contraste local sans saturer
            A.CLAHE(
                clip_limit=2.0,
                tile_grid_size=(8, 8),
                p=1.0
            ),
            
            # Contraste linéaire (RandomContrast supprimé en Albumentations 2.x,
            # RandomBrightnessContrast avec brightness=0 est l'équivalent exact)
            A.RandomBrightnessContrast(
                brightness_limit=0.0,
                contrast_limit=0.3,         # ±30%
                p=1.0
            ),
            
            # Ajustement tons (highlights/shadows)
            A.RandomToneCurve(
                scale=0.1,
                p=1.0
            ),
            
            # ═══════════════════════════════════════════════════════════════
            # 2. COULEURS (4 augmentations)
            # Simule variations température couleur, saturation
            # ═══════════════════════════════════════════════════════════════
            
            # Décalage teinte/saturation/valeur
            A.HueSaturationValue(
                hue_shift_limit=20,         # ±20° teinte
                sat_shift_limit=25,         # ±25% saturation
                val_shift_limit=20,         # ±20% valeur
                p=1.0
            ),
            
            # Variation couleur (température, etc.)
            A.ColorJitter(
                brightness=0.1,
                contrast=0.1,
                saturation=0.15,
                hue=0.05,
                p=1.0
            ),
            
            # Décalage par canal RGB
            A.RGBShift(
                r_shift_limit=15,
                g_shift_limit=15,
                b_shift_limit=15,
                p=1.0
            ),
            
            # FancyPCA - Augmentation style AlexNet (EXCLUSIF)
            A.FancyPCA(
                alpha=0.1,
                p=1.0
            ),
            
            # ═══════════════════════════════════════════════════════════════
            # 3. FLOU & NETTETÉ (4 augmentations)
            # Simule mise au point, bougé, qualité optique
            # ═══════════════════════════════════════════════════════════════
            
            # Flou gaussien classique
            A.GaussianBlur(
                blur_limit=(3, 7),
                p=1.0
            ),
            
            # Flou de mouvement (EXCLUSIF - bougé main)
            A.MotionBlur(
                blur_limit=7,
                p=1.0
            ),
            
            # Defocus - hors focus réaliste (EXCLUSIF)
            A.Defocus(
                radius=(3, 5),
                alias_blur=(0.1, 0.3),
                p=1.0
            ),
            
            # Netteté
            A.Sharpen(
                alpha=(0.1, 0.4),
                lightness=(0.8, 1.2),
                p=1.0
            ),
            
            # ═══════════════════════════════════════════════════════════════
            # 4. BRUIT (3 augmentations)
            # Simule capteur, compression, basse lumière
            # ═══════════════════════════════════════════════════════════════
            
            # Bruit gaussien
            A.GaussNoise(
                var_limit=(10.0, 40.0),
                p=1.0
            ),
            
            # Bruit ISO réaliste (EXCLUSIF - capteur haute sensibilité)
            A.ISONoise(
                color_shift=(0.01, 0.03),
                intensity=(0.1, 0.3),
                p=1.0
            ),
            
            # Compression JPEG (artefacts)
            A.ImageCompression(
                quality_lower=60,
                quality_upper=95,
                p=1.0
            ),
            
            # ═══════════════════════════════════════════════════════════════
            # 5. EFFETS ENVIRONNEMENT (4 augmentations) - TOUS EXCLUSIFS
            # Simule conditions de prise de vue réalistes
            # ═══════════════════════════════════════════════════════════════
            
            # Ombres réalistes (EXCLUSIF - main, objets)
            A.RandomShadow(
                shadow_roi=(0, 0, 1, 1),
                num_shadows_limit=(1, 2),
                shadow_dimension=5,
                p=1.0
            ),
            
            # Reflet soleil/lumière (EXCLUSIF - éblouissement)
            A.RandomSunFlare(
                flare_roi=(0, 0, 1, 0.5),
                angle_lower=0,
                angle_upper=1,
                num_flare_circles_lower=3,
                num_flare_circles_upper=6,
                src_radius=100,
                src_color=(255, 255, 255),
                p=1.0
            ),
            
            # Brouillard léger
            A.RandomFog(
                fog_coef_lower=0.1,
                fog_coef_upper=0.3,
                alpha_coef=0.1,
                p=1.0
            ),
            
            # Réduction couleurs (posterize)
            A.Posterize(
                num_bits=5,
                p=1.0
            ),
            
            # ═══════════════════════════════════════════════════════════════
            # 6. DISTORSIONS GÉOMÉTRIQUES (5 augmentations)
            # Simule angle de vue, surface non plane, optique
            # ═══════════════════════════════════════════════════════════════
            
            # Transformation perspective (EXCLUSIF - angle de vue)
            A.Perspective(
                scale=(0.02, 0.08),
                keep_size=True,
                p=1.0
            ),
            
            # Distorsion optique (EXCLUSIF - fish-eye léger)
            A.OpticalDistortion(
                distort_limit=0.1,
                shift_limit=0.05,
                p=1.0
            ),
            
            # Distorsion en grille (EXCLUSIF - carte ondulée)
            A.GridDistortion(
                num_steps=5,
                distort_limit=0.1,
                p=1.0
            ),
            
            # Transformation élastique (légère déformation)
            A.ElasticTransform(
                alpha=15,
                sigma=3,
                p=1.0
            ),
            
            # Rotation sûre (sans perte de pixels)
            A.SafeRotate(
                limit=10,
                border_mode=cv2.BORDER_REFLECT_101,
                p=1.0
            ),
            
        ]

        # SomeOf n'accepte qu'un entier pour n (un tuple plante en 1.4+).
        # Pour appliquer "3 à 6" transformations, on pré-construit un SomeOf
        # par valeur de n et on tire n au hasard pour chaque image.
        self._n_range = (3, 6)
        self._transforms_by_n = {
            n: A.SomeOf(transform_pool, n=n, p=1.0)
            for n in range(self._n_range[0], self._n_range[1] + 1)
        }


        safe_print(f"🚀 Augmenteur Albumentations initialisé:")
        safe_print(f"   GPU: {'✅ Activé' if self.use_gpu else '❌ Désactivé'}")
        safe_print(f"   Workers: {self.num_workers} threads")
        safe_print(f"   Pipeline: 25 augmentations (6 catégories)")
        safe_print(f"   Par image: 3-6 transformations aléatoires")
    
    def resize_image_gpu(self, img: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize image avec GPU (PyTorch)"""
        if not self.use_gpu:
            return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        
        try:
            # Convertir en tensor et déplacer sur GPU
            img_tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float().to(DEVICE)
            
            # Resize avec PyTorch
            img_resized = torch.nn.functional.interpolate(
                img_tensor, 
                size=(target_size[1], target_size[0]),  # (height, width)
                mode='bilinear', 
                align_corners=False
            )
            
            # Reconvertir en numpy
            img_resized = img_resized.squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.uint8)
            return img_resized
        except Exception as e:
            # Fallback CPU si erreur GPU
            return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
    
    def process_single_image(self, img_path: str, target_size: Tuple[int, int]) -> Optional[Tuple[np.ndarray, str]]:
        """Traite une image (lecture + resize)"""
        try:
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is None:
                return None
            
            # Convertir RGBA en RGB si nécessaire
            if len(img.shape) == 3 and img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Resize (GPU ou CPU)
            img_resized = self.resize_image_gpu(img, target_size)
            return (img_resized, img_path)
        except Exception:
            return None
    
    def resize_cards_batch(self, image_paths: List[str], target_size: Tuple[int, int]) -> List[Tuple[np.ndarray, str]]:
        """Resize batch d'images en parallèle"""
        resized_images = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = executor.map(
                lambda p: self.process_single_image(p, target_size),
                image_paths
            )
            
            for result in results:
                if result is not None:
                    resized_images.append(result)
        
        return resized_images
    
    def augment_image(self, image: np.ndarray) -> np.ndarray:
        """Applique 3 à 6 augmentations aléatoires à une image"""
        # Albumentations attend RGB, OpenCV utilise BGR
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Tirer le nombre de transformations pour cette image
        n = random.randint(self._n_range[0], self._n_range[1])
        augmented = self._transforms_by_n[n](image=image_rgb)

        # Reconvertir en BGR pour OpenCV
        return cv2.cvtColor(augmented['image'], cv2.COLOR_RGB2BGR)
    
    def augment_batch(self, images_data: List[Tuple[np.ndarray, str, int]], 
                     num_aug: int, output_images_dir: str, output_labels_dir: str) -> int:
        """Augmente un batch d'images avec affichage progressif"""
        count = 0
        total_images = len(images_data)
        
        for idx, (img, path, class_id) in enumerate(images_data, 1):
            base_name = os.path.splitext(os.path.basename(path))[0]
            
            # Afficher progression
            safe_print(f"[{idx}/{total_images}] {base_name}", end=" > ")
            
            for i in range(num_aug):
                # Seed aléatoire pour variété
                random.seed(int(time.time() * 1000000) % (2**31) + i + count)
                np.random.seed(int(time.time() * 1000000) % (2**31) + i + count)
                
                # Appliquer augmentation
                aug_img = self.augment_image(img)
                
                # Sauvegarder image
                out_img_name = f"{base_name}_aug_{i:03d}.png"
                out_img_path = os.path.join(output_images_dir, out_img_name)
                cv2.imwrite(out_img_path, aug_img)
                
                # Sauvegarder label YOLO
                out_label_name = f"{base_name}_aug_{i:03d}.txt"
                out_label_path = os.path.join(output_labels_dir, out_label_name)
                annotation_line = f"{class_id} 0.5 0.5 1.0 1.0"
                with open(out_label_path, "w") as f:
                    f.write(annotation_line)
                
                count += 1
            
            # Fin de ligne après chaque carte
            safe_print(f"OK {num_aug} variations")
        
        return count
    
    def augment_directory(self, input_dir: str, output_dir: str, 
                         num_aug: int = DEFAULT_NUM_AUG,
                         card_data_path: str = None) -> int:
        """
        Augmente toutes les images d'un dossier
        
        Args:
            input_dir: Dossier source avec images
            output_dir: Dossier destination
            num_aug: Nombre d'augmentations par image
            card_data_path: Chemin vers YAML/Excel pour mapping classes
            
        Returns:
            Nombre total d'images générées
        """
        # Créer dossiers de sortie
        output_images_dir = os.path.join(output_dir, "images")
        output_labels_dir = os.path.join(output_dir, "labels")
        os.makedirs(output_images_dir, exist_ok=True)
        os.makedirs(output_labels_dir, exist_ok=True)
        
        # Charger mapping cartes
        if card_data_path is None:
            card_data_path = PATHS['files']['cards_database_yaml']
        
        card_dict, class_map = load_card_data(card_data_path)
        
        # Lister images
        image_paths = glob(os.path.join(input_dir, "*.png")) + \
                      glob(os.path.join(input_dir, "*.jpg")) + \
                      glob(os.path.join(input_dir, "*.jpeg"))
        
        if not image_paths:
            safe_print(f"❌ Aucune image trouvée dans {input_dir}")
            return 0
        
        safe_print(f"\n📂 Source: {input_dir}")
        safe_print(f"📂 Destination: {output_dir}")
        safe_print(f"🖼️  {len(image_paths)} images trouvées")
        safe_print(f"🔄 {num_aug} augmentations par image")
        safe_print(f"📊 Total attendu: {len(image_paths) * num_aug} images\n")
        
        # Resize toutes les images
        safe_print("📐 Redimensionnement des images...")
        resized_images = self.resize_cards_batch(image_paths, TARGET_SIZE)
        safe_print(f"✅ {len(resized_images)} images redimensionnées\n")
        
        # Associer class_id à chaque image
        images_data = []
        skipped = []
        for img, path in resized_images:
            filename = os.path.basename(path)
            card_number = extract_card_number(filename)

            if card_number and card_number in class_map:
                class_id = class_map[card_number]
                images_data.append((img, path, class_id))
            else:
                # Carte absente du mapping: on ignore l'image plutôt que de
                # générer un class_id arbitraire (dataset corrompu silencieusement)
                skipped.append(filename)

        if skipped:
            safe_print(f"⚠️  {len(skipped)} image(s) ignorée(s) — carte absente du mapping "
                       f"({os.path.basename(str(card_data_path))}):")
            for name in skipped[:10]:
                safe_print(f"   - {name}")
            if len(skipped) > 10:
                safe_print(f"   ... et {len(skipped) - 10} autres")

        if not images_data:
            safe_print("❌ Aucune image avec mapping de classe valide, abandon")
            return 0
        
        # Augmenter
        safe_print("🎨 Augmentation en cours...\n")
        start_time = time.time()
        
        total_generated = self.augment_batch(
            images_data, num_aug, output_images_dir, output_labels_dir
        )
        
        elapsed = time.time() - start_time

        safe_print(f"\n✅ Augmentation terminée!")
        safe_print(f"   Images générées: {total_generated}")
        safe_print(f"   Temps: {elapsed:.1f}s ({total_generated/elapsed:.1f} img/s)")

        # Écrire data.yaml (noms de classes) — requis par merge_dataset pour
        # produire un dataset final avec de vrais noms au lieu de "class_N"
        self._write_data_yaml(output_dir, card_dict, class_map)

        return total_generated

    def _write_data_yaml(self, output_dir: str, card_dict: dict, class_map: dict) -> None:
        """Écrit le data.yaml du dossier augmenté (names ordonnés par class_id)"""
        import yaml

        names = build_class_names_list(card_dict, class_map)
        data = {
            'path': str(Path(output_dir).absolute()),
            'train': 'images',
            'val': 'images',
            'nc': len(names),
            'names': names,
        }
        yaml_path = os.path.join(output_dir, "data.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        safe_print(f"📝 data.yaml écrit: {yaml_path} ({len(names)} classes)")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN - Exécution en ligne de commande
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Augmentation d'images de cartes Pokémon (Albumentations)"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=BASE_IMAGES_DIR,
        help=f"Dossier source des images (défaut: {BASE_IMAGES_DIR})"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=AUG_OUTPUT_DIR,
        help=f"Dossier destination (défaut: {AUG_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=DEFAULT_NUM_AUG,
        help=f"Nombre d'augmentations par image (défaut: {DEFAULT_NUM_AUG})"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=None,
        help="Nombre de workers (défaut: auto)"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="Désactiver l'utilisation du GPU"
    )
    
    args = parser.parse_args()
    
    safe_print("=" * 60)
    safe_print("🎴 POKEMON CARD AUGMENTATION (Albumentations)")
    safe_print("=" * 60)
    
    augmenter = AugmentationAlbumentations(
        num_workers=args.workers,
        use_gpu=not args.no_gpu
    )
    
    total = augmenter.augment_directory(
        input_dir=args.input,
        output_dir=args.output,
        num_aug=args.count
    )
    
    safe_print("\n" + "=" * 60)
    safe_print(f"🎉 TERMINÉ: {total} images augmentées générées")
    safe_print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
