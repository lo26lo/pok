# 📚 API Reference - Pokémon Dataset Generator

**Version** : 3.2  
**Dernière mise à jour** : 14 novembre 2025

---

## 📋 Table des Matières

### Core Modules
1. [augmentation.py](#augmentationpy)
2. [mosaic_optimized.py](#mosaic_optimizedpy)
3. [holographic_augmenter_optimized.py](#holographic_augmenter_optimizedpy)
4. [random_erasing.py](#random_erasingpy)
5. [dataset_validator.py](#dataset_validatorpy)
6. [auto_balancer_optimized.py](#auto_balancer_optimizedpy)
7. [dataset_exporter.py](#dataset_exporterpy)
8. [workflow_manager.py](#workflow_managerpy)
9. [training_manager.py](#training_managerpy)
10. [detection_manager.py](#detection_managerpy)
11. [image_downloader.py](#image_downloaderpy)
12. [tcgdex_api.py](#tcgdex_apipy)
13. [card_mapping.py](#card_mappingpy)
14. [detection_with_prices.py](#detection_with_pricespy)
15. [utils.py](#utilspy)
16. [__init__.py](#__init__py)

---

## 🎨 augmentation.py

**Path**: `core/augmentation.py`  
**Purpose**: Image augmentation with imgaug (22 techniques)  
**Version**: 3.2

### Classes

#### `ImageAugmenter`

**Description**: Main augmentation class using imgaug pipeline.

**Constructor**:
```python
ImageAugmenter(
    count: int = 10,
    techniques: Optional[List[str]] = None,
    random_order: bool = True
)
```

**Parameters**:
- `count` (int): Number of augmentations per image. Default: 10
- `techniques` (List[str], optional): List of technique names to enable. If None, all 22 techniques enabled
- `random_order` (bool): Apply techniques in random order. Default: True

**Available Techniques**:
```python
AVAILABLE_TECHNIQUES = [
    'brightness',      # Multiply((0.5, 1.5))
    'contrast',        # LinearContrast((0.5, 1.5))
    'saturation',      # AddToHueAndSaturation((-50, 50))
    'hue',             # AddToHue((-30, 30))
    'gaussian_blur',   # GaussianBlur(sigma=(0, 2.0))
    'sharpen',         # Sharpen(alpha=(0, 1.0))
    'motion_blur',     # MotionBlur(k=(3, 7))
    'gaussian_noise',  # AdditiveGaussianNoise(scale=(0, 0.05*255))
    'dropout',         # Dropout(p=(0, 0.05))
    'coarse_dropout',  # CoarseDropout(p=(0, 0.1), size_percent=(0.02, 0.25))
    'rotation',        # Affine(rotate=(-15, 15))
    'affine',          # Affine(scale=(0.8, 1.2), translate_percent=(-0.1, 0.1))
    'perspective',     # PerspectiveTransform(scale=(0.01, 0.05))
    'elastic',         # ElasticTransformation(alpha=(0, 30), sigma=(3, 6))
    'piecewise_affine', # PiecewiseAffine(scale=(0.01, 0.03))
    'flip_horizontal', # Fliplr(0.5)
    'clahe',           # CLAHE(clip_limit=(1, 4))
    'cutout',          # Cutout(nb_iterations=(1, 3), size=(0.1, 0.3))
    'random_erasing',  # Custom random erasing
    'emboss',          # Emboss(alpha=(0, 1.0))
    'edge_detect',     # EdgeDetect(alpha=(0, 0.5))
    'add_to_brightness' # Add((-50, 50))
]
```

**Methods**:

##### `augment_image(image, bboxes=None)`
Augment single image.

```python
def augment_image(
    self,
    image: np.ndarray,
    bboxes: Optional[List[Tuple[float, float, float, float]]] = None
) -> Tuple[np.ndarray, Optional[List[Tuple[float, float, float, float]]]]
```

**Parameters**:
- `image` (np.ndarray): Input image (H, W, 3) BGR format
- `bboxes` (List[Tuple], optional): Bounding boxes [(x_min, y_min, x_max, y_max), ...]

**Returns**:
- Tuple[np.ndarray, List[Tuple]]: Augmented image and transformed bboxes

**Example**:
```python
from core.augmentation import ImageAugmenter
import cv2

augmenter = ImageAugmenter(count=5, techniques=['brightness', 'rotation'])

image = cv2.imread('card.jpg')
bboxes = [(100, 150, 300, 450)]

aug_image, aug_bboxes = augmenter.augment_image(image, bboxes)
cv2.imwrite('augmented.jpg', aug_image)
```

##### `augment_directory(input_dir, output_dir, save_labels=True)`
Augment all images in directory.

```python
def augment_directory(
    self,
    input_dir: str,
    output_dir: str,
    save_labels: bool = True
) -> Dict[str, int]
```

**Parameters**:
- `input_dir` (str): Path to input directory with images
- `output_dir` (str): Path to output directory
- `save_labels` (bool): Save YOLO labels (.txt). Default: True

**Returns**:
- Dict[str, int]: Statistics {'processed': N, 'augmented': M, 'errors': E}

**Directory Structure**:
```
input_dir/
  ├── images/
  │   ├── card1.jpg
  │   └── card2.jpg
  └── labels/  (optional)
      ├── card1.txt
      └── card2.txt

output_dir/
  ├── images/
  │   ├── card1_aug_0.jpg
  │   ├── card1_aug_1.jpg
  │   └── ...
  └── labels/
      ├── card1_aug_0.txt
      └── ...
```

**Example**:
```python
augmenter = ImageAugmenter(count=10)

stats = augmenter.augment_directory(
    input_dir='images/surging_sparks',
    output_dir='output/augmented'
)

print(f"Processed: {stats['processed']}")
print(f"Generated: {stats['augmented']}")
```

##### `get_pipeline()`
Get imgaug Sequential pipeline.

```python
def get_pipeline(self) -> iaa.Sequential
```

**Returns**:
- iaa.Sequential: Configured imgaug pipeline

**Example**:
```python
augmenter = ImageAugmenter(techniques=['brightness', 'rotation'])
pipeline = augmenter.get_pipeline()

# Use directly with imgaug
images = [img1, img2, img3]
augmented = pipeline(images=images)
```

---

### Functions

#### `load_yolo_labels(label_path)`
Load YOLO format labels.

```python
def load_yolo_labels(
    label_path: str
) -> List[Tuple[int, float, float, float, float]]
```

**Parameters**:
- `label_path` (str): Path to .txt label file

**Returns**:
- List[Tuple]: [(class_id, x_center, y_center, width, height), ...]

**YOLO Format**:
```
# card1.txt
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.25 0.35
```

**Example**:
```python
from core.augmentation import load_yolo_labels

labels = load_yolo_labels('labels/card1.txt')
# [(0, 0.5, 0.5, 0.3, 0.4), (1, 0.2, 0.3, 0.25, 0.35)]
```

#### `save_yolo_labels(labels, label_path)`
Save labels in YOLO format.

```python
def save_yolo_labels(
    labels: List[Tuple[int, float, float, float, float]],
    label_path: str
) -> None
```

**Parameters**:
- `labels` (List[Tuple]): [(class_id, x_center, y_center, width, height), ...]
- `label_path` (str): Output path

**Example**:
```python
from core.augmentation import save_yolo_labels

labels = [(0, 0.5, 0.5, 0.3, 0.4)]
save_yolo_labels(labels, 'output/labels/aug_0.txt')
```

#### `yolo_to_bbox(yolo_labels, image_shape)`
Convert YOLO format to absolute bounding boxes.

```python
def yolo_to_bbox(
    yolo_labels: List[Tuple[int, float, float, float, float]],
    image_shape: Tuple[int, int]
) -> List[Tuple[int, int, int, int, int]]
```

**Parameters**:
- `yolo_labels` (List[Tuple]): YOLO format [(class, x_c, y_c, w, h), ...]
- `image_shape` (Tuple[int, int]): (height, width)

**Returns**:
- List[Tuple]: [(class_id, x_min, y_min, x_max, y_max), ...]

**Example**:
```python
from core.augmentation import yolo_to_bbox

yolo = [(0, 0.5, 0.5, 0.3, 0.4)]  # Normalized
image_shape = (640, 640)

bboxes = yolo_to_bbox(yolo, image_shape)
# [(0, 224, 192, 416, 448)]  # Absolute pixels
```

#### `bbox_to_yolo(bboxes, image_shape)`
Convert absolute bboxes to YOLO format.

```python
def bbox_to_yolo(
    bboxes: List[Tuple[int, int, int, int, int]],
    image_shape: Tuple[int, int]
) -> List[Tuple[int, float, float, float, float]]
```

**Parameters**:
- `bboxes` (List[Tuple]): [(class, x_min, y_min, x_max, y_max), ...]
- `image_shape` (Tuple[int, int]): (height, width)

**Returns**:
- List[Tuple]: YOLO format [(class, x_c, y_c, w, h), ...]

**Example**:
```python
from core.augmentation import bbox_to_yolo

bboxes = [(0, 224, 192, 416, 448)]  # Pixels
image_shape = (640, 640)

yolo = bbox_to_yolo(bboxes, image_shape)
# [(0, 0.5, 0.5, 0.3, 0.4)]  # Normalized
```

---

### Performance

**Typical Usage**:
- 1000 images × 10 augmentations = 10,000 images
- CPU (i7): 30-50 minutes
- Memory: ~500 MB

**Optimization Tips**:
1. Reduce `count` for faster processing
2. Disable unused techniques
3. Use multiprocessing for large batches
4. Consider GPU alternatives (Albumentations, DALI)

---

## 🖼️ mosaic_optimized.py

**Path**: `core/mosaic_optimized.py`  
**Purpose**: Optimized mosaic generation (v3.2.1 - 30-60× speedup)  
**Version**: 3.2.1

### Classes

#### `MosaicGenerator`

**Description**: Generate YOLO-compatible mosaics with vectorized operations.

**Constructor**:
```python
MosaicGenerator(
    input_dir: str,
    output_dir: str,
    mosaic_size: Tuple[int, int] = (640, 640),
    cards_per_mosaic: Tuple[int, int] = (4, 8),
    background_type: str = 'mosaic',
    layout_type: str = 'grid',
    max_workers: int = 8
)
```

**Parameters**:
- `input_dir` (str): Directory with input images
- `output_dir` (str): Output directory for mosaics
- `mosaic_size` (Tuple[int, int]): Mosaic dimensions (width, height). Default: (640, 640)
- `cards_per_mosaic` (Tuple[int, int]): Range of cards per mosaic (min, max). Default: (4, 8)
- `background_type` (str): 'mosaic', 'local', or 'web'. Default: 'mosaic'
- `layout_type` (str): 'grid', 'rotation', or 'random'. Default: 'grid'
- `max_workers` (int): Number of parallel workers. Default: 8

**Methods**:

##### `generate_mosaics(num_groups=None, mode='standard')`
Generate mosaics with specified configuration.

```python
def generate_mosaics(
    self,
    num_groups: Optional[int] = None,
    mode: str = 'standard'
) -> Dict[str, Any]
```

**Parameters**:
- `num_groups` (int, optional): Number of mosaic groups to generate. If None, mode-dependent
- `mode` (str): 'quick' (200), 'standard' (500), or 'complete' (all). Default: 'standard'

**Returns**:
- Dict[str, Any]: Statistics {'generated': N, 'duration': T, 'fps': F}

**Modes**:

| Mode | Groups | Cards/Mosaic | Duration | Use Case |
|------|--------|--------------|----------|----------|
| quick | 25 | 2-4 | 2-3 min | Fast testing |
| standard | 62 | 4-6 | 5-8 min | Production |
| complete | All | 6-8 | 10-15 min | Maximum dataset |

**Example**:
```python
from core.mosaic_optimized import MosaicGenerator

generator = MosaicGenerator(
    input_dir='output/augmented',
    output_dir='output/mosaics',
    mosaic_size=(640, 640),
    cards_per_mosaic=(4, 6),
    background_type='local',
    layout_type='rotation'
)

stats = generator.generate_mosaics(mode='standard')
print(f"Generated {stats['generated']} mosaics in {stats['duration']:.1f}s")
```

##### `generate_single_mosaic(images, bboxes, background)`
Generate one mosaic from provided images.

```python
def generate_single_mosaic(
    self,
    images: List[np.ndarray],
    bboxes: List[List[Tuple[float, float, float, float]]],
    background: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, List[Tuple[int, List[Tuple[float, float]]]]]
```

**Parameters**:
- `images` (List[np.ndarray]): List of card images
- `bboxes` (List[List[Tuple]]): Bounding boxes for each image
- `background` (np.ndarray, optional): Background image. If None, generated

**Returns**:
- Tuple: (mosaic_image, polygon_annotations)

**Polygon Format**:
```python
# polygon_annotations
[
    (class_id, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]),  # 4 corners
    ...
]
```

**Example**:
```python
import cv2

img1 = cv2.imread('card1.jpg')
img2 = cv2.imread('card2.jpg')
images = [img1, img2]

bboxes = [
    [(0.2, 0.2, 0.8, 0.8)],  # Card 1 bbox
    [(0.1, 0.1, 0.9, 0.9)]   # Card 2 bbox
]

mosaic, polygons = generator.generate_single_mosaic(images, bboxes)
cv2.imwrite('mosaic.png', mosaic)
```

---

### Functions

#### `vectorized_placement(images, positions, rotations, mosaic_canvas)`
Place multiple images on canvas using vectorized operations (30× faster).

```python
def vectorized_placement(
    images: List[np.ndarray],
    positions: List[Tuple[int, int]],
    rotations: List[float],
    mosaic_canvas: np.ndarray
) -> np.ndarray
```

**Parameters**:
- `images` (List[np.ndarray]): Card images to place
- `positions` (List[Tuple[int, int]]): [(x, y), ...] positions
- `rotations` (List[float]): Rotation angles in degrees
- `mosaic_canvas` (np.ndarray): Background canvas

**Returns**:
- np.ndarray: Mosaic with placed cards

**Optimization**: Uses NumPy vectorization instead of loops (30× speedup)

---

### Performance Comparison

**v3.2.1 Optimizations** :

| Optimization | Speedup | Memory |
|--------------|---------|--------|
| Vectorization (no loops) | 15× | Same |
| Pre-allocation | 5× | -30% |
| Batch processing | 4× | +20% |
| OpenCV hardware accel | 2× | Same |
| **Total** | **30-60×** | -10% |

**Benchmarks**:
```
100 mosaics Quick:     6s (was 180s) → 30× faster
100 mosaics Standard: 12s (was 420s) → 35× faster
500 mosaics Complete: 40s (was 2400s) → 60× faster
```

---

## ✨ holographic_augmenter_optimized.py

**Path**: `core/holographic_augmenter_optimized.py`  
**Purpose**: GPU-accelerated holographic effects (v3.2.2 - 100-300× speedup)  
**Version**: 3.2.2

### Classes

#### `HolographicAugmenter`

**Description**: Apply holographic effects with GPU acceleration and LUTs.

**Constructor**:
```python
HolographicAugmenter(
    device: str = 'auto',
    use_fp16: bool = True,
    num_workers: int = 4,
    cache_lut: bool = True
)
```

**Parameters**:
- `device` (str): 'auto', 'cuda', 'cuda:0', 'cpu'. Default: 'auto'
- `use_fp16` (bool): Half-precision for GPU (2× faster). Default: True
- `num_workers` (int): CPU threads for pre/post processing. Default: 4
- `cache_lut` (bool): Cache Look-Up Tables (30% faster). Default: True

**Methods**:

##### `apply_effect(image, style='rainbow', intensity=0.7)`
Apply holographic effect to single image.

```python
def apply_effect(
    self,
    image: np.ndarray,
    style: str = 'rainbow',
    intensity: float = 0.7
) -> np.ndarray
```

**Parameters**:
- `image` (np.ndarray): Input image (H, W, 3) BGR
- `style` (str): 'rainbow', 'metallic', 'glitter', 'prismatic', 'sparkle'. Default: 'rainbow'
- `intensity` (float): Effect intensity [0.1, 1.0]. Default: 0.7

**Returns**:
- np.ndarray: Image with holographic effect

**Example**:
```python
from core.holographic_augmenter_optimized import HolographicAugmenter
import cv2

augmenter = HolographicAugmenter(device='cuda')

image = cv2.imread('card.jpg')
holo = augmenter.apply_effect(image, style='rainbow', intensity=0.8)

cv2.imwrite('card_holo.jpg', holo)
```

##### `apply_batch(images, style='rainbow', intensity=0.7, batch_size=16)`
Apply effect to multiple images (batch processing).

```python
def apply_batch(
    self,
    images: List[np.ndarray],
    style: str = 'rainbow',
    intensity: float = 0.7,
    batch_size: int = 16
) -> List[np.ndarray]
```

**Parameters**:
- `images` (List[np.ndarray]): List of images
- `style` (str): Effect style
- `intensity` (float): Effect intensity
- `batch_size` (int): Process N images at once. Default: 16

**Returns**:
- List[np.ndarray]: List of augmented images

**Example**:
```python
images = [cv2.imread(f'card_{i}.jpg') for i in range(100)]

holo_images = augmenter.apply_batch(
    images,
    style='metallic',
    intensity=0.6,
    batch_size=32  # RTX 3060: 32-64 optimal
)
```

##### `augment_directory(input_dir, output_dir, variations=5)`
Augment all images in directory with multiple styles.

```python
def augment_directory(
    self,
    input_dir: str,
    output_dir: str,
    variations: int = 5
) -> Dict[str, int]
```

**Parameters**:
- `input_dir` (str): Input directory path
- `output_dir` (str): Output directory path
- `variations` (int): Number of style variations per image. Default: 5

**Returns**:
- Dict[str, int]: {'processed': N, 'generated': M}

**Example**:
```python
stats = augmenter.augment_directory(
    input_dir='images/',
    output_dir='images_holographic/',
    variations=5  # All 5 styles
)

print(f"Generated {stats['generated']} holographic images")
```

---

### Holographic Styles

**1. Rainbow** 🌈
```python
# Multi-color gradient overlay
# HSV hue shift [0-180]
# Intensity: 0.1-1.0 (0.7 optimal)
```

**2. Metallic** 🔩
```python
# Silver/chrome reflections
# Radial gradients
# Intensity: 0.3-0.9 (0.6 optimal)
```

**3. Glitter** ✨
```python
# Sparkle patterns
# High-frequency noise
# Intensity: 0.5-1.0 (0.8 optimal)
```

**4. Prismatic** 💎
```python
# Chromatic aberration
# Multi-color prisms
# Intensity: 0.4-0.8 (0.6 optimal)
```

**5. Sparkle** ⭐
```python
# Star patterns
# Bright spots
# Intensity: 0.6-1.0 (0.7 optimal)
```

---

### Performance

**v3.2.2 Optimizations**:

| Optimization | Speedup |
|--------------|---------|
| GPU CUDA kernels | 50× |
| LUT pre-computation | 3× |
| Separable filters (2D→2×1D) | 2× |
| Half-precision FP16 | 2× |
| Multi-threading | 1.5× |
| **Total** | **100-300×** |

**Benchmarks (RTX 3060)**:

| Style | Before | After | Speedup |
|-------|--------|-------|---------|
| Rainbow | 2.5s | 0.025s | 100× |
| Metallic | 3.0s | 0.01s | 300× |
| Glitter | 1.8s | 0.015s | 120× |
| Prismatic | 4.2s | 0.018s | 233× |
| Sparkle | 2.0s | 0.012s | 167× |

**1000 images, 5 styles**: 3000s → 15s (5 min → 15 sec)

---

## 🎲 random_erasing.py

**Path**: `core/random_erasing.py`  
**Purpose**: Random erasing augmentation with Perlin noise backgrounds  
**Version**: 3.2

### Functions

#### `generate_perlin_background(width, height, scale=10)`
Generate Perlin noise background.

```python
def generate_perlin_background(
    width: int,
    height: int,
    scale: int = 10
) -> np.ndarray
```

**Parameters**:
- `width` (int): Image width
- `height` (int): Image height
- `scale` (int): Noise frequency (higher = smoother). Default: 10

**Returns**:
- np.ndarray: RGB image (H, W, 3)

**Example**:
```python
from core.random_erasing import generate_perlin_background
import cv2

bg = generate_perlin_background(640, 640, scale=8)
cv2.imwrite('perlin_bg.png', bg)
```

#### `random_erasing(image, probability=0.5, min_area=0.02, max_area=0.4, min_aspect=0.3, max_attempt=100)`
Apply random erasing augmentation.

```python
def random_erasing(
    image: np.ndarray,
    probability: float = 0.5,
    min_area: float = 0.02,
    max_area: float = 0.4,
    min_aspect: float = 0.3,
    max_attempt: int = 100
) -> np.ndarray
```

**Parameters**:
- `image` (np.ndarray): Input image
- `probability` (float): Probability of applying [0, 1]. Default: 0.5
- `min_area` (float): Min erase area (fraction). Default: 0.02 (2%)
- `max_area` (float): Max erase area (fraction). Default: 0.4 (40%)
- `min_aspect` (float): Min aspect ratio. Default: 0.3
- `max_attempt` (int): Max attempts to find valid region. Default: 100

**Returns**:
- np.ndarray: Image with random regions erased

**Example**:
```python
from core.random_erasing import random_erasing
import cv2

image = cv2.imread('card.jpg')
erased = random_erasing(image, probability=0.8, max_area=0.3)

cv2.imwrite('card_erased.jpg', erased)
```

---

## ✅ dataset_validator.py

**Path**: `core/dataset_validator.py`  
**Purpose**: Validate YOLO dataset with 5 checks + HTML report  
**Version**: 3.2

### Classes

#### `DatasetValidator`

**Description**: Comprehensive YOLO dataset validation.

**Constructor**:
```python
DatasetValidator(
    dataset_path: str,
    output_report: str = 'validation_report.html'
)
```

**Parameters**:
- `dataset_path` (str): Path to YOLO dataset root
- `output_report` (str): HTML report output path. Default: 'validation_report.html'

**Methods**:

##### `validate()`
Run all 5 validation checks.

```python
def validate(self) -> Dict[str, Any]
```

**Returns**:
- Dict[str, Any]: Validation results with errors/warnings

**Checks Performed**:
1. **Image Integrity**: Corrupted images, invalid formats, size < 32×32
2. **Label Integrity**: YOLO format errors, values out of [0, 1]
3. **Class Distribution**: Imbalance > 5:1 ratio
4. **Annotation Quality**: Bboxes < 1% image, overlaps > 80%
5. **Data Consistency**: Orphaned images/labels

**Example**:
```python
from core.dataset_validator import DatasetValidator

validator = DatasetValidator(
    dataset_path='output/mosaics',
    output_report='validation_report.html'
)

results = validator.validate()

print(f"Errors: {results['total_errors']}")
print(f"Warnings: {results['total_warnings']}")

# HTML report auto-opens in browser
```

##### `check_image_integrity()`
Check image files integrity.

```python
def check_image_integrity(self) -> List[Dict[str, str]]
```

**Returns**:
- List[Dict]: [{'file': 'card.jpg', 'error': 'Corrupted'}, ...]

##### `check_label_integrity()`
Check YOLO label format.

```python
def check_label_integrity(self) -> List[Dict[str, str]]
```

**Returns**:
- List[Dict]: [{'file': 'card.txt', 'line': 3, 'error': 'Invalid bbox'}, ...]

##### `check_class_distribution(threshold=5.0)`
Check class imbalance.

```python
def check_class_distribution(
    self,
    threshold: float = 5.0
) -> Dict[str, Any]
```

**Parameters**:
- `threshold` (float): Imbalance ratio threshold. Default: 5.0 (5:1)

**Returns**:
- Dict: {'imbalanced': bool, 'ratios': {...}, 'distribution': {...}}

**Example**:
```python
dist = validator.check_class_distribution(threshold=3.0)

if dist['imbalanced']:
    print("⚠️ Dataset imbalanced!")
    print(f"Ratios: {dist['ratios']}")
    # Recommend auto-balancing
```

---

### HTML Report

**Generated Report Contains**:
- ✅ Summary table (errors/warnings count)
- 📊 Class distribution chart
- 📝 Detailed error list with file paths
- 🎨 Color-coded severity (red=error, yellow=warning)
- 🔍 Recommendations for fixes

**Auto-opens in default browser after validation**

---

## ⚖️ auto_balancer_optimized.py

**Path**: `core/auto_balancer_optimized.py`  
**Purpose**: Balance YOLO dataset class distribution  
**Version**: 3.2

### Classes

#### `AutoBalancer`

**Description**: Automatically balance dataset using 3 strategies.

**Constructor**:
```python
AutoBalancer(
    dataset_path: str,
    target_count: Optional[int] = None,
    strategy: str = 'combined'
)
```

**Parameters**:
- `dataset_path` (str): Path to YOLO dataset
- `target_count` (int, optional): Target images per class. If None, use median
- `strategy` (str): 'upsampling', 'downsampling', or 'combined'. Default: 'combined'

**Methods**:

##### `balance()`
Execute balancing strategy.

```python
def balance(self) -> Dict[str, Any]
```

**Returns**:
- Dict: {'initial_distribution': {...}, 'final_distribution': {...}, 'duration': T}

**Example**:
```python
from core.auto_balancer_optimized import AutoBalancer

balancer = AutoBalancer(
    dataset_path='output/mosaics',
    target_count=50,
    strategy='combined'
)

stats = balancer.balance()

print(f"Before: {stats['initial_distribution']}")
print(f"After: {stats['final_distribution']}")
print(f"Duration: {stats['duration']:.1f}s")
```

---

### Strategies

**1. Upsampling** (Augment minorities)
- Duplicate minority classes
- Apply augmentation to duplicates
- Duration: 20-30 min (1000 images)
- Use case: Small dataset

**2. Downsampling** (Reduce majorities)
- Random sampling of majority classes
- No augmentation needed
- Duration: 10 sec
- Use case: Large dataset, limited compute

**3. Combined** (Recommended)
- Upsample minorities + downsample majorities
- Balanced result
- Duration: 25-35 min
- Use case: Production

**Performance**:
```
Before: Class 0: 500, Class 1: 50, Class 2: 200
Target: 150 per class

After: Class 0: 150, Class 1: 150, Class 2: 150
Duration: 28 minutes (combined strategy)
```

---

## 📦 dataset_exporter.py

**Path**: `core/dataset_exporter.py`  
**Purpose**: Export YOLO dataset to 4 formats (COCO, VOC, TFRecord, Roboflow)  
**Version**: 3.2

### Classes

#### `DatasetExporter`

**Description**: Multi-format dataset exporter.

**Constructor**:
```python
DatasetExporter(
    dataset_path: str,
    output_path: str,
    format: str = 'coco',
    splits: Tuple[float, float, float] = (0.7, 0.2, 0.1)
)
```

**Parameters**:
- `dataset_path` (str): Input YOLO dataset path
- `output_path` (str): Output directory
- `format` (str): 'coco', 'voc', 'tfrecord', 'roboflow'. Default: 'coco'
- `splits` (Tuple[float, float, float]): (train, val, test) ratios. Default: (0.7, 0.2, 0.1)

**Methods**:

##### `export()`
Export dataset to specified format.

```python
def export(self) -> Dict[str, Any]
```

**Returns**:
- Dict: {'format': str, 'files': [...], 'duration': float}

**Example**:
```python
from core.dataset_exporter import DatasetExporter

exporter = DatasetExporter(
    dataset_path='output/mosaics',
    output_path='exports/coco',
    format='coco',
    splits=(0.8, 0.1, 0.1)  # 80-10-10 split
)

result = exporter.export()
print(f"Exported {len(result['files'])} files in {result['duration']:.1f}s")
```

---

### Export Formats

#### COCO JSON
```python
exporter = DatasetExporter(dataset_path='...', format='coco')
exporter.export()

# Output:
# exports/coco/
#   ├── instances_train.json
#   ├── instances_val.json
#   └── instances_test.json
```

**JSON Structure**:
```json
{
  "images": [
    {"id": 1, "file_name": "card1.jpg", "width": 640, "height": 640}
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [100, 150, 200, 300],
      "area": 60000,
      "iscrowd": 0
    }
  ],
  "categories": [
    {"id": 0, "name": "class_0", "supercategory": "pokemon"}
  ]
}
```

#### Pascal VOC XML
```python
exporter = DatasetExporter(dataset_path='...', format='voc')
exporter.export()

# Output: 1 XML per image
# exports/voc/
#   ├── Annotations/
#   │   ├── card1.xml
#   │   └── card2.xml
#   └── ImageSets/
#       └── Main/
#           ├── train.txt
#           ├── val.txt
#           └── test.txt
```

**XML Structure**:
```xml
<annotation>
  <filename>card1.jpg</filename>
  <size>
    <width>640</width>
    <height>640</height>
  </size>
  <object>
    <name>class_0</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>150</ymin>
      <xmax>300</xmax>
      <ymax>450</ymax>
    </bndbox>
  </object>
</annotation>
```

#### TFRecord (TensorFlow)
```python
exporter = DatasetExporter(dataset_path='...', format='tfrecord')
exporter.export()

# Output: Binary files
# exports/tfrecord/
#   ├── train.tfrecord
#   ├── val.tfrecord
#   └── test.tfrecord
```

**Loading in TensorFlow**:
```python
import tensorflow as tf

dataset = tf.data.TFRecordDataset('train.tfrecord')
for example in dataset.take(1):
    parsed = tf.train.Example.FromString(example.numpy())
    # Access image, bbox, class
```

#### Roboflow
```python
exporter = DatasetExporter(dataset_path='...', format='roboflow')
exporter.export()

# Output: YOLO + metadata
# exports/roboflow/
#   ├── train/
#   │   ├── images/
#   │   └── labels/
#   ├── val/
#   ├── test/
#   └── data.yaml
```

---

## 🔄 workflow_manager.py

**Path**: `core/workflow_manager.py`  
**Purpose**: Orchestrate 5-step pipeline (augmentation → holographic → mosaics → validation → training)  
**Version**: 3.2

### Classes

#### `WorkflowManager`

**Description**: Automated workflow executor.

**Constructor**:
```python
WorkflowManager(
    config: WorkflowConfig,
    callbacks: Optional[List[Callable]] = None
)
```

**Parameters**:
- `config` (WorkflowConfig): Workflow configuration dataclass
- `callbacks` (List[Callable], optional): Progress callbacks

**Methods**:

##### `execute()`
Execute complete workflow.

```python
def execute(self) -> Dict[str, Any]
```

**Returns**:
- Dict: {'steps': [...], 'total_duration': T, 'success': bool}

**Example**:
```python
from core.workflow_manager import WorkflowManager, WorkflowConfig

config = WorkflowConfig(
    input_dir='images/surging_sparks',
    num_augmentations=10,
    mosaic_mode='standard',
    enable_holographic=True,
    enable_validation=True,
    enable_auto_balance=True,
    enable_training=False
)

workflow = WorkflowManager(config)
result = workflow.execute()

print(f"Success: {result['success']}")
print(f"Total duration: {result['total_duration']:.1f}s")

for step in result['steps']:
    print(f"{step['name']}: {step['duration']:.1f}s")
```

---

### WorkflowConfig

**Dataclass**:
```python
@dataclass
class WorkflowConfig:
    # Input
    input_dir: str
    
    # Augmentation
    num_augmentations: int = 10
    augmentation_techniques: Optional[List[str]] = None
    
    # Holographic
    enable_holographic: bool = False
    holographic_intensity: float = 0.7
    holographic_variations: int = 3
    
    # Mosaics
    mosaic_mode: str = 'standard'  # 'quick', 'standard', 'complete'
    mosaic_layout: str = 'rotation'
    mosaic_background: str = 'local'
    
    # Validation
    enable_validation: bool = True
    
    # Auto-balance
    enable_auto_balance: bool = False
    balance_target: Optional[int] = None
    balance_strategy: str = 'combined'
    
    # Training
    enable_training: bool = False
    training_epochs: int = 50
    training_model: str = 'yolov8n'
```

---

### Pipeline Steps

**Step 1: Augmentation** (30-60 min)
- imgaug 22 techniques
- Output: `output/augmented/`

**Step 2: Holographic** (5-10 min, optional)
- 5 holographic styles
- Output: `output/holographic/`

**Step 3: Mosaics** (5-15 min)
- Vectorized generation
- Output: `output/mosaics/`

**Step 4: Validation + Balance** (10-20 min)
- 5 validation checks
- Auto-balance if enabled
- Output: `validation_report.html`

**Step 5: Training** (2-8h, optional)
- YOLOv8/v11 training
- Output: `runs/detect/train/`

**Total Duration**:
- Without training: 1-2h
- With training: 3-10h

---

## 🎓 training_manager.py

**Path**: `core/training_manager.py`  
**Purpose**: YOLO training wrapper (YOLOv8/v11)  
**Version**: 3.2

### Classes

#### `TrainingManager`

**Description**: Manage YOLO model training.

**Constructor**:
```python
TrainingManager(
    config: TrainingConfig
)
```

**Parameters**:
- `config` (TrainingConfig): Training configuration dataclass

**Methods**:

##### `train()`
Start training with configuration.

```python
def train(self) -> Dict[str, Any]
```

**Returns**:
- Dict: {'best_model': str, 'metrics': {...}, 'duration': float}

**Example**:
```python
from core.training_manager import TrainingManager, TrainingConfig

config = TrainingConfig(
    data_yaml='output/mosaics/data.yaml',
    model='yolov8n',
    epochs=50,
    batch_size=16,
    image_size=640,
    device='auto',
    project='runs/detect',
    name='pokemon_detector'
)

manager = TrainingManager(config)
result = manager.train()

print(f"Best model: {result['best_model']}")
print(f"mAP50: {result['metrics']['mAP50']:.3f}")
```

##### `resume(checkpoint_path)`
Resume training from checkpoint.

```python
def resume(
    self,
    checkpoint_path: str
) -> Dict[str, Any]
```

**Parameters**:
- `checkpoint_path` (str): Path to `last.pt` checkpoint

**Example**:
```python
result = manager.resume('runs/detect/train/weights/last.pt')
```

---

### TrainingConfig

**Dataclass**:
```python
@dataclass
class TrainingConfig:
    # Required
    data_yaml: str
    model: str  # 'yolov8n', 'yolov8s', 'yolo11n', etc.
    
    # Training params
    epochs: int = 50
    batch_size: int = 16
    image_size: int = 640
    device: str = 'auto'
    workers: int = 8
    
    # Optimization
    optimizer: str = 'AdamW'
    lr0: float = 0.01
    lrf: float = 0.001
    momentum: float = 0.937
    weight_decay: float = 0.0005
    
    # Augmentation
    augment: bool = True
    mosaic: float = 1.0
    mixup: float = 0.0
    
    # Output
    project: str = 'runs/detect'
    name: str = 'train'
    exist_ok: bool = False
    
    # Advanced
    cache: Union[bool, str] = False  # False, True, 'ram', 'disk'
    pretrained: bool = True
    amp: bool = True  # Mixed precision
    patience: int = 50  # Early stopping
```

---

### Metrics Extraction

**Extract metrics from results**:
```python
metrics = manager.get_metrics('runs/detect/train')

print(f"Precision: {metrics['precision']:.3f}")
print(f"Recall: {metrics['recall']:.3f}")
print(f"mAP50: {metrics['mAP50']:.3f}")
print(f"mAP50-95: {metrics['mAP50-95']:.3f}")
```

---

## 🔍 detection_manager.py

**Path**: `core/detection_manager.py`  
**Purpose**: Real-time detection (webcam/video/image)  
**Version**: 3.2

### Classes

#### `DetectionManager`

**Description**: Manage YOLO inference.

**Constructor**:
```python
DetectionManager(
    model_path: str,
    confidence: float = 0.25,
    iou_threshold: float = 0.45,
    device: str = 'auto'
)
```

**Parameters**:
- `model_path` (str): Path to `.pt` model
- `confidence` (float): Confidence threshold [0, 1]. Default: 0.25
- `iou_threshold` (float): IoU threshold for NMS. Default: 0.45
- `device` (str): 'auto', 'cuda', 'cpu'. Default: 'auto'

**Methods**:

##### `detect_webcam(camera_id=0, show_fps=True)`
Real-time webcam detection.

```python
def detect_webcam(
    self,
    camera_id: int = 0,
    show_fps: bool = True
) -> None
```

**Parameters**:
- `camera_id` (int): Webcam ID (0, 1, 2, ...). Default: 0
- `show_fps` (bool): Display FPS counter. Default: True

**Keyboard Shortcuts**:
- `q` : Quit
- `s` : Save screenshot
- `p` : Pause/Resume

**Example**:
```python
from core.detection_manager import DetectionManager

detector = DetectionManager(
    model_path='runs/detect/train/weights/best.pt',
    confidence=0.3,
    iou_threshold=0.5
)

detector.detect_webcam(camera_id=0, show_fps=True)
```

##### `detect_video(video_path, output_path=None)`
Process video file.

```python
def detect_video(
    self,
    video_path: str,
    output_path: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `video_path` (str): Input video path
- `output_path` (str, optional): Output video path. If None, auto-generated

**Returns**:
- Dict: {'output_path': str, 'frames_processed': int, 'duration': float}

**Example**:
```python
result = detector.detect_video(
    video_path='test_video.mp4',
    output_path='output_annotated.mp4'
)

print(f"Processed {result['frames_processed']} frames")
print(f"Output: {result['output_path']}")
```

##### `detect_image(image_path, output_path=None)`
Detect on single image.

```python
def detect_image(
    self,
    image_path: str,
    output_path: Optional[str] = None
) -> Tuple[np.ndarray, List[Dict]]
```

**Parameters**:
- `image_path` (str): Input image path
- `output_path` (str, optional): Output image path

**Returns**:
- Tuple: (annotated_image, detections)

**Detections Format**:
```python
[
    {
        'class_id': 0,
        'class_name': 'Pikachu',
        'confidence': 0.95,
        'bbox': [100, 150, 300, 450],  # x1, y1, x2, y2
    },
    ...
]
```

**Example**:
```python
annotated, detections = detector.detect_image(
    image_path='test.jpg',
    output_path='result.jpg'
)

for det in detections:
    print(f"{det['class_name']}: {det['confidence']:.2f}")
```

---

## 📥 image_downloader.py

**Path**: `core/image_downloader.py`  
**Purpose**: Download Pokémon TCG images from TCGdex API  
**Version**: 3.2

### Classes

#### `ImageDownloader`

**Description**: Download images with parallel processing.

**Constructor**:
```python
ImageDownloader(
    output_dir: str = 'images',
    max_workers: int = 5,
    retry_count: int = 3
)
```

**Parameters**:
- `output_dir` (str): Output directory. Default: 'images'
- `max_workers` (int): Parallel download threads. Default: 5
- `retry_count` (int): Retry failed downloads. Default: 3

**Methods**:

##### `download_set(set_id, language='en')`
Download all cards from set.

```python
def download_set(
    self,
    set_id: str,
    language: str = 'en'
) -> Dict[str, Any]
```

**Parameters**:
- `set_id` (str): TCGdex set ID (e.g., 'sv08', 'sv01')
- `language` (str): 'en', 'fr', 'de', 'es', 'it', 'pt', 'ja', 'ko', 'zh-tw', 'pl'. Default: 'en'

**Returns**:
- Dict: {'downloaded': N, 'failed': M, 'duration': T}

**Example**:
```python
from core.image_downloader import ImageDownloader

downloader = ImageDownloader(
    output_dir='images/surging_sparks',
    max_workers=10
)

result = downloader.download_set('sv08', language='en')
print(f"Downloaded {result['downloaded']} images")
```

##### `download_card(card_id, language='en')`
Download single card.

```python
def download_card(
    self,
    card_id: str,
    language: str = 'en'
) -> bool
```

**Parameters**:
- `card_id` (str): TCGdex card ID (e.g., 'sv08_001')
- `language` (str): Language code

**Returns**:
- bool: True if success, False if failed

**Example**:
```python
success = downloader.download_card('sv08_019', language='fr')
```

---

### Supported Sets

**Popular Sets (2023-2025)**:
```python
SUPPORTED_SETS = {
    'sv08': 'Surging Sparks',
    'sv07': 'Stellar Crown',
    'sv06': 'Twilight Masquerade',
    'sv05': 'Temporal Forces',
    'sv04': 'Paradox Rift',
    'sv03': 'Obsidian Flames',
    'sv02': 'Paldea Evolved',
    'sv01': 'Scarlet & Violet',
    'swsh12.5': 'Crown Zenith',
    'swsh12': 'Silver Tempest',
    'swsh11': 'Lost Origin',
    'swsh10': 'Astral Radiance',
}
```

---

## 🌐 tcgdex_api.py

**Path**: `core/tcgdex_api.py`  
**Purpose**: TCGdex API v2 client  
**Version**: 3.2

### Classes

#### `TCGdexClient`

**Description**: API client for TCGdex.

**Constructor**:
```python
TCGdexClient(
    language: str = 'en',
    base_url: str = 'https://api.tcgdex.net/v2'
)
```

**Parameters**:
- `language` (str): Default language. Default: 'en'
- `base_url` (str): API base URL

**Methods**:

##### `get_set(set_id)`
Get set information.

```python
def get_set(
    self,
    set_id: str
) -> Dict[str, Any]
```

**Returns**:
```python
{
    'id': 'sv08',
    'name': 'Surging Sparks',
    'release_date': '2024-11-08',
    'card_count': 252,
    'logo': 'https://...',
}
```

##### `get_card(card_id)`
Get card details.

```python
def get_card(
    self,
    card_id: str
) -> Dict[str, Any]
```

**Returns**:
```python
{
    'id': 'sv08_019',
    'name': 'Ho-Oh',
    'set': {'id': 'sv08', 'name': 'Surging Sparks'},
    'image': {
        'small': 'https://...jpg',
        'large': 'https://...png'
    },
    'rarity': 'Rare',
    'hp': 130,
    'types': ['Fire', 'Flying'],
    'prices': {
        'cardmarket': {'avg': 2.5, 'trend': 3.0},
        'tcgplayer': {'market': 3.5, 'low': 2.0}
    }
}
```

##### `search_cards(query, filters=None)`
Search cards.

```python
def search_cards(
    self,
    query: str,
    filters: Optional[Dict] = None
) -> List[Dict]
```

**Parameters**:
- `query` (str): Search query (card name)
- `filters` (Dict, optional): {'set': 'sv08', 'type': 'Fire', ...}

**Example**:
```python
from core.tcgdex_api import TCGdexClient

client = TCGdexClient(language='en')

# Search
results = client.search_cards('Pikachu', filters={'set': 'sv08'})

for card in results:
    print(f"{card['name']} - {card['id']}")
```

---

## 🗺️ card_mapping.py

**Path**: `core/card_mapping.py`  
**Purpose**: Map class IDs to card names/IDs  
**Version**: 3.2

### Functions

#### `create_card_mapping(images_dir, output_file='models/card_name_to_id.json')`
Create mapping from image filenames.

```python
def create_card_mapping(
    images_dir: str,
    output_file: str = 'models/card_name_to_id.json'
) -> Dict[str, str]
```

**Parameters**:
- `images_dir` (str): Directory with card images
- `output_file` (str): Output JSON path

**Returns**:
- Dict[str, str]: {'Card_Name': 'set_cardnumber', ...}

**Example**:
```python
from core.card_mapping import create_card_mapping

mapping = create_card_mapping('images/surging_sparks')
# {'Ho-Oh': 'sv08_019', 'Pikachu': 'sv08_001', ...}

# Saved to models/card_name_to_id.json
```

#### `load_card_mapping(mapping_file='models/card_name_to_id.json')`
Load existing mapping.

```python
def load_card_mapping(
    mapping_file: str = 'models/card_name_to_id.json'
) -> Dict[str, str]
```

**Returns**:
- Dict[str, str]: Card name → ID mapping

---

## 💰 detection_with_prices.py

**Path**: `core/detection_with_prices.py`  
**Purpose**: Detection with price overlay  
**Version**: 3.2

### Classes

#### `DetectionWithPrices`

**Description**: Extend DetectionManager with price display.

**Constructor**:
```python
DetectionWithPrices(
    model_path: str,
    cards_database: str = 'models/cards_database.yaml',
    card_mapping: str = 'models/card_name_to_id.json',
    show_prices: bool = True
)
```

**Methods**:

##### `detect_with_prices(image)`
Detect and overlay prices.

```python
def detect_with_prices(
    self,
    image: np.ndarray
) -> Tuple[np.ndarray, List[Dict]]
```

**Returns**:
```python
(annotated_image, [
    {
        'class_name': 'Charizard ex',
        'confidence': 0.95,
        'bbox': [100, 150, 300, 450],
        'price': 120.0,
        'price_currency': 'EUR'
    },
    ...
])
```

**Example**:
```python
from core.detection_with_prices import DetectionWithPrices
import cv2

detector = DetectionWithPrices(
    model_path='runs/detect/train/weights/best.pt',
    show_prices=True
)

image = cv2.imread('test.jpg')
annotated, detections = detector.detect_with_prices(image)

cv2.imshow('Result', annotated)
cv2.waitKey(0)
```

---

## 🛠️ utils.py

**Path**: `core/utils.py`  
**Purpose**: Utility functions  
**Version**: 3.2

### Functions

#### `safe_print(text, encoding='utf-8', errors='replace')`
Safe print for Unicode characters.

```python
def safe_print(
    text: str,
    encoding: str = 'utf-8',
    errors: str = 'replace'
) -> None
```

**Example**:
```python
from core.utils import safe_print

safe_print("✅ Génération terminée")  # Works on all consoles
```

#### `ensure_dir(path)`
Create directory if not exists.

```python
def ensure_dir(
    path: Union[str, Path]
) -> Path
```

**Example**:
```python
from core.utils import ensure_dir

output_dir = ensure_dir('output/mosaics')
```

#### `load_card_data(yaml_path='models/cards_database.yaml')`
Load card database.

```python
def load_card_data(
    yaml_path: str = 'models/cards_database.yaml'
) -> List[Dict]
```

**Returns**:
- List[Dict]: [{'name': 'Pikachu', 'price': 2.5, ...}, ...]

#### `extract_card_number(filename)`
Extract card number from filename.

```python
def extract_card_number(
    filename: str
) -> Optional[str]
```

**Patterns**:
- `sv08_019.jpg` → `sv08_019`
- `Pikachu_sv08_019.png` → `sv08_019`
- `card_019.jpg` → `019`

**Example**:
```python
from core.utils import extract_card_number

card_id = extract_card_number('Ho-Oh_sv08_019.jpg')
# 'sv08_019'
```

#### `validate_yolo_label(label_line)`
Validate YOLO format line.

```python
def validate_yolo_label(
    label_line: str
) -> Tuple[bool, Optional[str]]
```

**Returns**:
- Tuple[bool, str]: (is_valid, error_message)

**Example**:
```python
from core.utils import validate_yolo_label

valid, error = validate_yolo_label("0 0.5 0.5 0.3 0.4")
# (True, None)

valid, error = validate_yolo_label("0 1.5 0.5 0.3 0.4")
# (False, "x_center out of range [0, 1]")
```

---

## 📦 __init__.py

**Path**: `core/__init__.py`  
**Purpose**: Package initialization  
**Version**: 3.2

**Exports**:
```python
from core.augmentation import ImageAugmenter
from core.mosaic_optimized import MosaicGenerator
from core.holographic_augmenter_optimized import HolographicAugmenter
from core.dataset_validator import DatasetValidator
from core.auto_balancer_optimized import AutoBalancer
from core.dataset_exporter import DatasetExporter
from core.workflow_manager import WorkflowManager
from core.training_manager import TrainingManager
from core.detection_manager import DetectionManager
from core.image_downloader import ImageDownloader
from core.tcgdex_api import TCGdexClient
from core.utils import safe_print, ensure_dir, load_card_data

__all__ = [
    'ImageAugmenter',
    'MosaicGenerator',
    'HolographicAugmenter',
    'DatasetValidator',
    'AutoBalancer',
    'DatasetExporter',
    'WorkflowManager',
    'TrainingManager',
    'DetectionManager',
    'ImageDownloader',
    'TCGdexClient',
    'safe_print',
    'ensure_dir',
    'load_card_data',
]

__version__ = '3.2'
```

**Usage**:
```python
# Import from core
from core import ImageAugmenter, MosaicGenerator

# Or individual imports
from core.augmentation import ImageAugmenter
```

---

## 📚 Complete Example

**Full workflow using API**:
```python
from core import (
    ImageDownloader,
    ImageAugmenter,
    HolographicAugmenter,
    MosaicGenerator,
    DatasetValidator,
    AutoBalancer,
    TrainingManager,
    DetectionManager
)

# 1. Download images
downloader = ImageDownloader('images/surging_sparks')
downloader.download_set('sv08', language='en')

# 2. Augment
augmenter = ImageAugmenter(count=10)
augmenter.augment_directory('images/surging_sparks', 'output/augmented')

# 3. Holographic effects
holo = HolographicAugmenter(device='cuda')
holo.augment_directory('output/augmented', 'output/holographic', variations=3)

# 4. Generate mosaics
mosaic_gen = MosaicGenerator('output/holographic', 'output/mosaics')
mosaic_gen.generate_mosaics(mode='standard')

# 5. Validate
validator = DatasetValidator('output/mosaics')
validator.validate()

# 6. Balance
balancer = AutoBalancer('output/mosaics', target_count=50)
balancer.balance()

# 7. Train
from core.training_manager import TrainingConfig
config = TrainingConfig(
    data_yaml='output/mosaics/data.yaml',
    model='yolov8n',
    epochs=50
)
trainer = TrainingManager(config)
trainer.train()

# 8. Detect
detector = DetectionManager('runs/detect/train/weights/best.pt')
detector.detect_webcam()
```

---

**Dernière mise à jour** : 14 novembre 2025  
**Version** : 3.2

**Documentation connexe** :
- `docs/USER_GUIDE.md` : Guide utilisateur complet
- `docs/TECHNICAL_GUIDE.md` : Architecture technique
- `docs/ADVANCED.md` : Optimisations avancées
