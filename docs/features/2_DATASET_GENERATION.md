# ⚙️ Dataset Generation

This document covers all features related to the creation and enrichment of your Pokémon card dataset.

---

## 📥 Image Downloader

The first step is to gather source images. The integrated downloader uses the public [TCGdex API](https://www.tcgdex.net/docs) to fetch high-quality card images.

| Feature | Description |
| :--- | :--- |
| **Source** | Free TCGdex API (no authentication required). |
| **Coverage** | Over 200 Pokémon TCG sets available. |
| **Languages** | 10 languages supported, including English, French, Japanese, and more. |
| **Quality & Format** | Choose between HD/Low quality and PNG/JPG/WebP formats. |
| **Parallel Downloads** | Use 1 to 16 parallel workers to speed up the download process significantly. |
| **Manifest File** | A `manifest.csv` is automatically generated with metadata for all downloaded cards. |

---

## 🎨 Advanced Augmentation

Augmentation is crucial for creating a robust model. Our tool uses `imgaug` to apply a wide variety of transformations.

- **22+ Transformation Types**: A random combination of 2-5 transforms is applied to each image, creating unique variations.
  - **Visual**: Blur, Contrast, Saturation, Fog, Posterize, Sharpen, Emboss.
  - **Noise**: Gaussian, Salt & Pepper, JPEG compression.
  - **Geometry**: Rotation, Scale, Translation, Perspective.
  - **Color**: HSV shift, Channel shuffle, Color temperature.
  - **Advanced**: Random erasing, Elastic deformation, Grid distortion.
- **Automatic Annotations**: YOLO `.txt` label files are automatically generated for every augmented image.
- **Alpha Channel Preservation**: Transparency in PNG images is correctly handled.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/example_augmented.png" alt="Augmented Card" width="50%"/>
</p>

---

## 🌈 Holographic Effects

To help the model recognize shiny cards, you can add realistic holographic effects.

- **5+ Shiny Styles**:
  1.  **Rainbow**: A multi-color gradient overlay.
  2.  **Linear**: A horizontal or vertical shimmer effect.
  3.  **Radial**: A circular light burst originating from the center.
  4.  **Metallic**: A chrome-like reflection effect.
  5.  **Glitter**: A pattern of small, bright sparkles.
- **Configurable Intensity**: Control the strength of the effect from subtle (0.1) to strong (1.0).
- **Multiple Variations**: Generate several different holographic versions for each card.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/example_holographic.png" alt="Holographic Card" width="50%"/>
</p>

---

## 🧩 Mosaic Generator

Mosaics combine multiple cards into a single image, forcing the model to learn to detect objects in various contexts and scales.

- **Ultra-Fast Generation**: Uses `ProcessPoolExecutor` for true parallel processing, making it **30-60x faster** than sequential methods.
- **3 Generation Modes**:
  - **Quick (200)**: For fast testing.
  - **Standard (500)**: Recommended for a balanced dataset.
  - **Complete (All)**: Generates all possible mosaics from the available images.
- **Layouts & Backgrounds**: Choose from multiple layouts (Grid, 3D Rotation) and backgrounds (Fake Cards, Local Images) to increase diversity.
- **Polygon Annotations**: Generates 4-point polygon annotations, fully compatible with YOLOv8.
- **Error Handling**: Corrupted source images are automatically detected and moved to a `corrupted/` folder without crashing the process.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/example_layout_annotated.png" alt="Annotated Mosaic" width="90%"/>
</p>

---

## ⚖️ Auto-Balancer

A balanced dataset is key to a good model. The auto-balancer ensures that no single card (class) dominates the dataset.

- **3 Balancing Strategies**:
  1.  **Augment**: Increases the number of images for minority classes.
  2.  **Reduce**: Decreases the number of images for majority classes.
  3.  **Both**: Equalizes all classes to a specified target count.
- **Configurable Target**: You can set the desired number of instances per class.
- **Safe Operation**: Automatically backs up the dataset before making any changes.

---

## 📚 Navigation

⬅️ [Previous: GUI Overview](1_GUI_OVERVIEW.md) | [Back to Features Overview](../FEATURES.md) | ➡️ [Next: Training & Detection](3_TRAINING_AND_DETECTION.md)

---

**Last Updated**: November 14, 2025
