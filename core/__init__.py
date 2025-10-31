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
- numpy_patch: Correctif compatibilité NumPy 2.0

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
from . import augmentation
from . import mosaic
from . import dataset_validator
from . import dataset_exporter
from . import auto_balancer
from . import holographic_augmenter
from . import tcgdex_api
from . import random_erasing
from . import utils
# from . import numpy_patch  # Patch désactivé : NumPy 1.26.4 dans venv, pas besoin
from . import workflow_manager
from . import training_manager
from . import detection_manager

# Export safe_print pour faciliter l'usage
from .utils import safe_print

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
    # 'numpy_patch',  # Disponible mais non appliqué automatiquement
    'workflow_manager',
    'training_manager',
    'detection_manager',
    'safe_print',  # Utilitaire pour print sans erreurs Unicode
]
