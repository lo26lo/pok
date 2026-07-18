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
import math
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


# Catégories d'augmentations (clés stables pour build_transform_pool/preview)
AUGMENTATION_CATEGORIES = ("brightness", "color", "blur", "noise",
                           "environment", "geometry")

# Paramètres de génération calibrés via la Live Preview (F06). La génération
# les lit par défaut ; les drapeaux CLI explicites restent prioritaires.
PARAMS_FILE = PATHS.get('files', {}).get('augmentation_params',
                                         'config/augmentation_params.json')


def default_generation_params() -> dict:
    """Valeurs de production historiques (aucune calibration)."""
    return {"intensity": 1.0, "n_transforms": 0,
            "categories": list(AUGMENTATION_CATEGORIES)}


def load_generation_params(path: Optional[str] = None) -> dict:
    """
    Paramètres de génération calibrés (config/augmentation_params.json),
    fusionnés avec les défauts et validés. Fichier absent ou invalide ->
    défauts historiques (best effort, ne lève jamais).
    """
    import json
    params = default_generation_params()
    path = Path(path or PARAMS_FILE)
    if not path.exists():
        return params
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        intensity = float(data.get("intensity", params["intensity"]))
        params["intensity"] = float(np.clip(intensity, 0.1, 2.0))
        n = int(data.get("n_transforms") or 0)
        params["n_transforms"] = max(0, n)
        cats = data.get("categories")
        if cats:
            valid = [c for c in cats if c in AUGMENTATION_CATEGORIES]
            if valid:
                params["categories"] = valid
        params["_source"] = str(path)
    except Exception as e:
        safe_print(f"⚠️ {path} illisible ({e}) — paramètres de production")
    return params


def save_generation_params(params: dict, path: Optional[str] = None) -> Path:
    """
    Sauvegarde les paramètres calibrés dans la Live Preview pour que la
    génération complète les utilise (GUI, workflow et CLI).
    """
    import json
    path = Path(path or PARAMS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "intensity": float(np.clip(float(params.get("intensity", 1.0)), 0.1, 2.0)),
        "n_transforms": int(params.get("n_transforms") or 0),
        "categories": list(params.get("categories")
                           or AUGMENTATION_CATEGORIES),
        "comment": "Calibré via la Live Preview (F06) — supprimez ce fichier "
                   "pour revenir aux valeurs de production historiques",
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return path


def _odd(value: float) -> int:
    """Arrondit à l'entier impair >= 3 le plus proche (kernels OpenCV)."""
    v = max(3, int(round(value)))
    return v if v % 2 == 1 else v + 1


def build_transform_pool(intensity: float = 1.0,
                         categories: Optional[List[str]] = None) -> List:
    """
    Construit le pool de 25 transformations Albumentations, groupé en
    6 catégories, avec une intensité globale réglable (F06 - preview live).

    Args:
        intensity: multiplicateur global des amplitudes (0.1 à 2.0) ;
                   1.0 reproduit EXACTEMENT le pipeline de production
        categories: sous-ensemble de AUGMENTATION_CATEGORIES à inclure
                    (None = toutes)

    Returns:
        Liste plate de transformations (à utiliser avec A.SomeOf)
    """
    i = float(np.clip(intensity, 0.1, 2.0))

    pools = {
        # 1. LUMINOSITÉ & CONTRASTE — conditions d'éclairage
        "brightness": [
            A.RandomBrightnessContrast(brightness_limit=0.15 * i,
                                       contrast_limit=0.15 * i, p=1.0),
            A.RandomGamma(gamma_limit=(int(100 - 30 * i), int(100 + 30 * i)), p=1.0),
            A.CLAHE(clip_limit=max(1.0, 2.0 * i), tile_grid_size=(8, 8), p=1.0),
            A.RandomBrightnessContrast(brightness_limit=0.0,
                                       contrast_limit=0.3 * i, p=1.0),
            A.RandomToneCurve(scale=0.1 * i, p=1.0),
        ],
        # 2. COULEURS — température, saturation
        "color": [
            A.HueSaturationValue(hue_shift_limit=int(20 * i),
                                 sat_shift_limit=int(25 * i),
                                 val_shift_limit=int(20 * i), p=1.0),
            A.ColorJitter(brightness=0.1 * i, contrast=0.1 * i,
                          saturation=0.15 * i, hue=0.05 * i, p=1.0),
            A.RGBShift(r_shift_limit=int(15 * i), g_shift_limit=int(15 * i),
                       b_shift_limit=int(15 * i), p=1.0),
            A.FancyPCA(alpha=0.1 * i, p=1.0),
        ],
        # 3. FLOU & NETTETÉ — mise au point, bougé
        "blur": [
            A.GaussianBlur(blur_limit=(3, _odd(3 + 4 * i)), p=1.0),
            A.MotionBlur(blur_limit=_odd(3 + 4 * i), p=1.0),
            A.Defocus(radius=(3, max(3, int(round(5 * i)))),
                      alias_blur=(0.1, 0.3), p=1.0),
            A.Sharpen(alpha=(0.1, min(1.0, 0.4 * i)), lightness=(0.8, 1.2), p=1.0),
        ],
        # 4. BRUIT — capteur, compression
        # ⚠️ API albumentations 2.x. Les anciens arguments 1.x (var_limit,
        # quality_lower/upper, *_lower/*_upper) sont IGNORÉS SILENCIEUSEMENT
        # par 2.x (retombée sur les défauts) — tests/test_augmentation_amplitudes.py
        # verrouille les valeurs effectives.
        "noise": [
            # var_limit 1.x = variance sur [0,255] ; std_range 2.x =
            # écart-type normalisé [0,1] : std = sqrt(var)/255. La borne
            # haute est plafonnée à la basse (2.x valide l'ordre du range)
            A.GaussNoise(std_range=(math.sqrt(10.0) / 255.0,
                                    math.sqrt(max(10.0, 40.0 * i)) / 255.0),
                         p=1.0),
            A.ISONoise(color_shift=(0.01, 0.03),
                       intensity=(0.1, max(0.1, 0.3 * i)), p=1.0),
            A.ImageCompression(quality_range=(60, 95), p=1.0),
        ],
        # 5. EFFETS ENVIRONNEMENT — prise de vue réaliste
        "environment": [
            A.RandomShadow(shadow_roi=(0, 0, 1, 1), num_shadows_limit=(1, 2),
                           shadow_dimension=5, p=1.0),
            A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), angle_range=(0, 1),
                             num_flare_circles_range=(3, 6), src_radius=100,
                             src_color=(255, 255, 255), p=1.0),
            A.RandomFog(fog_coef_range=(0.1, max(0.1, 0.3 * i)),
                        alpha_coef=0.1, p=1.0),
            A.Posterize(num_bits=5, p=1.0),
        ],
        # 6. DISTORSIONS GÉOMÉTRIQUES — angle de vue, surface
        "geometry": [
            A.Perspective(scale=(0.02, max(0.02, 0.08 * i)), keep_size=True, p=1.0),
            A.OpticalDistortion(distort_limit=0.1 * i, shift_limit=0.05, p=1.0),
            A.GridDistortion(num_steps=5, distort_limit=0.1 * i, p=1.0),
            A.ElasticTransform(alpha=15 * i, sigma=3, p=1.0),
            A.SafeRotate(limit=10 * i, border_mode=cv2.BORDER_REFLECT_101, p=1.0),
        ],
    }

    if categories is None:
        selected = list(AUGMENTATION_CATEGORIES)
    else:
        unknown = set(categories) - set(AUGMENTATION_CATEGORIES)
        if unknown:
            raise ValueError(f"Catégories inconnues: {sorted(unknown)} "
                             f"(choix: {AUGMENTATION_CATEGORIES})")
        selected = [c for c in AUGMENTATION_CATEGORIES if c in categories]
    if not selected:
        raise ValueError("Au moins une catégorie d'augmentation est requise")

    pool = []
    for cat in selected:
        pool.extend(pools[cat])
    return pool


def preview_augmentations(image: np.ndarray, count: int = 6,
                          n_transforms: Optional[int] = None,
                          intensity: float = 1.0,
                          categories: Optional[List[str]] = None,
                          seed: Optional[int] = None) -> List[np.ndarray]:
    """
    Génère `count` variantes augmentées d'une image, EN DIRECT (aucun
    sous-processus, aucune écriture disque) — cœur de la preview GUI (F06).

    Args:
        image: image BGR uint8 (l'originale n'est jamais modifiée)
        count: nombre de variantes à produire
        n_transforms: nombre de transformations par variante
                      (None = aléatoire 3-6, comme la production)
        intensity: multiplicateur global des amplitudes (0.1 à 2.0)
        categories: sous-ensemble de AUGMENTATION_CATEGORIES (None = toutes)
        seed: graine pour un rendu reproductible (None = aléatoire)

    Returns:
        Liste de `count` images BGR uint8 (mêmes dimensions que l'entrée)
    """
    pool = build_transform_pool(intensity=intensity, categories=categories)
    rng = random.Random(seed)

    results = []
    for k in range(count):
        n = n_transforms if n_transforms is not None else rng.randint(3, 6)
        n = max(1, min(int(n), len(pool)))
        transform = A.SomeOf(pool, n=n, p=1.0)
        if seed is not None:
            # Albumentations 1.x tire dans random/np.random globaux ;
            # 2.x utilise un seed par pipeline (Compose(seed=...))
            random.seed(seed + k)
            np.random.seed((seed + k) % (2 ** 32))
            try:
                transform = A.Compose([transform], seed=seed + k)
            except TypeError:
                pass  # albumentations 1.x : le seeding global suffit
        results.append(transform(image=image.copy())["image"])
    return results


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
    
    def __init__(self, num_workers: Optional[int] = None, use_gpu: bool = True,
                 intensity: float = 1.0,
                 n_transforms: Optional[int] = None,
                 categories: Optional[List[str]] = None):
        """
        Initialise l'augmenteur

        Args:
            num_workers: Nombre de workers (None = auto)
            use_gpu: Utiliser GPU pour resize si disponible
            intensity: multiplicateur global des amplitudes (0.1 à 2.0) —
                       1.0 = valeurs de production historiques
            n_transforms: transformations par image (None ou 0 = aléatoire
                          3-6, comportement historique)
            categories: sous-ensemble de AUGMENTATION_CATEGORIES
                        (None = toutes) — mêmes clés que la Live Preview F06
        """
        self.num_workers = num_workers or max(1, mp.cpu_count() - 2)
        self.use_gpu = use_gpu and CUDA_AVAILABLE
        self.intensity = float(np.clip(intensity, 0.1, 2.0))
        self.categories = (list(categories) if categories
                           else list(AUGMENTATION_CATEGORIES))

        # Pipeline d'augmentation Albumentations. Le pool est construit par
        # build_transform_pool() (partagé avec la preview live F06) ;
        # intensity=1.0 + toutes catégories = production historique
        transform_pool = build_transform_pool(intensity=self.intensity,
                                              categories=self.categories)

        # SomeOf n'accepte qu'un entier pour n (un tuple plante).
        # Pour appliquer "3 à 6" transformations, on pré-construit un SomeOf
        # par valeur de n et on tire n au hasard pour chaque image.
        # Chaque SomeOf est enveloppé dans un Compose avec bbox_params :
        # les transforms géométriques (Perspective, distorsions…)
        # transportent ainsi la bbox de la carte — les labels ne sont plus
        # systématiquement plein cadre.
        if n_transforms:
            fixed = max(1, min(int(n_transforms), len(transform_pool)))
            self._n_range = (fixed, fixed)
        else:
            self._n_range = (min(3, len(transform_pool)),
                             min(6, len(transform_pool)))
        bbox_params = A.BboxParams(format='yolo',
                                   label_fields=['class_labels'], clip=True)
        self._transforms_by_n = {
            n: A.Compose([A.SomeOf(transform_pool, n=n, p=1.0)],
                         bbox_params=bbox_params)
            for n in range(self._n_range[0], self._n_range[1] + 1)
        }

        n_lo, n_hi = self._n_range
        per_image = str(n_lo) if n_lo == n_hi else f"{n_lo}-{n_hi} (aléatoire)"
        safe_print(f"🚀 Augmenteur Albumentations initialisé:")
        safe_print(f"   GPU: {'✅ Activé' if self.use_gpu else '❌ Désactivé'}")
        safe_print(f"   Workers: {self.num_workers} threads")
        safe_print(f"   Pipeline: {len(transform_pool)} augmentations "
                   f"({len(self.categories)}/{len(AUGMENTATION_CATEGORIES)} catégories), "
                   f"intensité {self.intensity:g}x")
        safe_print(f"   Par image: {per_image} transformations")
    
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
    
    # Garde-fou bbox : sous cette aire relative, la bbox transformée est
    # considérée dégénérée et remplacée par le plein cadre. Nécessaire car
    # SafeRotate + border_mode=BORDER_REFLECT_101 casse le transport de
    # bbox dans albumentations 2.0.x (vérifié empiriquement : aire ~0.07
    # pour une carte plein cadre tournée de quelques degrés).
    _MIN_BBOX_AREA = 0.5

    def augment_with_bbox(self, image: np.ndarray,
                          class_id: int = 0) -> Tuple[np.ndarray,
                                                      Tuple[float, float, float, float]]:
        """
        Applique 3 à 6 augmentations aléatoires à une image de carte plein
        cadre et retourne (image_augmentée, bbox_yolo) — la bbox suit les
        transforms géométriques (fallback plein cadre si dégénérée).
        """
        # Albumentations attend RGB, OpenCV utilise BGR
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Tirer le nombre de transformations pour cette image
        n = random.randint(self._n_range[0], self._n_range[1])
        augmented = self._transforms_by_n[n](
            image=image_rgb,
            bboxes=[(0.5, 0.5, 1.0, 1.0)],
            class_labels=[class_id])

        bbox = (0.5, 0.5, 1.0, 1.0)
        if len(augmented['bboxes']):
            cx, cy, w, h = (float(v) for v in augmented['bboxes'][0])
            if w * h >= self._MIN_BBOX_AREA:
                bbox = (cx, cy, w, h)

        # Reconvertir en BGR pour OpenCV
        return cv2.cvtColor(augmented['image'], cv2.COLOR_RGB2BGR), bbox

    def augment_image(self, image: np.ndarray) -> np.ndarray:
        """Applique 3 à 6 augmentations aléatoires à une image"""
        return self.augment_with_bbox(image)[0]
    
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
                
                # Appliquer augmentation (la bbox suit les transforms
                # géométriques au lieu du plein cadre systématique)
                aug_img, bbox = self.augment_with_bbox(img, class_id)

                # Sauvegarder image
                out_img_name = f"{base_name}_aug_{i:03d}.png"
                out_img_path = os.path.join(output_images_dir, out_img_name)
                cv2.imwrite(out_img_path, aug_img)

                # Sauvegarder label YOLO
                out_label_name = f"{base_name}_aug_{i:03d}.txt"
                out_label_path = os.path.join(output_labels_dir, out_label_name)
                annotation_line = (f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} "
                                   f"{bbox[2]:.6f} {bbox[3]:.6f}")
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
        "--input", "-i", "--source",
        dest="input",
        type=str,
        default=BASE_IMAGES_DIR,
        help=f"Dossier source des images (défaut: {BASE_IMAGES_DIR}) "
             f"[alias: --source]"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help=f"Dossier destination (défaut: {AUG_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Nom du dossier destination SOUS output/ (interface GUI/workflow, "
             "ex: 'augmented' -> output/augmented)"
    )
    parser.add_argument(
        "--count", "-n", "--num_aug",
        dest="count",
        type=int,
        default=DEFAULT_NUM_AUG,
        help=f"Nombre d'augmentations par image (défaut: {DEFAULT_NUM_AUG}) "
             f"[alias: --num_aug]"
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
    # Paramètres du pipeline (F06) — sans drapeau explicite, la calibration
    # de la Live Preview (config/augmentation_params.json) est utilisée
    parser.add_argument(
        "--intensity",
        type=float,
        default=None,
        help="Intensité globale des transformations, 0.1-2.0 "
             "(défaut: calibration Live Preview, sinon 1.0)"
    )
    parser.add_argument(
        "--transforms",
        type=int,
        default=None,
        help="Transformations par image, 0 = aléatoire 3-6 "
             "(défaut: calibration Live Preview, sinon 0)"
    )
    parser.add_argument(
        "--categories",
        type=str,
        default=None,
        help="Catégories à inclure, séparées par des virgules "
             f"(choix: {','.join(AUGMENTATION_CATEGORIES)} ; "
             "défaut: calibration Live Preview, sinon toutes)"
    )

    args = parser.parse_args()

    # Destination : --output explicite > --target (sous output/) > défaut
    if args.output:
        output_dir = args.output
    elif args.target:
        target = args.target
        if os.path.isabs(target) or os.sep in target or '/' in target:
            output_dir = target
        else:
            output_dir = os.path.join(PATHS['directories']['output_base'], target)
    else:
        output_dir = AUG_OUTPUT_DIR

    # Paramètres du pipeline : CLI explicite > fichier calibré > défauts
    params = load_generation_params()
    source = params.pop("_source", None)
    if args.intensity is not None:
        params["intensity"] = args.intensity
        source = "CLI"
    if args.transforms is not None:
        params["n_transforms"] = args.transforms
        source = "CLI"
    if args.categories is not None:
        params["categories"] = [c.strip() for c in args.categories.split(',')
                                if c.strip()]
        source = "CLI"

    safe_print("=" * 60)
    safe_print("🎴 POKEMON CARD AUGMENTATION (Albumentations)")
    safe_print("=" * 60)
    if source:
        safe_print(f"🎛️  Paramètres du pipeline: {source}")

    augmenter = AugmentationAlbumentations(
        num_workers=args.workers,
        use_gpu=not args.no_gpu,
        intensity=params["intensity"],
        n_transforms=params["n_transforms"] or None,
        categories=params["categories"]
    )

    total = augmenter.augment_directory(
        input_dir=args.input,
        output_dir=output_dir,
        num_aug=args.count
    )
    
    safe_print("\n" + "=" * 60)
    safe_print(f"🎉 TERMINÉ: {total} images augmentées générées")
    safe_print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
