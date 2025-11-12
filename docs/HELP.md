# 📖 Pokemon Dataset Generator - Help & User Manual

**Version 3.0** | *Complete Guide for GUI v3.0*

---

## 📋 Table of Contents

1. [🚀 Getting Started](#-getting-started)
2. [🏠 Dashboard (Home)](#-dashboard-home)
3. [🔄 Automatic Workflow](#-automatic-workflow)
4. [🎨 Augmentation](#-augmentation)
5. [🧩 Mosaic Generator](#-mosaic-generator)
6. [✅ Dataset Validation](#-dataset-validation)
7. [🎓 YOLOv8 Training](#-yolov8-training)
8. [📹 Live Detection](#-live-detection)
9. [📦 Export Tools](#-export-tools)
10. [🛠️ Utilities](#-utilities)
11. [⚙️ Settings](#-settings)
12. [❓ FAQ & Troubleshooting](#-faq--troubleshooting)

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12** or higher
- **Windows** OS (tested on Windows 10/11)
- **Webcam** (optional, for live detection)
- **4GB+ RAM** recommended
- **CUDA GPU** (optional, for faster training)

### Installation

1. **Extract or Clone** the project:
   ```bash
   git clone https://github.com/lo26lo/pok.git
   cd pok
   ```

2. **Run the installer**:
   ```batch
   install_env.bat
   ```
   This will create a `.venv` virtual environment and install all dependencies.

3. **Launch the GUI**:
   ```batch
   run_gui_v3.bat
   ```

### First Launch

On first launch, the GUI will check:
- ✅ Virtual environment exists (`.venv/`)
- ✅ Excel file exists (for TCGdex API)

If checks fail:
- 🔴 **Red warning banner** appears
- Click "Fix Now" to run `install_env.bat`

---

## 🏠 Dashboard (Home)

The **Dashboard** is your command center with real-time statistics.

### Statistics Display

| Metric | Description |
|--------|-------------|
| **Source Images** | Number of original cards in `images/` |
| **Augmented Images** | Number of augmented images in `output/augmented/` |
| **Mosaic Images** | Number of generated mosaics in `output/yolov8/` |
| **Dataset Size** | Total disk usage of all datasets |

### Quick Actions

- **🔄 Run Workflow**: Launch the 5-step automatic pipeline
- **🎨 Augment**: Jump to Augmentation view
- **🧩 Generate Mosaics**: Jump to Mosaic view
- **✅ Validate**: Jump to Validation view

### Environment Status

- **Virtual Environment**: Shows if `.venv` is detected
- **Excel File**: Shows if `generated_extension.xlsx` exists
- **Fix Now**: Quick button to run installer

---

## 🔄 Automatic Workflow

The **Automatic Workflow** runs 5 steps sequentially:

### Steps

1. **🎨 Augmentation**: Generate image variations
2. **🧩 Mosaic Generation**: Create YOLO training layouts
3. **✅ Validation**: Verify dataset integrity
4. **⚖️ Auto-Balance**: Equalize class distribution
5. **🎓 Training**: Train YOLOv8 model

### Configuration

Toggle each step on/off with checkboxes:
- ✅ **Enable Augmentation**: Generate 5 variations per image (default)
- ✅ **Enable Mosaic**: Generate 65 mosaics (default)
- ✅ **Enable Validation**: Verify YOLO format (default)
- ✅ **Enable Balancing**: Balance classes to 50 images each (default)
- ✅ **Enable Training**: Train YOLOv8n for 50 epochs (default)

### Running the Workflow

1. Configure steps (check/uncheck)
2. Click **"Start Workflow"**
3. Monitor progress in real-time logs
4. Click **"Stop"** to cancel anytime

**Progress:**
- Blue animated progress bar
- Step-by-step status updates
- Elapsed time counter
- Success/Error messages

### When to Use

- ✅ **Initial setup**: First-time dataset creation
- ✅ **Full pipeline**: Complete training workflow
- ✅ **Automation**: Batch processing multiple cards

---

## 🎨 Augmentation

Generate **variations** of your original card images using **25+ transformation types**.

### Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Augmentation Count** | Variations per image | 5 |
| **Output Directory** | Where to save results | `output/augmented/` |

### Transformation Pipeline (SomeOf: 2-5 applied randomly)

**🌞 Luminosité & Contraste** (simule conditions d'éclairage):
- `Add (-20, +20)`: Ajuste luminosité globale (-20 à +20 pixels)
- `Multiply (0.8, 1.2)`: Multiplie contraste (80% à 120%)
- `LinearContrast (0.6, 1.6)`: Contraste linéaire (60% à 160%)
- `GammaContrast (0.7, 1.5)`: Correction gamma (0.7 à 1.5)

**🎨 Couleurs** (simule températures/ambiances):
- `AddToHueAndSaturation (-30°, +30°)`: Décalage teinte/saturation
- `ChangeColorTemperature (3000K, 10000K)`: Température couleur (chaud à froid)
- `MultiplyHueAndSaturation (0.8, 1.2)`: Multiplie saturation (80% à 120%)

**🌫️ Flou & Netteté** (simule bougé/mise au point):
- `GaussianBlur (0, 2.0)`: Flou gaussien (0 à 2.0 sigma)
- `AverageBlur (1x1, 5x5)`: Flou moyen (kernel 1x1 à 5x5)
- `Sharpen (alpha 0-0.5, lightness 0.8-1.3)`: Augmente netteté

**🔊 Bruit** (simule capteur bas de gamme):
- `AdditiveGaussianNoise (0-5%)`: Bruit gaussien (0 à 5% de 255)
- `ImpulseNoise (2%)`: Bruit impulsionnel (2% de pixels)
- `SaltAndPepper (1%)`: Bruit sel et poivre (1% de pixels)

**✨ Effets Visuels** (simule environnement):
- `Fog (severity 1-2)`: Brouillard léger (sévérité 1-2)
- `Posterize (5-8 bits)`: Réduction couleurs (5-8 bits par canal)
- `Emboss (alpha 0-30%)`: Effet relief (alpha 0-30%, force 0.5-1.5)
- `EdgeDetect (alpha 0-30%)`: Détection contours (alpha 0-30%)

**📸 Compression & Déformation**:
- `JpegCompression (50-99%)`: Compression JPEG (qualité 50% à 99%)
- `ElasticTransformation (alpha 0-5)`: Déformation élastique (alpha 0-5, sigma 0.5)

⚠️ **Note importante**: La rotation est appliquée **UNIQUEMENT** lors de la génération de mosaïques, **PAS** pendant l'augmentation. Cela évite une double rotation qui casserait l'alignement des bounding boxes.

### How It Works

1. **Input**: Reads all PNG images from `images/`
2. **Transform**: Applies 2-5 simultaneous random effects (from 25+ available)
3. **Annotation**: Generates matching YOLO `.txt` files
4. **Output**: Saves to `output/augmented/images/` and `labels/`

### Running Augmentation

1. Place PNG cards in `images/` folder
2. Set augmentation count (e.g., 5)
3. Click **"Start Augmentation"**
4. Monitor progress bar and logs
5. Click **"Stop"** to cancel

**Output Structure:**
```
output/augmented/
├── images/
│   ├── card001_aug_000.png
│   ├── card001_aug_001.png
│   └── ...
└── labels/
    ├── card001_aug_000.txt
    ├── card001_aug_001.txt
    └── ...
```

### YOLO Annotation Format

Each `.txt` file contains one line per object:
```
<class_id> <x_center> <y_center> <width> <height>
```

Example:
```
0 0.5 0.5 0.8 0.9
```

- Values normalized to [0, 1]
- x_center, y_center: object center
- width, height: bounding box size

---

## 🧩 Mosaic Generator

Create **composite images** with multiple cards for YOLO training.

### Configuration

| Setting | Options | Description |
|---------|---------|-------------|
| **Layout Mode** | Grid, Rotation, Random | How cards are arranged |
| **Background Mode** | Mosaic, Local, Web | Source of background images |
| **Output Directory** | Path | Where to save mosaics |

### Layout Modes

**1. Grid Mode** (default)
- Cards arranged in regular grid
- 2x2, 3x2, 3x3 layouts
- Uniform spacing

**2. Rotation Mode**
- Cards randomly rotated (±45°)
- Overlapping allowed
- Natural placement

**3. Random Mode**
- Cards placed randomly
- Variable scales (0.3-0.8x)
- Maximum variety

### Background Modes

**1. Mosaic Backgrounds** (default)
- Pre-generated textures
- Stored in `fakeimg/`
- Fast and reliable

**2. Local Directory**
- Use your own backgrounds
- Specify custom path
- JPEG/PNG supported

**3. Web Download**
- Download from Unsplash API
- Keyword: "texture"
- 100 images cached

### Running Mosaic Generation

1. Select layout mode
2. Select background mode
3. Set output directory
4. Click **"Generate Mosaics"**
5. Monitor progress bar and logs

**Default Output:** 65 mosaics with annotations

**Output Structure:**
```
output/yolov8/
├── images/
│   ├── mosaic_001.jpg
│   ├── mosaic_002.jpg
│   └── ...
└── labels/
    ├── mosaic_001.txt
    ├── mosaic_002.txt
    └── ...
```

### Annotation Format

Each mosaic `.txt` file contains:
- One line per card in the mosaic
- 4-point polygon format (8 values)
- Class ID from original card filename

Example:
```
0 0.1 0.2 0.4 0.2 0.4 0.6 0.1 0.6
1 0.6 0.3 0.9 0.3 0.9 0.7 0.6 0.7
```

---

## ✅ Dataset Validation

Verify **integrity** of your YOLO dataset before training.

### What It Checks

1. **YOLO Format**: Correct annotation structure
2. **Image Integrity**: No corrupted files
3. **Label Matching**: Every image has a label
4. **Class Distribution**: Count per class
5. **Bounding Box Validity**: Coordinates in [0, 1]

### Running Validation

1. Click **"Validate Dataset"** button
2. Monitor progress in logs
3. View HTML report when complete

### Validation Report

**HTML Report Includes:**
- ✅ Total images/labels count
- ✅ Valid vs. corrupted files
- ✅ Class distribution chart
- ✅ Error list with line numbers
- ✅ Recommendations

**Report Location:** `validation_report.html` (auto-opens in browser)

### Common Issues

| Issue | Solution |
|-------|----------|
| Missing labels | Check label path matches image path |
| Invalid coordinates | Ensure values are in [0, 1] range |
| Corrupted images | Re-augment or remove file |
| Empty labels | Check annotation generation |

---

## 🎓 YOLOv8 Training

Train **YOLOv8 models** directly from the GUI with real-time logs.

### Configuration

| Setting | Options | Description |
|---------|---------|-------------|
| **Model Size** | n, s, m, l, x | Model complexity |
| **Epochs** | 1-1000 | Training iterations |
| **Image Size** | 640, 1280 | Input resolution |
| **Batch Size** | Auto | Batch size (auto-detect GPU) |

### Model Sizes

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| **YOLOv8n** | ⚡⚡⚡ | ⭐⭐ | Fast detection, mobile |
| **YOLOv8s** | ⚡⚡ | ⭐⭐⭐ | Balanced, default |
| **YOLOv8m** | ⚡ | ⭐⭐⭐⭐ | High accuracy |
| **YOLOv8l** | 🐌 | ⭐⭐⭐⭐⭐ | Maximum accuracy |
| **YOLOv8x** | 🐢 | ⭐⭐⭐⭐⭐ | Research, benchmarking |

### Running Training

1. Select model size (e.g., `n`)
2. Set epochs (e.g., 50)
3. Set image size (e.g., 640)
4. Click **"Start Training"**
5. Monitor real-time logs
6. Click **"Stop"** to cancel

**Training Output:**
```
output/yolov8/runs/detect/train/
├── weights/
│   ├── best.pt          # Best model
│   └── last.pt          # Last epoch
├── results.png          # Metrics chart
├── confusion_matrix.png # Confusion matrix
└── val_batch0_pred.jpg  # Validation predictions
```

### Training Logs

Real-time logs show:
- Epoch progress (1/50, 2/50, ...)
- Loss values (box, cls, dfl)
- mAP@50, mAP@50-95
- GPU memory usage
- Training speed (imgs/sec)

### After Training

- **Best model**: Saved to `weights/best.pt`
- **Metrics**: View in `results.png`
- **Validation**: Check `val_batch0_pred.jpg`
- **Use model**: In Live Detection view

---

## 📹 Live Detection

Run **real-time detection** from your webcam using trained models.

### Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| **Model Path** | Path to `.pt` model file | `weights/best.pt` |
| **Confidence Threshold** | Detection threshold | 0.5 |
| **Webcam ID** | Camera index | 0 |

### Running Detection

1. Browse and select model (`.pt` file)
2. Set confidence threshold (0.0 - 1.0)
3. Set webcam ID (0 for default camera)
4. Click **"Start Detection"**
5. View real-time video with bounding boxes
6. Press **"Q"** in video window to stop

### Detection Window

- **Bounding boxes**: Green rectangles around detected cards
- **Class label**: Card name (top-left of box)
- **Confidence**: Detection score (e.g., 0.95)
- **FPS**: Frames per second (top-left corner)

### Tips

- 📷 **Good lighting**: Improves detection accuracy
- 🎯 **Hold cards still**: Reduces false positives
- 🖼️ **Clear background**: Minimizes noise
- 📏 **Proper distance**: 20-50cm from camera

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No video | Check webcam connection, try ID 1 |
| Low FPS | Use smaller model (YOLOv8n) |
| No detections | Lower confidence threshold |
| Wrong detections | Train longer, improve dataset |

---

## 📦 Export Tools

Export your **YOLO dataset** to multiple formats for different frameworks.

### Supported Formats

| Format | Framework | Extension | Description |
|--------|-----------|-----------|-------------|
| **COCO** | PyTorch, TensorFlow | `.json` | MS COCO JSON format |
| **Pascal VOC** | Caffe, MATLAB | `.xml` | XML annotations per image |
| **TFRecord** | TensorFlow | `.tfrecord` | Binary TensorFlow format |
| **Roboflow** | Roboflow | `.zip` | ZIP with YOLO + metadata |

### COCO Export

**Use case:** PyTorch, Detectron2, MMDetection

**Output:**
```json
{
  "images": [{"id": 1, "file_name": "image1.jpg", ...}],
  "annotations": [{"id": 1, "image_id": 1, "category_id": 0, "bbox": [x, y, w, h], ...}],
  "categories": [{"id": 0, "name": "class_0", ...}]
}
```

**Usage:**
1. Click **"Export to COCO"**
2. Select output file (e.g., `coco_annotations.json`)
3. Monitor progress
4. Import in PyTorch with `pycocotools`

### Pascal VOC Export

**Use case:** Caffe, MATLAB, TensorFlow Object Detection API

**Output:**
```xml
<annotation>
  <filename>image1.jpg</filename>
  <object>
    <name>class_0</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>150</ymin>
      <xmax>300</xmax>
      <ymax>400</ymax>
    </bndbox>
  </object>
</annotation>
```

**Usage:**
1. Click **"Export to VOC"**
2. Select output directory
3. Monitor progress
4. Use with TensorFlow Object Detection API

### TFRecord Export

**Use case:** TensorFlow, TensorFlow Lite

**Output:** Binary `.tfrecord` file with embedded images + annotations

**Usage:**
1. Click **"Export to TFRecord"**
2. Select output file (e.g., `dataset.tfrecord`)
3. Monitor progress
4. Load in TensorFlow with `tf.data.TFRecordDataset`

### Roboflow Export

**Use case:** Roboflow platform, sharing datasets

**Output:** ZIP archive with:
- YOLO images + labels
- `data.yaml` config
- `README.md` metadata
- Roboflow-compatible structure

**Usage:**
1. Click **"Export to Roboflow"**
2. Select output ZIP file
3. Monitor progress
4. Upload to Roboflow or share with team

---

## 🛠️ Utilities

Additional tools accessible from the **Utilities** view.

### 📋 Excel & Prices (TCGdex API)

**Manage TCG card data** with Excel integration.

#### Features

1. **Generate Extension Excel**
   - Select TCG extension (e.g., "Surging Sparks")
   - Generate Excel with all cards
   - Columns: Name, ID, Type, Rarity, HP, Stage, etc.

2. **Update Card Prices**
   - Load existing Excel
   - Fetch prices from Cardmarket + TCGPlayer
   - Add price columns to Excel

3. **Search Card with Prices**
   - Enter card name
   - Optionally specify extension
   - Get average + max prices

#### Usage

1. Open **Utilities** → **Excel & Prices**
2. Select operation (Generate / Update / Search)
3. Fill required fields
4. Click **"Execute"**
5. Monitor progress in logs

**Configuration:** Edit `api_config.json` to change language/API source.

### ⚖️ Auto-Balancing

**Balance class distribution** in your YOLO dataset.

#### Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Augment** | Increase minority classes | Small dataset |
| **Reduce** | Decrease majority classes | Large dataset |
| **Both** | Equalize all classes | Balanced training |

#### Settings

- **Target Count**: Images per class (e.g., 50)
- **Strategy**: Augment / Reduce / Both
- **Input Directory**: Path to YOLO dataset

#### Usage

1. Open **Utilities** → **Auto-Balancing**
2. Set target count (e.g., 50)
3. Select strategy (e.g., "augment")
4. Click **"Balance Dataset"**
5. Monitor progress

**Output:** Balanced dataset in same directory (backup created).

### 🌈 Holographic Augmentation

**Simulate holographic/shiny effects** on cards.

#### Effects

- Rainbow gradient overlays
- Light glare reflections
- Metallic texture
- Shimmer patterns
- Color shift

#### Settings

- **Input Directory**: Source cards (e.g., `images/`)
- **Output Directory**: Holographic output (e.g., `images_holographic/`)
- **Variations**: Effects per card (e.g., 5)

#### Usage

1. Open **Utilities** → **Holographic**
2. Set input/output directories
3. Set variation count
4. Click **"Generate Holographic"**
5. Monitor progress

**Use case:** Simulate rare card variants for training.

### 🌐 TCG Browser

**Browse and search TCG cards** with web interface.

#### Features

- Search by card name
- Filter by extension
- View card images
- See card details (HP, type, rarity)
- Export to Excel

#### Usage

1. Open **Utilities** → **TCG Browser**
2. Enter search query (e.g., "Pikachu")
3. Click **"Search"**
4. Browse results in table
5. Click card to view details

**API:** Uses TCGdex API (free, no auth required).

### 🧹 Clean & Reset

**Clean generated files and folders** with safety confirmations.

#### Available Clean Actions

| Action | Target | Description |
|--------|--------|-------------|
| **🗑️ Clean Output** | `output/` | Deletes entire output folder |
| **🎨 Clean Augmented** | `output/augmented/` | Deletes augmented images + labels |
| **🧩 Clean Mosaics** | `output/yolov8/` | Deletes YOLO mosaics |
| **🎓 Clean Training** | `runs/` | Deletes trained models + metrics |
| **🌈 Clean Holographic** | `images_holographic/` | Deletes holographic augmented images |
| **📋 Clean Fakeimg** | `fakeimg/` + `fakeimg_augmented/` | Deletes fake backgrounds |
| **🚨 Clean All** | All above | Deletes all generated folders |

#### Clean All Options

**Protected by default:**
- ⚠️ `images/` folder is NOT deleted by default
- Must explicitly check "Include images/ folder" option
- Double confirmation required before deleting

**What gets deleted (Clean All):**
1. `output/` - All augmented images and mosaics
2. `runs/` - All training results and models
3. `images_holographic/` - Holographic effects
4. `fakeimg/` + `fakeimg_augmented/` - Fake backgrounds
5. `images/` - Source images (only if checkbox enabled)

#### Usage

**Individual Clean:**
1. Open **Utilities** → **Clean & Reset** section
2. Click desired clean button (e.g., "Clean Output")
3. Confirm in dialog
4. Check logs for result

**Clean All:**
1. Open **Utilities** → **Clean & Reset** section
2. (Optional) Check "Include images/ folder"
3. Click **"CLEAN ALL"** button
4. Confirm in first dialog
5. Confirm again in second dialog (double security)
6. Monitor logs

#### Safety Features

- ✅ **Confirmation dialogs** for all actions
- ✅ **Double confirmation** for Clean All
- ✅ **Protected images/** folder by default
- ✅ **Detailed logs** showing what was deleted
- ✅ **Error handling** if deletion fails

#### When to Use

- 🔄 **Reset project**: Start fresh with new cards
- 💾 **Free disk space**: Remove large generated folders
- 🧪 **Test workflow**: Clean between test runs
- 🐛 **Fix corruption**: Remove corrupted generated files
- 📦 **Before backup**: Reduce backup size

#### Warning

⚠️ **PERMANENT DELETION**: Files cannot be recovered after cleaning!

⚠️ **Backup important data** before using Clean All!

⚠️ **Training results**: Models in `runs/` will be lost!

---

## ⚙️ Settings

Configure the GUI via **⚙️ Settings** button.

### General Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Images Directory** | Source card images | `images/` |
| **Output Directory** | Augmented output | `output/augmented/` |
| **Mosaic Directory** | Mosaic output | `output/yolov8/` |
| **Auto-Save Interval** | Config save frequency (sec) | 300 |

### Augmentation Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Augmentation Count** | Variations per image | 5 |
| **Transform Intensity** | Effect strength (0-1) | 0.5 |
| **Random Seed** | Reproducibility seed | Random |

### Training Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Default Epochs** | Training iterations | 50 |
| **Default Image Size** | Input resolution | 640 |
| **Default Model** | YOLOv8 variant | `n` |
| **Batch Size** | Images per batch | Auto |

### Advanced Settings

| Setting | Description | Default |
|---------|-------------|---------|
| **Confidence Threshold** | Detection threshold | 0.5 |
| **Max Workers** | Parallel threads | 4 |
| **Cache Images** | Cache for faster training | False |

### Saving Settings

- **Auto-save**: Every 5 minutes
- **Manual save**: Click "Save" button
- **File**: `gui_config.json`
- **Persistent**: Loaded on next launch

---

## ❓ FAQ & Troubleshooting

### General Issues

**Q: GUI doesn't start**

A: Run `install_env.bat` to create `.venv` environment. Then launch with `run_gui_v3.bat`.

**Q: NumPy errors**

A: Use NumPy < 2.0. The installer automatically handles this. If issues persist, run:
```batch
.venv\Scripts\pip install "numpy<2.0"
```

**Q: Unicode errors on Windows**

A: Fixed in v3.0 with `safe_print()` function. If you see encoding errors, they will auto-fallback to ASCII.

**Q: No logs during operations**

A: Fixed in v3.0 with `-u` (unbuffered) flag. Logs should appear in real-time now.

**Q: Environment check fails**

A: Click "Fix Now" button or run `install_env.bat` manually.

---

### Augmentation Issues

**Q: No augmented images generated**

A: Check:
- Source images exist in `images/` folder
- Images are valid PNG files
- Output directory is writable
- Logs for error messages

**Q: Augmentation too slow**

A: Reduce augmentation count or use fewer source images. Use `--workers 4` for parallel processing.

**Q: YOLO labels missing**

A: Ensure source images have valid dimensions. Check logs for annotation errors.

---

### Mosaic Issues

**Q: No mosaics generated**

A: Check:
- Augmented images exist in `output/augmented/`
- Background images exist (if using local mode)
- Output directory is writable

**Q: Background download fails**

A: Switch to "Mosaic Backgrounds" mode. Web mode requires internet connection.

**Q: Cards not visible in mosaic**

A: Adjust layout mode or background mode. Try "Grid" mode for predictable placement.

---

### Training Issues

**Q: Training crashes**

A: Reduce batch size or image size. Check:
- Valid YOLO dataset in `output/yolov8/`
- `data.yaml` file exists
- GPU memory (if using CUDA)

**Q: Training too slow**

A: Use smaller model (YOLOv8n), reduce image size (640), or enable GPU acceleration.

**Q: Low mAP score**

A: Train longer (more epochs), balance dataset, add more training data, or use larger model.

**Q: GPU not detected**

A: Install CUDA-enabled PyTorch:
```batch
.venv\Scripts\pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

---

### Detection Issues

**Q: No detections**

A: Lower confidence threshold (e.g., 0.3). Ensure model is trained on similar cards.

**Q: Webcam not working**

A: Try webcam ID 1 or 2. Check camera permissions in Windows Settings.

**Q: Low FPS**

A: Use YOLOv8n model, reduce image size, or disable unnecessary background processes.

**Q: Wrong detections**

A: Train model longer, improve dataset quality, or use larger model (YOLOv8m+).

---

### Export Issues

**Q: Export fails**

A: Check:
- Valid YOLO dataset exists
- Output path is writable
- Disk space available

**Q: COCO export empty**

A: Ensure `data.yaml` has correct class names. Check annotation format.

**Q: TFRecord too large**

A: Images are embedded. Use VOC or COCO format for external images.

---

### API Issues

**Q: TCGdex API not working**

A: Check internet connection. TCGdex is free and requires no authentication.

**Q: Price search fails**

A: Cardmarket/TCGPlayer prices may be unavailable for some cards. Check spelling.

**Q: Excel generation empty**

A: Ensure extension name is correct (e.g., "Surging Sparks"). Check API logs.

---

### Clean & Reset Issues

**Q: Clean All doesn't delete images/**

A: By design! Check "Include images/ folder" option to delete source images. This protects your original cards.

**Q: Can I recover deleted files?**

A: No. Clean operations are permanent. Always backup important data before cleaning.

**Q: Clean fails with permission error**

A: Check:
- Files are not open in another program
- You have write permissions
- Folders are not in use by Python/training processes

**Q: Should I clean before training?**

A: Only if you want to regenerate the dataset. Clean removes all previous work including trained models.

**Q: What's the difference between Clean Output and Clean All?**

A:
- **Clean Output**: Deletes only `output/` folder (augmented + mosaics)
- **Clean All**: Deletes everything (output, runs, holographic, fakeimg, optionally images)

**Q: How to free up space without losing models?**

A: Use individual clean actions:
- Clean Augmented (keep mosaics)
- Clean Mosaics (if already trained)
- Clean Holographic (if not needed)
- Keep `runs/` for trained models

**Q: Clean deleted my training results!**

A: Clean Training or Clean All removes `runs/` folder. Backup `runs/train/*/weights/best.pt` before cleaning.

---

### Performance Tips

**Speed Up Training:**
- Use GPU (install CUDA PyTorch)
- Reduce image size (640 → 320)
- Use smaller model (YOLOv8n)
- Enable image caching

**Speed Up Augmentation:**
- Use parallel processing (`--workers 4`)
- Reduce augmentation count
- Use SSD for faster I/O

**Reduce Memory Usage:**
- Close unused applications
- Use smaller batch size
- Reduce image size
- Use YOLOv8n model

---

## 📞 Getting More Help

- **📖 Full Documentation**: `docs/GUI_V3_GUIDE.md`
- **🐛 Report Bugs**: [GitHub Issues](https://github.com/lo26lo/pok/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/lo26lo/pok/discussions)
- **📧 Email Support**: contact@example.com

---

<div align="center">

**Made with ❤️ for Pokemon TCG collectors and AI enthusiasts**

[🏠 Back to Top](#-pokemon-dataset-generator---help--user-manual)

</div>
