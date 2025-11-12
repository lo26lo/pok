"""
Core Package - Pokemon Dataset Generator
=========================================

Ce package contient tous les modules métier pour la génération,
l'augmentation, la validation et l'export de datasets Pokemon.

Modules disponibles:
-------------------
**Génération & Augmentation:**
- augmentation: Augmentation d'images avec imgaug
- mosaic: Création de mosaïques YOLO
- holographic_augmenter: Effets holographiques sur cartes
- random_erasing: Augmentation par effacement aléatoire

**Validation & Export:**
- dataset_validator: Validation des annotations YOLO
- dataset_exporter: Export multi-format (COCO, VOC, TFRecord)
- auto_balancer: Équilibrage automatique des classes

**API & Données:**
- tcgdex_api: Interface API Pokemon TCG

**Machine Learning:**
- workflow_manager: Orchestration pipeline complet
- training_manager: Entraînement YOLOv8
- detection_manager: Détection temps réel et batch

**Utilitaires:**
- utils: Fonctions utilitaires communes

Usage:
------
    # Import modules de base
    from core import augmentation
    from core import mosaic
    from core.utils import load_card_data
    
    # Import managers
    from core.workflow_manager import WorkflowManager, WorkflowConfig
    from core.training_manager import TrainingManager, TrainingConfig
    from core.detection_manager import DetectionManager, DetectionConfig
    
    # Workflow automatique
    config = WorkflowConfig(num_augmentations=20)
    manager = WorkflowManager(config)
    results = manager.run()
"""

__version__ = "3.0.0"
__author__ = "Pokemon Dataset Generator Team"

# Imports pour faciliter l'accès aux modules
# Remplacer imports directs par des imports protégés pour éviter les
# circular-imports lors de l'initialisation du package (ex: GUI import)
try:
    from . import augmentation
except Exception:
    augmentation = None

try:
    from . import mosaic_optimized as mosaic  # Version GPU-optimisée par défaut
except Exception:
    try:
        from . import mosaic as mosaic
    except Exception:
        mosaic = None

try:
    from . import dataset_validator
except Exception:
    dataset_validator = None

try:
    from . import dataset_exporter
except Exception:
    dataset_exporter = None

try:
    from . import auto_balancer_optimized as auto_balancer  # Version GPU-optimisée par défaut
except Exception:
    try:
        from . import auto_balancer as auto_balancer
    except Exception:
        auto_balancer = None

try:
    from . import holographic_augmenter_optimized as holographic_augmenter  # Version GPU-optimisée par défaut
except Exception:
    try:
        from . import holographic_augmenter as holographic_augmenter
    except Exception:
        holographic_augmenter = None

try:
    from . import tcgdex_api
except Exception:
    tcgdex_api = None

try:
    from . import random_erasing
except Exception:
    random_erasing = None

try:
    from . import utils
except Exception:
    utils = None

try:
    from . import workflow_manager
except Exception:
    workflow_manager = None

try:
    from . import training_manager
except Exception:
    training_manager = None

try:
    from . import detection_manager
except Exception:
    detection_manager = None

# Export safe_print pour faciliter l'usage (fallback si utils absent)
try:
    from .utils import safe_print
except Exception:
    try:
        # si utils n'est pas disponible en tant que package relatif, tente import absolu
        from utils import safe_print
    except Exception:
        def safe_print(*args, **kwargs):
            # fallback minimal
            print(*args, **kwargs)

__all__ = [
    'augmentation',
    'mosaic',
    'dataset_validator',
    'dataset_exporter',
    'auto_balancer',
    'holographic_augmenter',
    'tcgdex_api',
    'random_erasing',
    'utils',
    'workflow_manager',
    'training_manager',
    'detection_manager',
    'safe_print',  # Utilitaire pour print sans erreurs Unicode
]
