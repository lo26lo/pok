# 🚀 Pokémon Dataset Generator - Detailed Features

This document provides an in-depth overview of all features in the Pokémon Dataset Generator v3.1.

---

## 📋 Table of Contents

1. [Card Mapping & Price Detection](#card-mapping--price-detection)
2. [Image Download & Management](#image-download--management)
3. [Advanced Augmentation](#advanced-augmentation)
4. [Mosaic Generation](#mosaic-generation)
5. [YOLO Training](#yolo-training)
6. [Live Detection](#live-detection)
7. [Dataset Management](#dataset-management)
8. [Testing & Validation](#testing--validation)
9. [Workflow Optimization](#workflow-optimization)

---

## 💰 Card Mapping & Price Detection

### Overview
The card mapping and price detection system allows real-time price display during YOLO detection, automatically mapping detected class names to TCGdex card IDs and fetching their market prices.

### Components

#### 1. Card Mapping System (`core/card_mapping.py`)
**Purpose**: Map YOLO class names to TCGdex card IDs

**Features**:
- Automatic mapping via `card_name_to_id.json`
- Fallback to class name if no mapping exists
- Case-insensitive matching
- Support for special characters and variations

**Usage**:
```python
from core.card_mapping import get_card_id_from_class_name

card_id = get_card_id_from_class_name("Pikachu_ex")
# Returns: "sv08-025" (mapped ID) or "Pikachu_ex" (fallback)
```

#### 2. Price Detection (`core/detection_with_prices.py`)
**Purpose**: Display card prices during live detection

**Features**:
- Real-time price overlays on detected cards
- Excel integration for price database
- Support for Cardmarket (EUR) and TCGPlayer (USD)
- Visual price boxes with color coding
- Confidence threshold filtering

**Usage**:
```python
from core.detection_with_prices import PriceDetector

detector = PriceDetector(
    model_path="yolov8n.pt",
    excel_path="excel/cards_info.xlsx"
)

# Detect on image
detector.detect_image("test.jpg", output_path="result.jpg", conf_threshold=0.5)

# Detect on webcam
detector.detect_video(source=0, conf_threshold=0.5)
```

#### 3. Initialization Scripts

**`scripts/init_prices.py`** - Initialize from data.yaml
```bash
python scripts/init_prices.py
```
- Reads cards from `output/dataset/data.yaml`
- Fetches prices from TCGdex API
- Creates/updates `excel/cards_info.xlsx`

**`scripts/init_prices_simple.py`** - Training subset (8 cards)
```bash
python scripts/init_prices_simple.py
```
- Quick initialization for testing
- Pre-defined 8-card dataset
- Faster execution

**`scripts/init_prices_real.py`** - Real card dataset
```bash
python scripts/init_prices_real.py
```
- Production-ready initialization
- Comprehensive card list
- Full price database

### Excel Schema

**cards_info.xlsx** structure:
| Column | Type | Description |
|--------|------|-------------|
| `Name` | str | Card name (e.g., "Pikachu") |
| `Set #` | str | Card ID (e.g., "sv08_025") |
| `Type` | str | Card type (Pokemon/Trainer/Energy) |
| `Rarity` | str | Rarity (Common/Rare/etc.) |
| `Prix` | float | Minimum price (EUR/USD) |
| `Prix max` | float | Maximum price (EUR/USD) |
| `SourcePrix` | str | Price source ("TCGdex") |

### Configuration

**gui_config.json** - Price detection settings:
```json
{
  "detection": {
    "show_prices": true,
    "excel_path": "excel/cards_info.xlsx",
    "confidence_threshold": 0.5
  }
}
```

---

## ⬇️ Image Download & Management

### TCGdex API Integration

**Features**:
- Free, no authentication required
- 200+ Pokémon sets available
- 10 languages supported
- High/Low quality options
- PNG/JPG/WebP formats
- Parallel downloads (1-16 workers)

**Supported Languages**:
`en`, `fr`, `de`, `it`, `es`, `pt`, `ja`, `ko`, `zh`, `th`

**Usage (GUI)**:
1. Open **Image Download** tab
2. Select set from dropdown (or enter manually)
3. Choose language and quality
4. Set worker count for parallel downloads
5. Click **Download**

**Usage (CLI)**:
```bash
python core/image_downloader.py \
  --set "Surging Sparks" \
  --lang "en" \
  --quality "high" \
  --workers 8
```

**Output**:
- Images saved to `images/`
- Manifest CSV with metadata
- Automatic naming: `{set}_{number}_{lang}.png`

---

## 🎨 Advanced Augmentation

### 22 Transformation Types

1. **Blur** - Gaussian blur (kernel: 3-9)
2. **Contrast** - Adjust contrast (0.5-2.0)
3. **Brightness** - Adjust brightness (0.7-1.3)
4. **Saturation** - Color saturation (0.5-1.5)
5. **Hue Shift** - Change hue (-30 to +30°)
6. **Gamma Correction** - Gamma adjust (0.5-2.0)
7. **Fog Effect** - Add fog overlay (alpha: 0.1-0.4)
8. **Noise** - Gaussian noise (sigma: 10-30)
9. **JPEG Compression** - Compression artifacts (quality: 30-70)
10. **Pixelation** - Pixelate effect (scale: 0.3-0.7)
11. **Posterize** - Reduce colors (levels: 2-5)
12. **Solarize** - Solarization effect (threshold: 100-200)
13. **Sharpen** - Edge enhancement
14. **Emboss** - Emboss filter
15. **Rotation** - Rotate (-15 to +15°)
16. **Perspective** - 3D perspective transform
17. **Scaling** - Scale (0.8-1.2x)
18. **Translation** - Shift position (±20px)
19. **Color Temperature** - Warm/cool tint
20. **Motion Blur** - Directional blur (kernel: 5-15)
21. **Random Erasing** - Random patches (10-30%)
22. **Holographic Effects** - Rainbow gradients, shimmer, light reflections

### Holographic Augmentation

**Features**:
- Intensity control (0.1-1.0)
- Multiple variations per image (1-10)
- Rainbow gradient overlays
- Shimmer patterns
- Light reflection spots
- Rotational effects

**Usage**:
```python
from core.holographic_augmenter_optimized import HolographicAugmenterOptimized

augmenter = HolographicAugmenterOptimized(
    use_gpu=True,  # GPU auto-detected
    num_workers=4  # Multi-threading
)

augmenter.process_directory(
    input_dir="images/",
    output_dir="augmented/"
)
```

### Combination Strategy

- **2-5 simultaneous transforms** per image
- **35,420+ unique combinations** possible
- **Random seed per image** for reproducibility
- **YOLO annotations** preserved during transforms

---

## 🧩 Mosaic Generation

### 3 Layout Modes

1. **Grid Layout** - Organized grid pattern
2. **3D Rotation** - Perspective-rotated cards
3. **Random Layout** - Natural random placement

### 3 Background Modes

1. **Fake Cards Mosaic** - Generated card backgrounds
2. **Local Image** - Use custom image file
3. **Web Image** - Download from URL

### 3 Generation Modes

1. **Quick** - 200 mosaics
2. **Standard** - 500 mosaics
3. **Complete** - 900 mosaics

### Features

- **4-8 cards per mosaic**
- **YOLO polygon annotations** (4-point)
- **Automatic class balancing**
- **Configurable max_groups**
- **Batch generation support**

**Usage (CLI)**:
```bash
python core/mosaic.py \
  --mode complete \
  --layout random \
  --background fake \
  --max_groups 300
```

---

## 🎓 YOLO Training

### Supported Models

- YOLOv8: `n`, `s`, `m`, `l`, `x`
- YOLO11: `n`, `s`, `m`, `l`, `x`

### Training Parameters

- **Epochs**: 10-500
- **Batch Size**: 8-32 (auto-adjusted for GPU)
- **Image Size**: 320-1280 (default: 640)
- **Device**: CPU / CUDA (GPU)

### Features

- Real-time training logs with colors
- Automatic validation splits (80/20)
- Metric export (mAP, precision, recall)
- Results visualization (confusion matrix, curves)
- Model checkpointing (best/last)
- Stop button for interruption

**Usage (GUI)**:
1. Open **Training** tab
2. Select model and parameters
3. Click **Start Training**
4. Monitor progress in logs
5. View results in `runs/train/`

---

## 📹 Live Detection

### 3 Detection Modes

1. **Webcam** - Real-time webcam detection
2. **Video** - Process video files
3. **Image** - Batch image detection

### Features

- Model selection (any .pt file)
- Confidence threshold slider (0.1-0.9)
- Real-time FPS counter
- Bounding box visualization
- Class labels and confidence scores
- **Price display** (if enabled)
- Recording capability

**Keyboard Shortcuts**:
- `Q` - Quit detection
- `S` - Save screenshot
- `P` - Pause/Resume
- `R` - Toggle recording

---

## 🗂️ Dataset Management

### Export Formats

1. **YOLO** (default) - Ultralytics format
2. **COCO** - Microsoft COCO format
3. **VOC** - Pascal VOC XML format
4. **TFRecord** - TensorFlow format
5. **Roboflow** - Roboflow compatible

### Auto-Balancer

**Purpose**: Balance class distribution in dataset

**Features**:
- Automatic undersampling of majority classes
- Configurable target ratio
- Preserves annotation quality
- Generates balanced split

**Usage**:
```python
from core.auto_balancer_optimized import AutoBalancer

balancer = AutoBalancer(
    target_ratio=2.0,
    use_gpu=True  # GPU-accelerated operations
)
balancer.balance_dataset("output/yolov8/")
```

### Validation

**Dataset Validator** checks:
- YOLO format correctness
- Image integrity (corrupted files)
- Annotation consistency
- Class distribution
- Label/image matching

**HTML Report Generation**:
```bash
python tests/verify_detailed.py
```
Output: `validation_report.html`

---

## 🧪 Testing & Validation

### Test Suite

Located in `tests/` directory:

**Unit Tests**:
- `test_annotations.py` - Annotation format validation
- `test_detection_prices.py` - Price detection testing
- `test_full_chain.py` - End-to-end pipeline test
- `test_mapping_debug.py` - Card mapping validation
- `test_autobalancer_performance.py` - Balancer benchmarks
- `test_holographic_performance.py` - Holographic effects benchmark
- `test_mosaic_performance.py` - Mosaic generation benchmark

**Verification Scripts**:
- `verify_data_yaml.py` - data.yaml validation
- `verify_detailed.py` - Comprehensive dataset check
- `check_corrupted_images.py` - Image integrity check

**Visualization Tools**:
- `visualize_annotations.py` - View annotations
- `visualize_bbox.py` - Bounding box inspector

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_full_chain.py

# Verify dataset
python tests/verify_detailed.py

# Check corrupted images
python tests/check_corrupted_images.py
```

---

## ⚡ Workflow Optimization

### Optimized Workflow (`scripts/workflow_optimized.py`)

**Features**:
- Streamlined pipeline execution
- Better error handling and recovery
- Performance improvements
- Parallel processing where possible
- Progress tracking and logging

**Workflow Steps**:
1. **Download** - Fetch cards from TCGdex
2. **Augment** - Generate augmented images
3. **Mosaic** - Create mosaic compositions
4. **Validate** - Check dataset quality
5. **Train** - Train YOLO model
6. **Detect** - Test on new images

**Usage**:
```bash
python scripts/workflow_optimized.py --mode full
```

**Modes**:
- `quick` - Download → Augment → Mosaic
- `full` - Complete pipeline
- `custom` - User-defined steps

---

## 🎨 GUI Features

### Modern Interface (v3.1)

**Tabs**:
1. **Dashboard** - Statistics and quick actions
2. **Download** - TCGdex image download
3. **Augmentation** - Image augmentation settings
4. **Mosaic** - Mosaic generation
5. **Training** - YOLO training
6. **Detection** - Live detection with prices
7. **Utilities** - Tools and settings

**Settings Dialog** (6 tabs):
1. **General** - Basic settings
2. **Paths** - Directory configuration
3. **TCGdex** - API settings
4. **Training** - Training defaults
5. **Detection** - Detection settings
6. **Advanced** - Expert options

---

## 🔧 Configuration Files

### gui_config.json

Complete GUI state persistence:
```json
{
  "last_model": "yolov8n.pt",
  "confidence": 0.5,
  "show_prices": true,
  "excel_path": "excel/cards_info.xlsx",
  "theme": "dark"
}
```

### api_config.json

TCGdex API configuration:
```json
{
  "tcgdex": {
    "language": "en",
    "quality": "high",
    "workers": 8
  }
}
```

---

## 📊 Performance

### Benchmarks

**Augmentation**:
- ~0.5s per image (22 transforms)
- ~100 images/minute

**Mosaic Generation**:
- ~2s per mosaic (8 cards)
- ~30 mosaics/minute

**YOLO Training** (YOLOv8n, GTX 3060):
- ~10 epochs in 5 minutes (500 images)
- ~0.3s per batch (batch_size=16)

**Detection**:
- ~30 FPS on webcam (1080p)
- ~50 FPS on GPU

---

## 🚀 Quick Start Guide

### Minimal Setup (5 minutes)

1. **Install**:
```bash
install_env.bat
```

2. **Download Cards**:
```bash
python core/image_downloader.py --set "Surging Sparks" --lang "en"
```

3. **Initialize Prices**:
```bash
python scripts/init_prices_simple.py
```

4. **Launch GUI**:
```bash
run_gui_v3.1.bat
```

### Full Pipeline (30 minutes)

1. Download cards (10 min)
2. Generate augmentations (5 min)
3. Create mosaics (10 min)
4. Train YOLO model (5 min)
5. Test detection with prices (instant)

---

## 📚 Additional Resources

- [📖 HELP.md](../HELP.md) - Complete user manual
- [📜 CHANGELOG.md](../CHANGELOG.md) - Version history
- [🌐 TCGdex Integration](INTEGRATION_TCGDEX.md) - API details
- [🎨 GUI Guide](GUI_V3_GUIDE.md) - Interface walkthrough

---

## 💡 Tips & Tricks

### Performance Optimization

1. **Use GPU** for training (10x faster)
2. **Parallel downloads** (8-16 workers)
3. **Batch processing** for augmentation
4. **SSD storage** for faster I/O

### Quality Improvement

1. **Higher epochs** (100+) for better accuracy
2. **More augmentations** (50-100 per image)
3. **Balanced dataset** (use auto-balancer)
4. **Larger image size** (640-1280) for small objects

### Troubleshooting

**Common Issues**:
- **CUDA Out of Memory**: Reduce batch size
- **Slow Training**: Check GPU usage
- **Low mAP**: More data, more epochs
- **Missing Prices**: Run `init_prices.py`

---

## 🤝 Contributing

See main README for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details.

---

**Last Updated**: November 10, 2025  
**Version**: 3.1.0
