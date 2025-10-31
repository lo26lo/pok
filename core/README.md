# Core Package Documentation

## 📁 Architecture

Le dossier `core/` contient tous les modules métier séparés de l'interface GUI.

```
core/
├── __init__.py                  # Package principal
│
├── 🎨 GÉNÉRATION & AUGMENTATION
│   ├── augmentation.py          # Augmentation imgaug
│   ├── mosaic.py                # Mosaïques YOLO
│   ├── holographic_augmenter.py # Effets holographiques
│   └── random_erasing.py        # Random erasing
│
├── ✅ VALIDATION & EXPORT
│   ├── dataset_validator.py    # Validation YOLO
│   ├── dataset_exporter.py      # Export multi-format
│   └── auto_balancer.py         # Équilibrage classes
│
├── 🤖 MACHINE LEARNING
│   ├── workflow_manager.py      # Pipeline automatique
│   ├── training_manager.py      # Entraînement YOLOv8
│   └── detection_manager.py     # Détection temps réel
│
├── 🔌 API & DONNÉES
│   └── tcgdex_api.py            # API Pokemon TCG
│
└── 🛠️ UTILITAIRES
    ├── utils.py                 # Fonctions communes
    └── numpy_patch.py           # Fix NumPy 2.0
```

## 🚀 Utilisation

### Import basique
```python
from core import augmentation
from core import mosaic
from core.utils import load_card_data
```

### Workflow automatique
```python
from core.workflow_manager import WorkflowManager, WorkflowConfig

config = WorkflowConfig(
    num_augmentations=20,
    mosaic_mode="standard",
    enable_validation=True
)

manager = WorkflowManager(config)
manager.set_log_callback(print)
results = manager.run()

if manager.is_success():
    print(manager.get_summary())
```

### Entraînement YOLO
```python
from core.training_manager import TrainingManager, TrainingConfig

config = TrainingConfig(
    model_name="yolov8n.pt",
    epochs=100,
    batch_size=32
)

manager = TrainingManager(config)
manager.set_log_callback(print)

if manager.train():
    metrics = manager.get_metrics()
    print(f"mAP50: {metrics['mAP50']:.3f}")
```

### Détection
```python
from core.detection_manager import DetectionManager, DetectionConfig

config = DetectionConfig(
    model_path=Path("runs/train/best.pt"),
    confidence=0.5
)

manager = DetectionManager(config)

# Image unique
detections = manager.detect_image("test.jpg")
for det in detections:
    print(f"{det.class_name}: {det.confidence:.2%}")

# Webcam
manager.detect_webcam()

# Batch
results = manager.detect_folder("images/", output_folder="results/")
```

## 📝 Annotations Type

Tous les modules utilisent des annotations complètes :

```python
from typing import List, Dict, Optional, Callable
from pathlib import Path
from dataclasses import dataclass

@dataclass
class MyConfig:
    """Configuration avec validation"""
    value: int
    path: Path
    
    def __post_init__(self):
        if self.value < 0:
            raise ValueError("value doit être >= 0")

def my_function(param: str, count: int = 10) -> List[str]:
    """
    Description de la fonction
    
    Args:
        param: Description paramètre
        count: Nombre d'éléments
        
    Returns:
        Liste de résultats
        
    Raises:
        ValueError: Si param vide
    """
    pass
```

## 🔄 Dépendances

### Core (requis)
- numpy
- opencv-python
- pandas
- pillow
- imgaug

### ML (optionnel)
- ultralytics (YOLO)
- torch

### API (optionnel)
- requests

## 🧪 Tests

Chaque module peut être exécuté standalone :

```bash
# Workflow
python core/workflow_manager.py

# Training
python core/training_manager.py --epochs 50

# Detection
python core/detection_manager.py model.pt --image test.jpg
```

## 📊 Logs

Tous les managers supportent les callbacks :

```python
def my_log_function(message: str):
    print(f"[LOG] {message}")

manager.set_log_callback(my_log_function)
```

## 🎯 Bonnes pratiques

1. **Séparation GUI / Logique** : Ne jamais importer tkinter dans core/
2. **Type hints** : Toujours annoter les fonctions publiques
3. **Docstrings** : Format Google/Numpy style
4. **Validation** : Utiliser `__post_init__` dans dataclasses
5. **Callbacks** : Pour communication avec GUI
6. **Lazy loading** : Importer ultralytics/cv2 dans les méthodes
7. **Logging** : Utiliser le module logging + callbacks

## 🔗 Intégration GUI

Le GUI doit simplement instancier les managers et passer des callbacks :

```python
# Dans GUI
from core.workflow_manager import WorkflowManager, WorkflowConfig

def on_log(msg):
    self.log_text.insert(tk.END, msg + "\n")

def on_progress(current, total, message):
    self.progress_bar['value'] = (current / total) * 100
    self.progress_label.config(text=message)

config = WorkflowConfig(...)
manager = WorkflowManager(config)
manager.set_log_callback(on_log)
manager.set_progress_callback(on_progress)

# Lancer dans un thread
threading.Thread(target=manager.run, daemon=True).start()
```

## 📄 Licence

Voir LICENSE à la racine du projet.
