# 🚀 Advanced Guide - Pokémon Dataset Generator

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025

---

## 📋 Table des Matières

1. [GPU Optimizations](#gpu-optimizations)
2. [PyInstaller .exe Creation](#pyinstaller-exe-creation)
3. [Excel to YAML Migration](#excel-to-yaml-migration)
4. [Custom Augmentation Pipelines](#custom-augmentation-pipelines)
5. [Multi-GPU Training](#multi-gpu-training)
6. [Performance Profiling](#performance-profiling)
7. [Advanced YOLO Configuration](#advanced-yolo-configuration)
8. [Docker Deployment](#docker-deployment)

---

## 🎮 GPU Optimizations

### Architecture Detection

**Supported GPU Types** :
- ✅ NVIDIA CUDA (RTX 20xx/30xx/40xx/50xx)
- ✅ AMD ROCm (Linux only)
- ✅ Apple Silicon MPS (M1/M2/M3)
- ✅ Intel oneAPI (experimental)

**Auto-detection** :
```python
import torch

# Check CUDA
if torch.cuda.is_available():
    print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

# Check MPS (Apple)
if torch.backends.mps.is_available():
    print("MPS (Apple Silicon) available")

# Check ROCm (AMD)
if torch.version.hip:
    print(f"ROCm version: {torch.version.hip}")
```

---

### CUDA Memory Management

**Problem: Out of Memory (OOM)**

**Strategy 1: Gradient Accumulation**
```python
# Instead of batch_size=32, use batch_size=8 with accumulation
from ultralytics import YOLO

model = YOLO('yolov8n.pt')
model.train(
    data='data.yaml',
    epochs=100,
    batch=8,  # Reduced batch size
    accumulate=4  # Gradient accumulation (effective batch=32)
)
```

**Strategy 2: Mixed Precision (FP16)**
```python
# Enable AMP (Automatic Mixed Precision)
model.train(
    data='data.yaml',
    amp=True,  # 2× faster, 50% less VRAM
    device=0
)
```

**Strategy 3: Memory Efficient Training**
```python
# Disable cache for large datasets
model.train(
    data='data.yaml',
    cache=False,  # Don't cache images in RAM
    workers=4,  # Reduce workers
    batch=8
)
```

**Strategy 4: Manual CUDA Memory Management**
```python
import torch
import gc

# Clear CUDA cache
torch.cuda.empty_cache()
gc.collect()

# Monitor CUDA memory
print(f"Allocated: {torch.cuda.memory_allocated() / 1e9:.2f} GB")
print(f"Reserved: {torch.cuda.memory_reserved() / 1e9:.2f} GB")
```

---

### GPU-Accelerated Augmentation

**Problem: imgaug is CPU-only (slow)**

**Solution 1: Albumentations (GPU support)**
```python
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2

# GPU-accelerated pipeline
transform = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.HueSaturationValue(p=0.5),
    A.GaussianBlur(blur_limit=(3, 7), p=0.3),
    A.Rotate(limit=15, p=0.5),
    A.HorizontalFlip(p=0.5),
    ToTensorV2()  # Convert to PyTorch tensor
])

# Apply on GPU
image = cv2.imread('card.jpg')
augmented = transform(image=image)['image']
# Then move to GPU: augmented.cuda()
```

**Solution 2: NVIDIA DALI (advanced)**
```python
# Requires: pip install --extra-index-url https://developer.download.nvidia.com/compute/redist nvidia-dali-cuda120

from nvidia.dali.pipeline import Pipeline
import nvidia.dali.fn as fn
import nvidia.dali.types as types

class AugmentationPipeline(Pipeline):
    def __init__(self, batch_size, num_threads, device_id):
        super().__init__(batch_size, num_threads, device_id)
        self.input = fn.readers.file(file_root="images/")
        
    def define_graph(self):
        images = self.input
        images = fn.decoders.image(images, device="mixed")  # GPU decode
        images = fn.resize(images, size=(640, 640))
        images = fn.rotate(images, angle=fn.random.uniform(range=(-15, 15)))
        images = fn.brightness_contrast(images, 
                                       brightness=fn.random.uniform(range=(0.8, 1.2)),
                                       contrast=fn.random.uniform(range=(0.8, 1.2)))
        return images

# 10-50× faster than CPU augmentation
pipe = AugmentationPipeline(batch_size=32, num_threads=4, device_id=0)
pipe.build()
```

**Performance Comparison** :

| Method | Speed (1000 images) | GPU Usage |
|--------|---------------------|-----------|
| imgaug (CPU) | 30-50 min | 0% |
| Albumentations (CPU) | 20-30 min | 0% |
| Albumentations (GPU) | 5-10 min | 40-60% |
| NVIDIA DALI | 1-2 min | 80-90% |

---

### Optimizing Holographic Effects (v3.2.2)

**GPU Acceleration Already Implemented** :
- ✅ Custom CUDA kernels
- ✅ LUT (Look-Up Tables) pre-computed
- ✅ Separable filters (2D → 2× 1D convolution)
- ✅ Half-precision (FP16) for GPU computations

**Manual GPU Usage** :
```python
from core.holographic_augmenter_optimized import HolographicAugmenter
import torch

# Force GPU device
augmenter = HolographicAugmenter(device='cuda:0')  # or 'cuda:1' for 2nd GPU

# Batch processing (recommended)
images = [img1, img2, img3, ...]  # List of NumPy arrays
augmented = augmenter.apply_batch(
    images, 
    style='rainbow',
    intensity=0.7,
    batch_size=16  # Process 16 at once
)
```

**Performance Tuning** :
```python
# Configuration
augmenter = HolographicAugmenter(
    device='cuda',
    use_fp16=True,  # Half-precision (2× faster)
    num_workers=4,  # CPU threads for pre/post processing
    cache_lut=True  # Cache Look-Up Tables (saves 30% time)
)
```

---

### RTX 40xx/50xx Optimizations

**CUDA 12.4 Features** :
- ✅ Tensor Cores Gen 4
- ✅ DLSS 3.5 (not used by YOLO)
- ✅ ADA Lovelace architecture

**PyTorch Installation** :
```batch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**YOLO Training Optimizations** :
```python
model.train(
    data='data.yaml',
    epochs=100,
    batch=32,  # RTX 4090: 64-128, RTX 4060: 16-32
    imgsz=640,
    amp=True,  # Enable AMP (critical for 40xx)
    device=0,
    # RTX 40xx specific
    workers=16,  # More workers for faster data loading
    cache='ram',  # Cache in RAM (RTX 4090: 24GB VRAM)
    optimizer='AdamW',  # Better than SGD for large batch
    lr0=0.01,
    lrf=0.001
)
```

**Expected Performance (YOLOv8n, 640px, batch=16)** :

| GPU | FPS Training | FPS Inference | VRAM |
|-----|--------------|---------------|------|
| RTX 4090 | 150-200 | 300-400 | 4-6 GB |
| RTX 4080 | 120-150 | 250-300 | 4-5 GB |
| RTX 4070 Ti | 100-120 | 200-250 | 3-4 GB |
| RTX 4060 Ti | 60-80 | 120-150 | 3-4 GB |

---

### CPU Fallback Optimizations

**When GPU unavailable, optimize CPU** :

**1. Enable Multi-threading**
```python
import torch
torch.set_num_threads(8)  # Use 8 CPU cores

# YOLO training
model.train(
    data='data.yaml',
    workers=8,  # Match CPU cores
    batch=4,  # Smaller batch for CPU
    device='cpu'
)
```

**2. Intel MKL Optimizations**
```batch
# Install Intel MKL
pip install mkl mkl-service

# Set environment variables
set MKL_NUM_THREADS=8
set OMP_NUM_THREADS=8
set NUMEXPR_NUM_THREADS=8
```

**3. OpenCV Threading**
```python
import cv2
cv2.setNumThreads(8)  # Enable OpenCV multi-threading
```

**CPU Performance (i7-12700K, 8 cores)** :
- Training YOLOv8n : 15-20 sec/epoch (vs 3-5 sec on RTX 3060)
- Augmentation : 2-3 sec/image
- Detection : 8-15 FPS (vs 45-60 on GPU)

---

## 📦 PyInstaller .exe Creation

### Why Create Executable ?

**Advantages** :
- ✅ No Python installation required
- ✅ Single file distribution
- ✅ Easier for non-technical users
- ✅ Version control (bundle specific Python/deps)

**Disadvantages** :
- ❌ Large file size (~500 MB - 1.5 GB)
- ❌ Slower first launch (unpacking)
- ❌ Harder to debug
- ❌ Windows Defender false positives

---

### Prerequisites

**Install PyInstaller** :
```batch
call .venv\Scripts\activate.bat
pip install pyinstaller
```

**Verify installation** :
```batch
pyinstaller --version
# Should display: 6.x.x
```

---

### Build Executable

**Using provided .spec file** :
```batch
call .venv\Scripts\activate.bat
pyinstaller config/pokemon_dataset_generator.spec
```

**Output** :
- `dist/Pokemon_Dataset_Generator.exe` (~500 MB)
- `build/` folder (temporary, can delete)

**Duration** : 10-15 minutes (first build)

---

### Custom .spec Configuration

**`config/pokemon_dataset_generator.spec`** :
```python
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Collect all data files
datas = [
    ('config', 'config'),
    ('models', 'models'),
    ('backgrounds', 'backgrounds'),
    ('docs', 'docs'),
]

# Hidden imports (modules not auto-detected)
hiddenimports = [
    'ultralytics',
    'imgaug',
    'customtkinter',
    'tkinterdnd2',
    'PIL',
    'cv2',
    'yaml',
    'torch',
    'torchvision',
]

a = Analysis(
    ['GUI_v3.1_modern.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'jupyter', 'notebook'],  # Exclude unused
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Pokemon_Dataset_Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='config/icon.ico',  # Custom icon (optional)
)
```

---

### Optimize .exe Size

**Problem: 1.5 GB executable**

**Solution 1: Exclude unnecessary modules**
```python
# In .spec file
excludes=[
    'matplotlib',
    'jupyter',
    'notebook',
    'scipy.stats',
    'pandas.plotting',
    'tensorboard',
    'wandb',
]
```

**Solution 2: Use --onefile vs --onedir**
```batch
# Single file (slower startup, easier distribution)
pyinstaller --onefile GUI_v3.1_modern.py

# Directory (faster startup, multiple files)
pyinstaller --onedir GUI_v3.1_modern.py
```

**Solution 3: UPX Compression**
```batch
# Download UPX: https://upx.github.io/
# Place upx.exe in PATH

# Build with compression
pyinstaller --upx-dir="C:\Tools\upx" config/pokemon_dataset_generator.spec
```

**Size Comparison** :

| Configuration | Size | Startup Time |
|---------------|------|--------------|
| --onedir (no UPX) | 1.5 GB | 3-5 sec |
| --onedir (UPX) | 800 MB | 5-8 sec |
| --onefile (no UPX) | 600 MB | 10-15 sec |
| --onefile (UPX) | 450 MB | 15-20 sec |

**Recommendation** : `--onedir` without UPX (best balance)

---

### Handle PyTorch in .exe

**Problem: PyTorch adds 1+ GB**

**Solution: CPU-only PyTorch**
```batch
# Before building .exe
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Then build
pyinstaller config/pokemon_dataset_generator.spec
```

**Trade-off** : 
- ✅ Reduces .exe size by 50% (1.5 GB → 750 MB)
- ❌ No GPU support in .exe

**For GPU .exe** : Include CUDA runtime (adds ~500 MB)

---

### Distribution

**Package for distribution** :
```batch
# Create ZIP with .exe + required files
powershell Compress-Archive -Path dist/Pokemon_Dataset_Generator.exe, README.md, models/ -DestinationPath Pokemon_Dataset_Generator_v3.2.zip
```

**Contents** :
```
Pokemon_Dataset_Generator_v3.2.zip
├── Pokemon_Dataset_Generator.exe
├── README.md
├── models/
│   ├── yolo11n.pt
│   └── card_name_to_id.json
└── config/
    └── api_config.json.example
```

**Installer (optional with Inno Setup)** :
```iss
; Pokemon_Dataset_Generator.iss
[Setup]
AppName=Pokémon Dataset Generator
AppVersion=3.2
DefaultDirName={pf}\Pokemon_Dataset_Generator
OutputBaseFilename=Pokemon_Dataset_Generator_Setup_v3.2
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\Pokemon_Dataset_Generator.exe"; DestDir: "{app}"
Source: "models\*"; DestDir: "{app}\models"; Flags: recursesubdirs
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{commondesktop}\Pokémon Dataset Generator"; Filename: "{app}\Pokemon_Dataset_Generator.exe"
```

---

### Troubleshooting .exe

**Problem 1: "Failed to execute script"**

**Cause** : Missing hidden import

**Solution** : Add to hiddenimports in .spec
```python
hiddenimports = [
    'ultralytics',
    'imgaug.augmenters',  # Add submodules
    'cv2.data',
]
```

**Problem 2: "DLL load failed"**

**Cause** : Missing Visual C++ Redistributable

**Solution** : Include in installer or ask user to install:
- [vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe)

**Problem 3: Slow startup (20+ seconds)**

**Cause** : Unpacking large .exe

**Solution** : Use --onedir instead of --onefile

---

## 📄 Excel to YAML Migration

### Why Migrate Excel → YAML ?

**Problems with Excel** :
- ❌ Large file size (10 MB for 1000 cards)
- ❌ Requires openpyxl dependency
- ❌ Slower read/write (1-2 sec)
- ❌ Not Git-friendly (binary format)
- ❌ Hard to diff/merge

**Advantages of YAML** :
- ✅ Smaller size (2 MB for 1000 cards, 80% reduction)
- ✅ Human-readable text format
- ✅ Fast read/write (0.1 sec)
- ✅ Git-friendly (text diff)
- ✅ No external dependency

---

### Migration Script

**Automatic conversion** :
```batch
scripts\run_script.bat convert_excel_to_yaml
```

**Manual Python** :
```python
import pandas as pd
import yaml

# Read Excel
df = pd.read_excel('excel/cards_with_prices.xlsx')

# Convert to dict
cards_list = df.to_dict('records')

# Save as YAML
with open('models/cards_database.yaml', 'w', encoding='utf-8') as f:
    yaml.dump({'cards': cards_list}, f, allow_unicode=True, default_flow_style=False)

print(f"✅ Converted {len(cards_list)} cards to YAML")
```

---

### YAML Structure

**Example `cards_database.yaml`** :
```yaml
cards:
  - name: "Pikachu"
    id: "sv08_001"
    set: "Surging Sparks"
    type: "Electric"
    rarity: "Common"
    hp: 60
    stage: "Basic"
    price: 2.50
    price_max: 5.00
    price_source: "cardmarket"
    price_currency: "EUR"
    last_updated: "2025-11-14"
    
  - name: "Charizard ex"
    id: "sv08_182"
    set: "Surging Sparks"
    type: "Fire"
    rarity: "Ultra Rare"
    hp: 330
    stage: "Stage 2"
    price: 120.00
    price_max: 200.00
    price_source: "tcgplayer"
    price_currency: "USD"
    last_updated: "2025-11-14"
```

---

### Loading YAML in Python

**Fast loading** :
```python
import yaml
from pathlib import Path

def load_cards_database():
    yaml_path = Path('models/cards_database.yaml')
    
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return data['cards']

# Usage
cards = load_cards_database()
print(f"Loaded {len(cards)} cards")

# Access
pikachu = next(c for c in cards if c['name'] == 'Pikachu')
print(f"Pikachu price: {pikachu['price']} {pikachu['price_currency']}")
```

**Performance** :
- Excel (openpyxl) : 1.2 sec (1000 cards)
- YAML (PyYAML) : 0.1 sec (1000 cards)
- **12× faster !**

---

### Updating Prices in YAML

**Manual update** :
```python
import yaml

# Load
with open('models/cards_database.yaml', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Update
for card in data['cards']:
    if card['name'] == 'Charizard ex':
        card['price'] = 150.00
        card['price_max'] = 250.00
        card['last_updated'] = '2025-11-14'

# Save
with open('models/cards_database.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
```

**Batch update from TCGdex API** :
```batch
scripts\run_script.bat update_prices_from_tcgdex
```

---

### Backward Compatibility

**Support both Excel and YAML** :
```python
from pathlib import Path
import yaml
import pandas as pd

def load_cards_flexible():
    yaml_path = Path('models/cards_database.yaml')
    excel_path = Path('excel/cards_with_prices.xlsx')
    
    # Prefer YAML
    if yaml_path.exists():
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['cards']
    
    # Fallback to Excel
    elif excel_path.exists():
        df = pd.read_excel(excel_path)
        return df.to_dict('records')
    
    else:
        raise FileNotFoundError("No cards database found (YAML or Excel)")

# Works with both formats
cards = load_cards_flexible()
```

---

## 🎨 Custom Augmentation Pipelines

### Creating Custom imgaug Pipeline

**Basic custom pipeline** :
```python
import imgaug.augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
import cv2

# Define custom pipeline
custom_seq = iaa.Sequential([
    # Heavy rotation for testing rotation invariance
    iaa.Affine(rotate=(-45, 45)),
    
    # Extreme brightness
    iaa.Multiply((0.5, 2.0)),
    
    # Heavy blur
    iaa.GaussianBlur(sigma=(0, 5.0)),
    
    # Perspective transform
    iaa.PerspectiveTransform(scale=(0.01, 0.1)),
    
    # Cutout (random erasing)
    iaa.Cutout(nb_iterations=(2, 5), size=0.2, squared=False),
])

# Apply
image = cv2.imread('card.jpg')
bbs = BoundingBoxesOnImage([
    BoundingBox(x1=100, y1=150, x2=300, y2=450)
], shape=image.shape)

image_aug, bbs_aug = custom_seq(image=image, bounding_boxes=bbs)
```

---

### Conditional Augmentation

**Apply different augmentations based on conditions** :
```python
import random

def conditional_augmentation(image, class_id):
    """Apply different augmentations per class"""
    
    if class_id in [0, 1, 2]:  # Common cards
        # Light augmentation
        seq = iaa.Sequential([
            iaa.Multiply((0.8, 1.2)),
            iaa.Affine(rotate=(-10, 10)),
        ])
    
    elif class_id in [3, 4, 5]:  # Rare cards
        # Medium augmentation
        seq = iaa.Sequential([
            iaa.Multiply((0.7, 1.3)),
            iaa.Affine(rotate=(-20, 20)),
            iaa.GaussianBlur(sigma=(0, 2.0)),
        ])
    
    else:  # Ultra rare
        # Heavy augmentation + holographic
        seq = iaa.Sequential([
            iaa.Multiply((0.5, 1.5)),
            iaa.Affine(rotate=(-30, 30)),
            iaa.PerspectiveTransform(scale=(0.01, 0.05)),
        ])
    
    return seq(image=image)
```

---

### Domain-Specific Augmentation

**Simulate real-world conditions** :
```python
# Webcam detection simulation
webcam_aug = iaa.Sequential([
    # Motion blur (camera movement)
    iaa.MotionBlur(k=(3, 7)),
    
    # Low light (poor lighting)
    iaa.Multiply((0.5, 0.8)),
    
    # Noise (cheap webcam sensor)
    iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),
    
    # JPEG compression artifacts
    iaa.JpegCompression(compression=(70, 90)),
    
    # Slight rotation (hand holding phone)
    iaa.Affine(rotate=(-5, 5)),
])

# Scanner simulation
scanner_aug = iaa.Sequential([
    # High contrast
    iaa.LinearContrast((1.2, 1.5)),
    
    # Slight perspective (not perfectly flat)
    iaa.PerspectiveTransform(scale=(0.01, 0.02)),
    
    # Scan lines
    iaa.Cutout(nb_iterations=(10, 20), size=(0.01, 0.05), squared=False),
])

# Professional photo simulation
photo_aug = iaa.Sequential([
    # Good lighting
    iaa.Multiply((0.9, 1.1)),
    
    # Slight depth of field blur
    iaa.GaussianBlur(sigma=(0, 0.5)),
    
    # Color correction
    iaa.AddToHueAndSaturation((-10, 10)),
])
```

---

### Augmentation with Probability Control

**Fine-tune augmentation likelihood** :
```python
from imgaug import parameters as iap

# Probabilistic pipeline
prob_seq = iaa.Sequential([
    # 50% chance to flip
    iaa.Fliplr(0.5),
    
    # 30% chance to rotate
    iaa.Sometimes(0.3, iaa.Affine(rotate=(-15, 15))),
    
    # 70% chance to change brightness
    iaa.Sometimes(0.7, iaa.Multiply((0.8, 1.2))),
    
    # 20% chance to blur
    iaa.Sometimes(0.2, iaa.GaussianBlur(sigma=(0, 2.0))),
    
    # Always apply one of these (mutually exclusive)
    iaa.OneOf([
        iaa.AdditiveGaussianNoise(scale=(0, 0.05*255)),
        iaa.Dropout(p=(0, 0.05)),
        iaa.CoarseDropout(p=(0, 0.05), size_percent=(0.02, 0.1)),
    ]),
])
```

---

### Performance Optimization

**Batch augmentation** :
```python
import numpy as np

def augment_batch(images, bboxes_list, seq, batch_size=16):
    """Augment multiple images in batches"""
    
    results = []
    
    for i in range(0, len(images), batch_size):
        batch_images = images[i:i+batch_size]
        batch_bboxes = bboxes_list[i:i+batch_size]
        
        # Augment batch (faster than one-by-one)
        aug_images, aug_bboxes = seq(
            images=batch_images,
            bounding_boxes=batch_bboxes
        )
        
        results.extend(zip(aug_images, aug_bboxes))
    
    return results

# Usage
images = [cv2.imread(f'card_{i}.jpg') for i in range(100)]
bboxes = [...]  # List of BoundingBoxesOnImage

augmented = augment_batch(images, bboxes, custom_seq, batch_size=16)
# 2-3× faster than sequential processing
```

---

## 🔀 Multi-GPU Training

### YOLO Multi-GPU Support

**DataParallel (simple, less efficient)** :
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

# Use GPUs 0 and 1
model.train(
    data='data.yaml',
    epochs=100,
    batch=32,  # Total batch split across GPUs
    device=[0, 1],  # GPU IDs
    workers=16
)
```

**DistributedDataParallel (advanced, more efficient)** :
```python
# Requires torchrun
# Run from command line:
# torchrun --nproc_per_node=2 train_distributed.py

import torch
from ultralytics import YOLO

# train_distributed.py
def main():
    # Auto-detect local rank
    local_rank = int(os.environ.get('LOCAL_RANK', 0))
    torch.cuda.set_device(local_rank)
    
    model = YOLO('yolov8n.pt')
    model.train(
        data='data.yaml',
        epochs=100,
        batch=16,  # Per-GPU batch size
        device=local_rank,
        workers=8
    )

if __name__ == '__main__':
    main()
```

**Performance** :

| GPUs | Speedup | Efficiency | Use Case |
|------|---------|------------|----------|
| 1× RTX 3060 | 1.0× | 100% | Baseline |
| 2× RTX 3060 | 1.8× | 90% | Good |
| 4× RTX 3060 | 3.2× | 80% | Diminishing returns |

---

### Multi-GPU Augmentation

**Problem: imgaug doesn't support multi-GPU**

**Solution: Multiprocessing** :
```python
from multiprocessing import Pool, cpu_count
import imgaug.augmenters as iaa

def augment_single(args):
    """Worker function for multiprocessing"""
    image, bbox, seq = args
    aug_image, aug_bbox = seq(image=image, bounding_boxes=bbox)
    return aug_image, aug_bbox

def augment_parallel(images, bboxes, seq, num_workers=None):
    """Parallel augmentation across CPU cores"""
    
    if num_workers is None:
        num_workers = cpu_count()
    
    # Prepare args
    args_list = [(img, bb, seq) for img, bb in zip(images, bboxes)]
    
    # Parallel processing
    with Pool(num_workers) as pool:
        results = pool.map(augment_single, args_list)
    
    return results

# Usage (8× faster on 8-core CPU)
images = [...]
bboxes = [...]
seq = iaa.Sequential([...])

augmented = augment_parallel(images, bboxes, seq, num_workers=8)
```

---

## 📊 Performance Profiling

### Python Profiling

**cProfile (built-in)** :
```python
import cProfile
import pstats

# Profile function
def profile_augmentation():
    from core.augmentation import augment_images
    augment_images('images/', 'output/', count=10)

# Run profiler
cProfile.run('profile_augmentation()', 'profile_stats')

# Analyze results
p = pstats.Stats('profile_stats')
p.strip_dirs()
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 slowest functions
```

**line_profiler (detailed)** :
```batch
pip install line_profiler

# Add @profile decorator to functions
# Run
kernprof -l -v script.py
```

---

### GPU Profiling

**PyTorch Profiler** :
```python
import torch
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    profile_memory=True
) as prof:
    # Code to profile
    model.train(data='data.yaml', epochs=1)

# Print results
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=10))

# Export Chrome trace
prof.export_chrome_trace("trace.json")
# Open trace.json in chrome://tracing
```

**NVIDIA Nsight Systems** :
```batch
# Windows
nsys profile --trace=cuda,nvtx python train.py

# Generates report.qdrep
# Open in Nsight Systems GUI
```

---

### Memory Profiling

**memory_profiler** :
```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    images = []
    for i in range(1000):
        img = cv2.imread(f'card_{i}.jpg')
        images.append(img)  # Memory leak !
    return images

# Run
python -m memory_profiler script.py
```

**Output** :
```
Line #    Mem usage    Increment   Line Contents
================================================
     3     45.0 MiB     45.0 MiB   def memory_intensive_function():
     4     45.0 MiB      0.0 MiB       images = []
     5   2450.0 MiB   2405.0 MiB       for i in range(1000):
     6   2450.0 MiB      0.0 MiB           img = cv2.imread(f'card_{i}.jpg')
     7   2450.0 MiB      0.0 MiB           images.append(img)
```

---

### Benchmark Scripts

**Test mosaic performance** :
```batch
scripts\run_test.bat test_mosaic_performance
```

**Test holographic performance** :
```batch
scripts\run_test.bat test_holographic_performance
```

**Custom benchmark** :
```python
import time
import numpy as np

def benchmark_function(func, *args, iterations=10):
    """Benchmark function execution time"""
    
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    
    print(f"Average: {avg_time:.4f}s ± {std_time:.4f}s")
    print(f"Min: {np.min(times):.4f}s, Max: {np.max(times):.4f}s")
    
    return avg_time

# Usage
benchmark_function(augment_images, 'images/', 'output/', count=10)
```

---

## 🎯 Advanced YOLO Configuration

### Hyperparameter Tuning

**Learning Rate Scheduling** :
```python
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

model.train(
    data='data.yaml',
    epochs=100,
    
    # Learning rate
    lr0=0.01,  # Initial LR
    lrf=0.001,  # Final LR (epoch 100)
    
    # Momentum
    momentum=0.937,
    
    # Weight decay
    weight_decay=0.0005,
    
    # Warmup
    warmup_epochs=3.0,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
)
```

**Augmentation Hyperparameters** :
```python
model.train(
    data='data.yaml',
    
    # Spatial augmentations
    degrees=15.0,  # Rotation range
    translate=0.1,  # Translation (fraction of image)
    scale=0.5,  # Scale range (0.5 = ±50%)
    shear=0.0,  # Shear (disabled)
    perspective=0.0,  # Perspective (disabled)
    flipud=0.0,  # Vertical flip prob
    fliplr=0.5,  # Horizontal flip prob
    
    # Color augmentations
    hsv_h=0.015,  # Hue gain
    hsv_s=0.7,  # Saturation gain
    hsv_v=0.4,  # Value (brightness) gain
    
    # Mosaic augmentation
    mosaic=1.0,  # Probability (YOLO's built-in mosaic)
    mixup=0.0,  # MixUp probability
    copy_paste=0.0,  # Copy-paste augmentation
)
```

---

### Advanced Training Strategies

**Transfer Learning from Custom Checkpoint** :
```python
# Option 1: Continue from your own trained model
model = YOLO('runs/detect/train/weights/best.pt')
model.train(
    data='data_new.yaml',  # New dataset
    epochs=50,
    freeze=10,  # Freeze first 10 layers
)

# Option 2: Fine-tune last layers only
model = YOLO('yolov8n.pt')
model.train(
    data='data.yaml',
    epochs=100,
    freeze=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],  # Freeze backbone
)
```

**Early Stopping** :
```python
model.train(
    data='data.yaml',
    epochs=300,  # Max epochs
    patience=50,  # Stop if no improvement for 50 epochs
    save_period=10,  # Save checkpoint every 10 epochs
)
```

**Multi-Scale Training** :
```python
model.train(
    data='data.yaml',
    imgsz=640,  # Base size
    rect=False,  # Disable rectangular training
    # YOLO automatically uses multi-scale [640±50%]
)
```

---

### Custom Loss Functions

**Modify loss weights** :
```python
model.train(
    data='data.yaml',
    
    # Loss weights
    box=7.5,  # Box loss gain
    cls=0.5,  # Class loss gain
    dfl=1.5,  # DFL loss gain
    
    # Focal loss (for class imbalance)
    fl_gamma=0.0,  # 0 = disabled, 2.0 = strong focal
)
```

---

### Validation Strategies

**Custom validation split** :
```python
# data.yaml with custom split
"""
train: output/train/images
val: output/val/images
test: output/test/images  # Optional test set

nc: 10
names: ['class_0', 'class_1', ...]

# Custom split ratios (handled externally)
split:
  train: 0.7
  val: 0.2
  test: 0.1
"""

# Validation frequency
model.train(
    data='data.yaml',
    val=True,  # Enable validation
    plots=True,  # Generate plots
    save_json=True,  # Save COCO JSON
)
```

---

## 🐳 Docker Deployment

### Dockerfile

**CPU-only deployment** :
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY config/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch CPU
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy application
COPY . .

# Expose port (if web interface)
EXPOSE 8501

# Run application
CMD ["python", "GUI_v3.1_modern.py"]
```

**GPU-enabled deployment** :
```dockerfile
# Dockerfile.gpu
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY config/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch CUDA
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu124

COPY . .

CMD ["python3", "GUI_v3.1_modern.py"]
```

---

### Docker Compose

**docker-compose.yml** :
```yaml
version: '3.8'

services:
  pokemon-dataset-generator:
    build:
      context: .
      dockerfile: Dockerfile.gpu
    
    runtime: nvidia  # Enable GPU
    
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - PYTHONUNBUFFERED=1
    
    volumes:
      - ./images:/app/images
      - ./output:/app/output
      - ./runs:/app/runs
      - ./models:/app/models
    
    ports:
      - "8501:8501"  # If web interface
    
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Build and run** :
```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Kubernetes Deployment

**deployment.yaml** :
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pokemon-dataset-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pokemon-dataset-gen
  template:
    metadata:
      labels:
        app: pokemon-dataset-gen
    spec:
      containers:
      - name: app
        image: pokemon-dataset-generator:v3.2
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
        volumeMounts:
        - name: data
          mountPath: /app/images
        - name: output
          mountPath: /app/output
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: pokemon-data-pvc
      - name: output
        persistentVolumeClaim:
          claimName: pokemon-output-pvc
```

---

## 🔐 Security Best Practices

### API Keys Management

**Never commit API keys** :
```python
# ❌ BAD
API_KEY = "sk_live_123456789"

# ✅ GOOD
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('TCGDEX_API_KEY')
```

**.env file** :
```bash
# .env (add to .gitignore !)
TCGDEX_API_KEY=your_key_here
CARDMARKET_TOKEN=your_token_here
```

---

### Input Validation

**Prevent path traversal** :
```python
from pathlib import Path

def safe_path(user_input, base_dir='images'):
    """Validate user-provided path"""
    
    base = Path(base_dir).resolve()
    target = (base / user_input).resolve()
    
    # Ensure target is inside base_dir
    if not target.is_relative_to(base):
        raise ValueError(f"Invalid path: {user_input}")
    
    return target

# Usage
try:
    safe_file = safe_path(user_input)
except ValueError as e:
    print(f"❌ Security error: {e}")
```

---

### Sandboxing External Code

**Run untrusted code safely** :
```python
import subprocess
import tempfile

def run_sandboxed(code, timeout=30):
    """Execute Python code in isolated process"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout
    
    except subprocess.TimeoutExpired:
        return "❌ Execution timeout"
    
    finally:
        Path(temp_file).unlink()
```

---

## 📚 Additional Resources

### Official Documentation
- **Ultralytics YOLO** : [docs.ultralytics.com](https://docs.ultralytics.com)
- **imgaug** : [imgaug.readthedocs.io](https://imgaug.readthedocs.io)
- **PyTorch** : [pytorch.org/docs](https://pytorch.org/docs)
- **TCGdex API** : [api.tcgdex.net/docs](https://api.tcgdex.net/docs)

### Community
- **Ultralytics Discord** : [discord.com/invite/ultralytics](https://discord.com/invite/ultralytics)
- **YOLO Reddit** : [r/YOLO](https://reddit.com/r/YOLO)
- **Computer Vision Discord** : Various communities

### Papers
- **YOLOv8** : "YOLOv8: Real-Time Object Detection" (2023)
- **Data Augmentation** : "A survey on Image Data Augmentation" (2019)
- **Transfer Learning** : "How transferable are features in deep neural networks?" (2014)

---

**Dernière mise à jour** : 14 novembre 2025  
**Version** : 3.2

**Pour aller plus loin** :
- `docs/TECHNICAL_GUIDE.md` : Architecture détaillée
- `docs/API_REFERENCE.md` : Documentation complète API
- `docs/guides/PERFORMANCE_TUNING.md` : Guide optimisation avancée
