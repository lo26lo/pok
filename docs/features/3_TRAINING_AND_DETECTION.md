# 🎓 Training and Detection

This document explains the features related to training your YOLO model and using it for live detection.

---

## 🎓 YOLO Training

The GUI provides a simple interface to train a powerful YOLOv8 model on your custom-generated dataset.

### Key Training Features

| Feature | Description |
| :--- | :--- |
| **Model Support** | Natively supports **YOLOv8** and **YOLOv11** architectures. |
| **Model Sizes** | Choose from 5 model sizes: `n` (nano), `s` (small), `m` (medium), `l` (large), `x` (extra-large). |
| **One-Click Training** | Configure all parameters (epochs, batch size, image size) and start training with a single button click. |
| **Real-time Metrics** | The training dashboard displays live metrics, including **mAP**, **precision**, **recall**, and loss curves. |
| **GPU Acceleration** | Automatically detects and uses your NVIDIA GPU for significantly faster training. |
| **Interruptible** | A "Stop" button allows you to safely interrupt the training process at any time. |

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/training_metrics.png" alt="Training Metrics" width="80%"/>
  <br><em>Live training dashboard showing key performance metrics.</em>
</p>

### Training Output

Upon completion, the following files are generated in the `runs/train/pokemon_detector/` directory:

-   **`weights/best.pt`**: The model with the best validation performance. **This is the model you should use for detection.**
-   **`weights/last.pt`**: The model from the very last epoch.
-   **`results.png`**: A plot of all metric curves over the training epochs.
-   **`confusion_matrix.png`**: A confusion matrix showing class-level performance.
-   **`val_batch0_pred.jpg`**: Example validation images with predicted bounding boxes.

---

## 📹 Live Detection

Once your model is trained, you can immediately use it for real-time object detection.

### Detection Modes

-   **Webcam**: Detect cards in real-time using your computer's webcam.
-   **Video**: Process a pre-recorded video file and detect cards frame-by-frame.
-   **Image**: Run detection on a single image or a batch of images in a folder.

### Core Detection Features

-   **Price Integration**: Displays the market price from Cardmarket or TCGPlayer directly on the bounding box of detected cards. (See [Price System Guide](4_PRICE_SYSTEM.md) for more info).
-   **Confidence Threshold**: Adjust the detection sensitivity (default is 0.5) to filter out weak detections.
-   **Visual Overlay**: Clearly shows bounding boxes, class names (card names), confidence scores, and prices.
-   **Recording**: Option to record the output of webcam or video detections.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/detection_with_prices.png" alt="Detection with Prices" width="80%"/>
  <br><em>Live detection showing card name, confidence, and market price.</em>
</p>

---

## 📚 Navigation

⬅️ [Previous: Dataset Generation](2_DATASET_GENERATION.md) | [Back to Features Overview](../FEATURES.md) | ➡️ [Next: Price System](4_PRICE_SYSTEM.md)

---

**Last Updated**: November 14, 2025
