#!/usr/bin/env python3
"""
Module d'auto-balancing des classes dans un dataset YOLO
Rééquilibre automatiquement le nombre d'images par classe
"""
import os
import sys
import cv2
import numpy as np
import shutil
from pathlib import Path
from collections import defaultdict
import random

# Import safe_print - gère import relatif ET absolu
try:
    from .utils import safe_print
except ImportError:
    # Exécution directe du script (python core/auto_balancer.py)
    from utils import safe_print


class DatasetBalancer:
    """Rééquilibre un dataset YOLO pour avoir le même nombre d'images par classe"""
    
    def __init__(self, dataset_dir, target_count=None, strategy='augment'):
        """
        Initialise le balancer
        
        Args:
            dataset_dir: Dossier contenant images/ et labels/
            target_count: Nombre cible d'images par classe (None = utilise le max)
            strategy: 'augment' (augmenter) ou 'reduce' (réduire) ou 'both'
        """
        self.dataset_dir = Path(dataset_dir)
        self.images_dir = self.dataset_dir / "images"
        self.labels_dir = self.dataset_dir / "labels"
        self.target_count = target_count
        self.strategy = strategy
        
        self.class_distribution = defaultdict(list)
    
    def analyze(self):
        """Analyse la distribution actuelle des classes"""
        safe_print("🔍 Analyse de la distribution des classes...")
        
        label_files = list(self.labels_dir.glob("*.txt"))
        
        for label_path in label_files:
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    # Stocker le fichier image associé
                    img_name = label_path.stem
                    self.class_distribution[class_id].append(img_name)
        
        # Afficher la distribution
        safe_print(f"\n📊 Distribution actuelle:")
        sorted_classes = sorted(self.class_distribution.items(), key=lambda x: len(x[1]))
        
        for class_id, images in sorted_classes:
            safe_print(f"   Classe {class_id:3d}: {len(images):4d} images")
        
        min_count = len(sorted_classes[0][1]) if sorted_classes else 0
        max_count = len(sorted_classes[-1][1]) if sorted_classes else 0
        
        safe_print(f"\n   Min: {min_count} | Max: {max_count} | Ratio: {max_count/min_count:.2f}x" if min_count > 0 else "")
        
        return self.class_distribution
    
    def balance(self):
        """Rééquilibre le dataset"""
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
            shutil.copytree(self.images_dir, backup_dir / "images")
            shutil.copytree(self.labels_dir, backup_dir / "labels")
        
        # Balancer chaque classe
        for class_id, images in self.class_distribution.items():
            current_count = len(images)
            
            if current_count < self.target_count and self.strategy in ['augment', 'both']:
                # Augmenter
                needed = self.target_count - current_count
                safe_print(f"📈 Classe {class_id}: {current_count} → {self.target_count} (+{needed})")
                self._augment_class(class_id, images, needed)
            
            elif current_count > self.target_count and self.strategy in ['reduce', 'both']:
                # Réduire
                to_remove = current_count - self.target_count
                safe_print(f"📉 Classe {class_id}: {current_count} → {self.target_count} (-{to_remove})")
                self._reduce_class(class_id, images, to_remove)
            
            else:
                safe_print(f"✅ Classe {class_id}: {current_count} (déjà équilibré)")
        
        safe_print("\n✅ Balancing terminé!")
    
    def _augment_class(self, class_id, existing_images, needed):
        """Augmente le nombre d'images d'une classe"""
        # Importer ici pour éviter les dépendances
        import imgaug.augmenters as iaa
        
        # Définir les augmentations
        aug = iaa.Sequential([
            iaa.Sometimes(0.5, iaa.Fliplr(1.0)),
            iaa.Sometimes(0.3, iaa.Affine(rotate=(-15, 15))),
            iaa.Sometimes(0.3, iaa.Multiply((0.8, 1.2))),
            iaa.Sometimes(0.3, iaa.GaussianBlur(sigma=(0, 1.0))),
            iaa.Sometimes(0.2, iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)))
        ])
        
        # Générer les nouvelles images
        generated = 0
        while generated < needed:
            # Choisir une image source aléatoire
            source_img_name = random.choice(existing_images)
            
            # Trouver l'extension de l'image
            img_path = None
            for ext in ['.png', '.jpg', '.jpeg']:
                test_path = self.images_dir / (source_img_name + ext)
                if test_path.exists():
                    img_path = test_path
                    break
            
            if img_path is None:
                continue
            
            # Charger l'image
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # Appliquer l'augmentation
            img_aug = aug(image=img)
            
            # Générer un nouveau nom
            new_name = f"{source_img_name}_bal{generated}"
            new_img_path = self.images_dir / (new_name + img_path.suffix)
            new_label_path = self.labels_dir / (new_name + ".txt")
            
            # Sauvegarder l'image
            cv2.imwrite(str(new_img_path), img_aug)
            
            # Copier le label
            source_label = self.labels_dir / (source_img_name + ".txt")
            if source_label.exists():
                shutil.copy(source_label, new_label_path)
            
            generated += 1
    
    def _reduce_class(self, class_id, images, to_remove):
        """Réduit le nombre d'images d'une classe"""
        # Sélectionner aléatoirement les images à supprimer
        to_delete = random.sample(images, to_remove)
        
        for img_name in to_delete:
            # Trouver et supprimer l'image
            for ext in ['.png', '.jpg', '.jpeg']:
                img_path = self.images_dir / (img_name + ext)
                if img_path.exists():
                    img_path.unlink()
                    break
            
            # Supprimer le label
            label_path = self.labels_dir / (img_name + ".txt")
            if label_path.exists():
                label_path.unlink()


def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-balancing de dataset YOLO")
    parser.add_argument("dataset_dir", help="Dossier du dataset")
    parser.add_argument("--target", type=int, help="Nombre cible par classe")
    parser.add_argument("--strategy", choices=['augment', 'reduce', 'both'], 
                        default='augment', help="Stratégie de balancing")
    parser.add_argument("--analyze-only", action="store_true", 
                        help="Analyse seulement, ne pas modifier")
    args = parser.parse_args()
    
    balancer = DatasetBalancer(args.dataset_dir, args.target, args.strategy)
    
    if args.analyze_only:
        balancer.analyze()
    else:
        balancer.balance()


if __name__ == "__main__":
    main()
