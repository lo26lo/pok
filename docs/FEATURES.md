# 🚀 Pokémon Dataset Generator - Features Overview

This document provides a high-level overview of the main features of the Pokémon Dataset Generator. For more detailed information, please follow the links to the specific documentation pages.

---

## 📋 Table of Contents

1.  [**GUI Overview**](#1--gui-overview)
2.  [**Dataset Generation**](#2--dataset-generation)
3.  [**Training and Detection**](#3--training-and-detection)
4.  [**Price System**](#4--price-system)

---

## 1. 🎨 GUI Overview

The application is built around a modern, intuitive graphical user interface designed for an efficient workflow. It features a collapsible sidebar, a main content area for the active task, and a real-time log panel. The central dashboard provides at-a-glance statistics and quick access to all major functions.

> **➡️ [Learn more in the detailed GUI Overview](./features/1_GUI_OVERVIEW.md)**

---

## 2. ⚙️ Dataset Generation

Create rich and diverse datasets with a suite of powerful tools. The process is designed to be flexible and highly configurable.

-   **Image Downloader**: Fetch high-quality card images from the TCGdex API with parallel downloads.
-   **Advanced Augmentation**: Apply over 22 types of transformations to create unique image variations.
-   **Live Augmentation Preview**: Tune intensity, transform count and categories with instant visual feedback on a sample card — no generation run needed.
-   **Holographic Effects**: Add 5+ styles of realistic shiny effects to help the model generalize.
-   **Mosaic Generator**: Combine multiple cards into complex scenes with automatic polygon annotations, generated up to 60x faster with parallel processing.
-   **Realistic Backgrounds**: Procedural background generator (wood table, playmat, binder pages, fabric, desk) with soft drop shadows under cards and photo-like camera effects (color temperature, vignette) — background mode 3, fully offline and license-free.
-   **Realistic Occlusions**: Fan/hand layout mode with overlapping cards, plastic sleeve effects, procedural fingers and inter-card shadows; cards hidden below 25% visibility are never annotated (layout mode 4).
-   **Auto-Balancer**: Automatically balance the class distribution in your dataset to prevent model bias.

> **➡️ [Learn more in the detailed Dataset Generation guide](./features/2_DATASET_GENERATION.md)**

---

## 3. 🎓 Training and Detection

Train a powerful YOLOv8 model on your custom dataset and use it for live detection, all within the same application.

-   **Real-World Validation Set**: Dedicated `real_mAP` metric on hand-annotated photos of real cards (never used in training, MD5 leakage guard), evaluated automatically after each training run.
-   **Evaluation Tab**: Browse training runs, view Ultralytics curves and confusion matrices, compare two runs side by side, and inspect the worst predictions (missed cards, false positives, wrong classes) on real or synthetic validation images.
-   **Fine-Grained Card Identification**: A second pipeline stage identifies *which exact card* was detected (set + number), even for sets YOLO was never trained on. Each detected crop is embedded (MobileNetV2 features via OpenCV DNN — no extra Python dependency; pure-OpenCV descriptor as fallback) and matched against a cosine k-NN index (FAISS if installed, numpy otherwise) built from the downloaded TCGdex images with `python tools/build_card_index.py`. Enable "🎴 Identify Cards" in the Detection view to see the exact name, set and number in the overlay; prices are then looked up directly by card ID. Measured 98.4% top-1 / 100% top-5 at ~7 ms per card on CPU (245 real cards, degraded webcam-like queries — see `tools/benchmark_card_embeddings.py`).
-   **Card Grading (condition estimate)**: Enable "🔍 Grade Cards" to estimate each detected card's condition from the webcam crop — border centering measured from gradient profiles (±3% accuracy) and whitened-corner detection (card rounding masked, any border color, neutral on white borders). The overlay shows an NM/EX/GD/PL badge and weights the displayed price accordingly (1.0/0.85/0.70/0.50). Heuristic and best effort: it never blocks detection; surface scratches are out of scope at webcam resolution.
-   **Collection Scan Mode**: A continuous webcam session that deduplicates the cards it sees and builds an inventory with the total collection value. A card is added once it has been identified on 3 frames — showing the same card for 10 seconds still yields a single entry, while two copies side by side count as quantity 2. Live counter on the overlay (unique cards, copies, running value), per-card prices from the local database, and a session recap with CSV + Excel export (totals row included). Start it with the "🧺 Start Collection Scan" button in the Detection view (falls back to YOLO-class deduplication if the identification index is missing).

-   **One-Click Training**: Configure and launch training for YOLOv8 or YOLOv11 models with a single click.
-   **Real-time Metrics**: Monitor training progress with live charts for mAP, precision, recall, and loss.
-   **Live Detection**: Use your trained model for real-time detection via webcam, video file, or static images.
-   **System Profiles**: Pre-configured profiles for Desktop, Laptop, and **Jetson Orin AGX 32GB**.
-   **Jetson Export**: Export models to **TensorRT** for optimized edge inference (2-3x speedup).

> **➡️ [Learn more in the detailed Training and Detection guide](./features/3_TRAINING_AND_DETECTION.md)**

---

## 4. 💰 Price System

Integrate real-time market prices directly into the detection process, providing instant feedback on the value of detected cards.

-   **Automatic Mapping**: Links the detected card name to its official database ID.
-   **Local Price Database**: Fetches and caches prices from Cardmarket and TCGPlayer into a local Excel file to minimize API calls.
-   **Live Price Overlay**: Displays the card's market price directly on the bounding box during detection.
-   **Offline Price Snapshot**: Preload prices into a local SQLite cache (`python tools/preload_prices.py --set sv08`, `--database`, or `--inventory <scan.csv>`; also the "⬇ Preload Prices" button in the Detection view) — detection and collection scans then display prices with **no network at all**. The snapshot date is always visible ("💾 152 prix, snapshot du 2026-07-12"), a freshness TTL (24h) controls when prices are re-fetched, and every fetch is kept as a timestamped history row.
-   **Price History & Alerts**: The "💹 Price History" window plots each card's price evolution as a sparkline (persistent across sessions, fed by every preload) and manages threshold alerts: get notified when a card rises **above** or drops **below** a price. Alerts are checked after every preload, disarm when they fire (no spam) and re-arm automatically once the price crosses back.

> **➡️ [Learn more in the detailed Price System guide](./features/4_PRICE_SYSTEM.md)**

---

**Last Updated**: November 28, 2025
**Version**: 3.4.1
