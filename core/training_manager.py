"""
Training Manager - Gestion de l'entraînement YOLO
==================================================

Ce module gère l'entraînement de modèles YOLOv8 pour la détection
de cartes Pokemon.

Fonctionnalités:
- Entraînement avec différentes configurations
- Validation automatique
- Export des métriques
- Visualisation des résultats

Auteur: Pokemon Dataset Generator Team
Version: 3.0.0
"""

import os
import sys
from pathlib import Path

# Import safe_print - gère import relatif ET absolu
try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration pour l'entraînement YOLO"""
    # Modèle de base
    model_name: str = "yolov8n.pt"  # n, s, m, l, x
    
    # Hyperparamètres
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 640
    device: str = "0"  # "0", "cpu", "0,1,2,3"
    workers: int = 4  # Nombre de workers pour le dataloader
    cache: str = "False"  # False, ram, disk
    
    # Chemins
    data_yaml: Path = Path("output/yolov8/data.yaml")
    project_dir: Path = Path("runs/train")
    name: str = "pokemon_detector"
    
    # Options avancées
    patience: int = 50  # Early stopping
    save_period: int = -1  # Sauvegarder tous les N epochs (-1 = désactivé)
    exist_ok: bool = True  # Écraser le dossier existant
    pretrained: bool = True
    optimizer: str = "SGD"  # SGD, Adam, AdamW
    lr0: float = 0.01  # Learning rate initial
    lrf: float = 0.01  # Learning rate final (fraction de lr0)
    cos_lr: bool = False  # Utiliser cosine LR scheduler
    
    # Augmentation
    augment: bool = True
    hsv_h: float = 0.015  # Hue
    hsv_s: float = 0.7    # Saturation
    hsv_v: float = 0.4    # Value
    degrees: float = 0.0  # Rotation
    translate: float = 0.1
    scale: float = 0.5
    shear: float = 0.0
    perspective: float = 0.0
    flipud: float = 0.0   # Flip up-down
    fliplr: float = 0.5   # Flip left-right
    mosaic: float = 1.0
    mixup: float = 0.0
    
    def __post_init__(self):
        """Validation après initialisation"""
        if self.epochs < 1:
            raise ValueError("epochs doit être >= 1")
        if self.batch_size < 1:
            raise ValueError("batch_size doit être >= 1")
        if not self.data_yaml.exists():
            raise FileNotFoundError(f"data.yaml non trouvé: {self.data_yaml}")


class TrainingManager:
    """
    Gestionnaire d'entraînement YOLO
    
    Exemple:
        >>> config = TrainingConfig(epochs=100, batch_size=32)
        >>> manager = TrainingManager(config)
        >>> manager.set_log_callback(lambda msg: print(msg))
        >>> success = manager.train()
        >>> if success:
        ...     metrics = manager.get_metrics()
        ...     print(f"mAP50: {metrics['mAP50']:.3f}")
    """
    
    def __init__(self, config: TrainingConfig):
        """
        Initialise le gestionnaire d'entraînement
        
        Args:
            config: Configuration d'entraînement
        """
        self.config = config
        self._log_callback: Optional[Callable[[str], None]] = None
        self._model = None
        self._results = None
        
    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """
        Définit la fonction callback pour les logs
        
        Args:
            callback: Fonction prenant un message string
        """
        self._log_callback = callback
    
    def _log(self, message: str) -> None:
        """Log un message"""
        logger.info(message)
        if self._log_callback:
            self._log_callback(message)
    
    def train(self) -> bool:
        """
        Lance l'entraînement du modèle
        
        Returns:
            True si succès, False sinon
        """
        try:
            from ultralytics import YOLO
            
            self._log("🎓 Démarrage de l'entraînement YOLO")
            self._log(f"   Modèle: {self.config.model_name}")
            self._log(f"   Epochs: {self.config.epochs}")
            self._log(f"   Batch: {self.config.batch_size}")
            self._log(f"   Image Size: {self.config.image_size}")
            self._log(f"   Device: {self.config.device}")
            self._log(f"   Workers: {self.config.workers}")
            self._log(f"   Cache: {self.config.cache}")
            if self.config.cos_lr:
                self._log(f"   LR: {self.config.lr0} → {self.config.lrf} (Cosine)")
            self._log(f"   Data: {self.config.data_yaml}")
            
            # Charger le modèle pré-entraîné
            self._model = YOLO(self.config.model_name)
            
            # Lancer l'entraînement
            self._results = self._model.train(
                data=str(self.config.data_yaml),
                epochs=self.config.epochs,
                imgsz=self.config.image_size,
                batch=self.config.batch_size,
                device=self.config.device,
                workers=self.config.workers,
                cache=self.config.cache if self.config.cache != "False" else False,
                patience=self.config.patience,
                save=True,
                save_period=self.config.save_period,
                project=str(self.config.project_dir),
                name=self.config.name,
                exist_ok=self.config.exist_ok,
                pretrained=self.config.pretrained,
                optimizer=self.config.optimizer,
                lr0=self.config.lr0,
                lrf=self.config.lrf,
                cos_lr=self.config.cos_lr,
                # Augmentations
                augment=self.config.augment,
                hsv_h=self.config.hsv_h,
                hsv_s=self.config.hsv_s,
                hsv_v=self.config.hsv_v,
                degrees=self.config.degrees,
                translate=self.config.translate,
                scale=self.config.scale,
                shear=self.config.shear,
                perspective=self.config.perspective,
                flipud=self.config.flipud,
                fliplr=self.config.fliplr,
                mosaic=self.config.mosaic,
                mixup=self.config.mixup,
                verbose=True
            )
            
            best_path = self.get_best_model_path()
            self._log("✅ Entraînement terminé!")
            self._log(f"📊 Modèle sauvegardé: {best_path}")
            
            # Afficher métriques finales
            metrics = self.get_metrics()
            if metrics:
                self._log("\n📈 Métriques finales:")
                self._log(f"   mAP50: {metrics.get('mAP50', 0):.3f}")
                self._log(f"   mAP50-95: {metrics.get('mAP50-95', 0):.3f}")
                self._log(f"   Precision: {metrics.get('precision', 0):.3f}")
                self._log(f"   Recall: {metrics.get('recall', 0):.3f}")
            
            return True
            
        except ImportError:
            self._log("❌ Package ultralytics non installé!")
            self._log("   Installation: pip install ultralytics")
            return False
            
        except Exception as e:
            self._log(f"❌ Erreur lors de l'entraînement: {e}")
            import traceback
            self._log(traceback.format_exc())
            return False
    
    def get_best_model_path(self) -> Path:
        """
        Retourne le chemin du meilleur modèle entraîné
        
        Returns:
            Path vers best.pt
        """
        return self.config.project_dir / self.config.name / "weights" / "best.pt"
    
    def get_last_model_path(self) -> Path:
        """
        Retourne le chemin du dernier modèle sauvegardé
        
        Returns:
            Path vers last.pt
        """
        return self.config.project_dir / self.config.name / "weights" / "last.pt"
    
    def get_metrics(self) -> Optional[Dict[str, float]]:
        """
        Récupère les métriques d'entraînement
        
        Returns:
            Dictionnaire des métriques ou None si non disponible
        """
        if self._results is None:
            return None
        
        try:
            # Essayer de récupérer depuis results
            metrics = {}
            
            if hasattr(self._results, 'results_dict'):
                results_dict = self._results.results_dict
                metrics['mAP50'] = results_dict.get('metrics/mAP50(B)', 0)
                metrics['mAP50-95'] = results_dict.get('metrics/mAP50-95(B)', 0)
                metrics['precision'] = results_dict.get('metrics/precision(B)', 0)
                metrics['recall'] = results_dict.get('metrics/recall(B)', 0)
            
            return metrics if metrics else None
            
        except Exception as e:
            self._log(f"⚠️ Impossible de récupérer les métriques: {e}")
            return None
    
    def validate(self, model_path: Optional[Path] = None) -> Optional[Dict[str, float]]:
        """
        Valide un modèle sur le dataset de validation
        
        Args:
            model_path: Chemin du modèle (par défaut: best.pt)
            
        Returns:
            Dictionnaire des métriques de validation
        """
        try:
            from ultralytics import YOLO
            
            if model_path is None:
                model_path = self.get_best_model_path()
            
            if not model_path.exists():
                self._log(f"❌ Modèle non trouvé: {model_path}")
                return None
            
            self._log(f"🔍 Validation du modèle: {model_path}")
            
            model = YOLO(str(model_path))
            results = model.val(data=str(self.config.data_yaml))
            
            metrics = {
                'mAP50': results.box.map50,
                'mAP50-95': results.box.map,
                'precision': results.box.mp,
                'recall': results.box.mr
            }
            
            self._log("✅ Validation terminée")
            self._log(f"   mAP50: {metrics['mAP50']:.3f}")
            self._log(f"   mAP50-95: {metrics['mAP50-95']:.3f}")
            
            return metrics
            
        except Exception as e:
            self._log(f"❌ Erreur validation: {e}")
            return None
    
    def export_model(self, 
                     model_path: Optional[Path] = None,
                     format: str = "onnx") -> Optional[Path]:
        """
        Exporte le modèle dans un autre format
        
        Args:
            model_path: Chemin du modèle source
            format: Format de sortie (onnx, torchscript, coreml, etc.)
            
        Returns:
            Path du modèle exporté ou None si échec
        """
        try:
            from ultralytics import YOLO
            
            if model_path is None:
                model_path = self.get_best_model_path()
            
            if not model_path.exists():
                self._log(f"❌ Modèle non trouvé: {model_path}")
                return None
            
            self._log(f"📦 Export du modèle vers {format}...")
            
            model = YOLO(str(model_path))
            export_path = model.export(format=format)
            
            self._log(f"✅ Modèle exporté: {export_path}")
            return Path(export_path)
            
        except Exception as e:
            self._log(f"❌ Erreur export: {e}")
            return None
    
    def plot_results(self) -> bool:
        """
        Affiche les graphiques d'entraînement
        
        Returns:
            True si succès
        """
        try:
            import cv2
            
            results_png = self.config.project_dir / self.config.name / "results.png"
            
            if not results_png.exists():
                self._log(f"❌ Graphiques non trouvés: {results_png}")
                return False
            
            img = cv2.imread(str(results_png))
            cv2.imshow('Training Results', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            return True
            
        except Exception as e:
            self._log(f"❌ Erreur affichage: {e}")
            return False


def main():
    """Point d'entrée pour exécution standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Entraînement YOLOv8")
    parser.add_argument("--model", default="yolov8n.pt", 
                       help="Modèle de base (yolov8n.pt, yolov8s.pt, etc.)")
    parser.add_argument("--epochs", type=int, default=50,
                       help="Nombre d'epochs")
    parser.add_argument("--batch", type=int, default=16,
                       help="Taille du batch")
    parser.add_argument("--device", default="0",
                       help="Device (0, cpu, 0,1,2,3)")
    parser.add_argument("--data", default="output/yolov8/data.yaml",
                       help="Chemin vers data.yaml")
    
    args = parser.parse_args()
    
    # Créer configuration
    config = TrainingConfig(
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch,
        device=args.device,
        data_yaml=Path(args.data)
    )
    
    # Lancer entraînement
    manager = TrainingManager(config)
    manager.set_log_callback(print)
    
    success = manager.train()
    
    if success:
        safe_print("\n" + "="*50)
        safe_print("🎉 Entraînement réussi!")
        safe_print(f"📊 Modèle: {manager.get_best_model_path()}")
        safe_print("="*50)
        sys.exit(0)
    else:
        safe_print("\n❌ Entraînement échoué!")
        sys.exit(1)


if __name__ == "__main__":
    main()
