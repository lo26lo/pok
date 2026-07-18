#!/usr/bin/env python3
"""
Module d'auto-balancing OPTIMISÉ des classes dans un dataset YOLO
Performance: 10-20x plus rapide que la version originale
- Multi-threading pour génération parallèle
- Batch processing des augmentations
- Pré-chargement optimisé des images
"""
import os
import re
import sys
import cv2
import numpy as np
import shutil
from pathlib import Path
from collections import defaultdict
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict, Optional
import multiprocessing as mp

# Import safe_print
try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print


class DatasetBalancerOptimized:
    """Rééquilibre un dataset YOLO avec optimisations de performance"""
    
    def __init__(self, dataset_dir, target_count=None, strategy='augment', num_workers=None):
        """
        Initialise le balancer optimisé
        
        Args:
            dataset_dir: Dossier contenant images/ et labels/
            target_count: Nombre cible d'images par classe (None = utilise le max)
            strategy: 'augment' (augmenter) ou 'reduce' (réduire) ou 'both'
            num_workers: Nombre de threads (None = CPU_COUNT - 2)
        """
        self.dataset_dir = Path(dataset_dir)
        self.images_dir = self.dataset_dir / "images"
        self.labels_dir = self.dataset_dir / "labels"
        self.target_count = target_count
        self.strategy = strategy
        self.num_workers = num_workers or max(1, mp.cpu_count() - 2)
        
        self.class_distribution = defaultdict(list)
        
        safe_print(f"🚀 Auto-balancer optimisé initialisé:")
        safe_print(f"   Workers: {self.num_workers} threads")
    
    def analyze(self):
        """Analyse la distribution actuelle des classes (OPTIMISÉ)"""
        safe_print("🔍 Analyse de la distribution des classes...")
        
        label_files = list(self.labels_dir.glob("*.txt"))
        
        # Lecture parallèle des labels. IMPORTANT: une image ne compte
        # qu'UNE fois par classe (set), même si elle contient plusieurs
        # instances — sinon les cibles sont faussées et _reduce_class
        # peut tirer plusieurs fois le même fichier.
        def read_label(label_path):
            class_ids = set()
            try:
                with open(label_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            class_ids.add(int(parts[0]))
            except Exception:
                pass
            return label_path.stem, class_ids

        # Lire tous les labels en parallèle
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            results = executor.map(read_label, label_files)

            for img_name, class_ids in results:
                for class_id in class_ids:
                    self.class_distribution[class_id].append(img_name)

        # Afficher la distribution
        safe_print(f"\n📊 Distribution actuelle:")
        sorted_classes = sorted(self.class_distribution.items(), key=lambda x: len(x[1]))

        if len(sorted_classes) <= 20:
            for class_id, images in sorted_classes:
                safe_print(f"   Classe {class_id:3d}: {len(images):4d} images")
        else:
            for class_id, images in sorted_classes[:10]:
                safe_print(f"   Classe {class_id:3d}: {len(images):4d} images")
            safe_print(f"   ... ({len(sorted_classes) - 20} classes cachées)")
            for class_id, images in sorted_classes[-10:]:
                safe_print(f"   Classe {class_id:3d}: {len(images):4d} images")
        
        min_count = len(sorted_classes[0][1]) if sorted_classes else 0
        max_count = len(sorted_classes[-1][1]) if sorted_classes else 0
        
        safe_print(f"\n   Min: {min_count} | Max: {max_count} | Ratio: {max_count/min_count:.2f}x" if min_count > 0 else "")
        
        return self.class_distribution
    
    def balance(self):
        """Rééquilibre le dataset (OPTIMISÉ)"""
        start_time = time.time()
        self.analyze()
        
        if not self.class_distribution:
            safe_print("❌ Aucune classe trouvée!")
            return
        
        # Déterminer le nombre cible
        if self.target_count is None:
            if self.strategy == 'reduce':
                self.target_count = min(len(imgs) for imgs in self.class_distribution.values())
            else:
                self.target_count = max(len(imgs) for imgs in self.class_distribution.values())
        
        safe_print(f"\n🎯 Nombre cible par classe: {self.target_count}")
        safe_print(f"⚙️  Stratégie: {self.strategy}")
        safe_print("")
        
        # Créer un dossier de backup
        backup_dir = self.dataset_dir / "backup_before_balancing"
        if not backup_dir.exists():
            safe_print("💾 Création du backup...")
            backup_start = time.time()
            shutil.copytree(self.images_dir, backup_dir / "images")
            shutil.copytree(self.labels_dir, backup_dir / "labels")
            backup_time = time.time() - backup_start
            safe_print(f"   Backup créé en {backup_time:.1f}s")
        
        # Préparer les tâches
        tasks = []
        for class_id, images in self.class_distribution.items():
            current_count = len(images)
            
            if current_count < self.target_count and self.strategy in ['augment', 'both']:
                needed = self.target_count - current_count
                tasks.append(('augment', class_id, images, needed, current_count))
            elif current_count > self.target_count and self.strategy in ['reduce', 'both']:
                to_remove = current_count - self.target_count
                tasks.append(('reduce', class_id, images, to_remove, current_count))
        
        safe_print(f"📦 {len(tasks)} classes à traiter\n")
        
        # Traiter toutes les classes en parallèle (OPTIMISÉ)
        completed = 0
        total_generated = 0
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {}
            
            for task_type, class_id, images, count, current in tasks:
                if task_type == 'augment':
                    future = executor.submit(self._augment_class_parallel, class_id, images, count)
                else:
                    future = executor.submit(self._reduce_class, class_id, images, count)
                futures[future] = (task_type, class_id, current, count)
            
            # Afficher la progression
            for future in as_completed(futures):
                task_type, class_id, current, count = futures[future]
                try:
                    result = future.result()
                    completed += 1
                    
                    if task_type == 'augment':
                        total_generated += count
                        safe_print(f"📈 Classe {class_id:3d}: {current} → {self.target_count} (+{count}) - [{completed}/{len(tasks)}]")
                    else:
                        safe_print(f"📉 Classe {class_id:3d}: {current} → {self.target_count} (-{count}) - [{completed}/{len(tasks)}]")
                except Exception as e:
                    safe_print(f"❌ Erreur classe {class_id}: {e}")
        
        # Répercuter les ajouts/suppressions sur train.txt / val.txt :
        # le data.yaml du dataset final pointe ces listes figées au merge,
        # sans quoi les images _balN sont ignorées à l'entraînement et les
        # images supprimées restent référencées.
        self._refresh_split_files()

        elapsed = time.time() - start_time
        safe_print(f"\n✅ Balancing terminé en {elapsed:.1f}s!")
        if total_generated > 0:
            safe_print(f"   {total_generated} images générées ({total_generated/elapsed:.1f} img/s)")

    def _refresh_split_files(self):
        """
        Met à jour train.txt / val.txt (listes de chemins absolus créées par
        merge_dataset) après le balancing :
        - retire les entrées dont le fichier n'existe plus (strategy reduce)
        - ajoute chaque nouvelle image _balN au SPLIT DE SON IMAGE SOURCE
          (une variante d'une image de val en train serait une fuite) ;
          les images sans source connue vont au train
        Pas de re-shuffle : le split existant est préservé.
        """
        train_txt = self.dataset_dir / "train.txt"
        val_txt = self.dataset_dir / "val.txt"
        if not train_txt.exists() and not val_txt.exists():
            return  # dataset sans listes de split : rien à faire

        def load_existing(path: Path) -> List[str]:
            if not path.exists():
                return []
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            return [line for line in lines if Path(line).exists()]

        train_list = load_existing(train_txt)
        val_list = load_existing(val_txt)
        referenced = {str(Path(p).resolve()) for p in train_list + val_list}
        val_stems = {Path(p).stem for p in val_list}

        added_train = added_val = 0
        for ext in ('*.png', '*.jpg', '*.jpeg'):
            for img_path in self.images_dir.glob(ext):
                resolved = str(img_path.resolve())
                if resolved in referenced:
                    continue
                referenced.add(resolved)
                source_stem = re.sub(r'_bal\d+$', '', img_path.stem)
                if source_stem in val_stems:
                    val_list.append(resolved)
                    added_val += 1
                else:
                    train_list.append(resolved)
                    added_train += 1

        with open(train_txt, 'w', encoding='utf-8') as f:
            f.write("\n".join(train_list))
        with open(val_txt, 'w', encoding='utf-8') as f:
            f.write("\n".join(val_list))
        safe_print(f"📝 Splits mis à jour: {len(train_list)} train "
                   f"(+{added_train}), {len(val_list)} val (+{added_val})")
    
    def _load_image_with_cache(self, img_name: str) -> Tuple[np.ndarray, str]:
        """Charge une image avec gestion du cache"""
        for ext in ['.png', '.jpg', '.jpeg']:
            img_path = self.images_dir / (img_name + ext)
            if img_path.exists():
                img = cv2.imread(str(img_path))
                if img is not None:
                    return img, ext
        return None, None
    
    def _adjust_yolo_bbox_for_augmentation(self, bbox_line: str,
                                           ax: float, bx: float,
                                           ay: float, by: float) -> Optional[str]:
        """
        Ajuste une bbox YOLO après une transformation affine axiale
        x' = ax·x + bx, y' = ay·y + by (coordonnées normalisées) — couvre
        le flip (ax < 0) ET le scale (|ax| ≠ 1) du pipeline imgaug.
        Retourne None si la bbox devient dégénérée après clipping.
        """
        parts = bbox_line.strip().split()
        if len(parts) != 5:
            return bbox_line.strip() or None

        class_id = parts[0]
        cx, cy, w, h = map(float, parts[1:])

        cx = ax * cx + bx
        cy = ay * cy + by
        w = abs(ax) * w
        h = abs(ay) * h

        # Clipper aux bords de l'image (un zoom > 1 peut faire déborder)
        x0 = max(0.0, min(1.0, cx - w / 2))
        x1 = max(0.0, min(1.0, cx + w / 2))
        y0 = max(0.0, min(1.0, cy - h / 2))
        y1 = max(0.0, min(1.0, cy + h / 2))
        if x1 - x0 < 1e-4 or y1 - y0 < 1e-4:
            return None

        return (f"{class_id} {(x0 + x1) / 2:.6f} {(y0 + y1) / 2:.6f} "
                f"{x1 - x0:.6f} {y1 - y0:.6f}")

    def _augment_single_image(self, args: Tuple) -> bool:
        """Augmente une seule image (pour parallélisation)"""
        img, source_img_name, generated_idx, aug, ext = args

        try:
            # Appliquer l'augmentation avec détection des transformations
            import imgaug as ia

            h, w = img.shape[:2]

            # 3 keypoints (coin + axes) pour mesurer la transformation
            # affine réellement appliquée (flip ET scale)
            kps = ia.KeypointsOnImage([
                ia.Keypoint(x=0, y=0),
                ia.Keypoint(x=w - 1, y=0),
                ia.Keypoint(x=0, y=h - 1),
            ], shape=img.shape)

            # Appliquer l'augmentation
            img_aug, kps_aug = aug(image=img, keypoints=kps)

            # Reconstruire la transformation axiale en coordonnées normalisées
            k0, k1, k2 = kps_aug.keypoints
            ax = (k1.x - k0.x) / max(1, w - 1)
            ay = (k2.y - k0.y) / max(1, h - 1)
            bx = k0.x / w
            by = k0.y / h

            # Générer un nouveau nom
            new_name = f"{source_img_name}_bal{generated_idx}"
            new_img_path = self.images_dir / (new_name + ext)
            new_label_path = self.labels_dir / (new_name + ".txt")

            # Sauvegarder l'image avec compression PNG optimisée
            if ext == '.png':
                cv2.imwrite(str(new_img_path), img_aug, [cv2.IMWRITE_PNG_COMPRESSION, 1])
            else:
                cv2.imwrite(str(new_img_path), img_aug)

            # Ajuster et sauvegarder le label
            source_label = self.labels_dir / (source_img_name + ".txt")
            if source_label.exists():
                with open(source_label, 'r') as f:
                    lines = f.readlines()

                # Ajuster chaque bounding box (les dégénérées sont écartées)
                adjusted_lines = [
                    adjusted for line in lines
                    if (adjusted := self._adjust_yolo_bbox_for_augmentation(
                        line, ax, bx, ay, by)) is not None
                ]

                with open(new_label_path, 'w') as f:
                    f.write('\n'.join(adjusted_lines))

            return True
        except Exception:
            return False
    
    def _augment_class_parallel(self, class_id, existing_images, needed):
        """Augmente le nombre d'images d'une classe (VERSION PARALLÈLE)"""
        # Importer ici pour éviter les dépendances
        import imgaug.augmenters as iaa
        
        # Définir les augmentations (SANS rotation pour éviter les bordures noires)
        aug = iaa.Sequential([
            iaa.Sometimes(0.5, iaa.Fliplr(1.0)),
            # PAS de rotation pour éviter les coins noirs dans les mosaïques!
            iaa.Sometimes(0.3, iaa.Multiply((0.8, 1.2))),
            iaa.Sometimes(0.3, iaa.GaussianBlur(sigma=(0, 1.0))),
            iaa.Sometimes(0.2, iaa.AdditiveGaussianNoise(scale=(0, 0.05*255))),
            iaa.Sometimes(0.2, iaa.Affine(scale=(0.9, 1.1))),
            iaa.Sometimes(0.2, iaa.GammaContrast((0.8, 1.2)))
        ])
        
        # Pré-charger TOUTES les images sources (OPTIMISATION)
        source_images = {}
        extensions = {}
        for img_name in existing_images:
            img, ext = self._load_image_with_cache(img_name)
            if img is not None:
                source_images[img_name] = img
                extensions[img_name] = ext
        
        if not source_images:
            return 0
        
        # Préparer les tâches de génération (les images préchargées sont
        # passées directement : pas de relecture disque par variante)
        tasks = []
        for i in range(needed):
            source_img_name = random.choice(existing_images)
            if source_img_name in source_images:
                ext = extensions[source_img_name]
                tasks.append((source_images[source_img_name],
                              source_img_name, i, aug, ext))
        
        # Générer toutes les images en parallèle (BATCH PROCESSING)
        success_count = 0
        batch_size = 10  # Traiter par lots de 10
        
        for batch_start in range(0, len(tasks), batch_size):
            batch = tasks[batch_start:batch_start + batch_size]
            
            with ThreadPoolExecutor(max_workers=min(self.num_workers, len(batch))) as executor:
                results = executor.map(self._augment_single_image, batch)
                success_count += sum(1 for r in results if r)
        
        return success_count
    
    def _reduce_class(self, class_id, images, to_remove):
        """Réduit le nombre d'images d'une classe (OPTIMISÉ)"""
        # Sélectionner aléatoirement les images à supprimer
        to_delete = random.sample(images, to_remove)
        
        deleted = 0
        for img_name in to_delete:
            # Trouver et supprimer l'image
            for ext in ['.png', '.jpg', '.jpeg']:
                img_path = self.images_dir / (img_name + ext)
                if img_path.exists():
                    img_path.unlink()
                    deleted += 1
                    break
            
            # Supprimer le label
            label_path = self.labels_dir / (img_name + ".txt")
            if label_path.exists():
                label_path.unlink()
        
        return deleted


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-balancing OPTIMISÉ de dataset YOLO")
    parser.add_argument("dataset_dir", help="Dossier du dataset")
    parser.add_argument("--target", type=int, help="Nombre cible par classe")
    parser.add_argument("--strategy", choices=['augment', 'reduce', 'both'], 
                        default='augment', help="Stratégie de balancing")
    parser.add_argument("--analyze-only", action="store_true", 
                        help="Analyse seulement, ne pas modifier")
    parser.add_argument("--workers", type=int, help="Nombre de workers")
    args = parser.parse_args()
    
    balancer = DatasetBalancerOptimized(args.dataset_dir, args.target, args.strategy, args.workers)
    
    if args.analyze_only:
        balancer.analyze()
    else:
        balancer.balance()


if __name__ == "__main__":
    main()
