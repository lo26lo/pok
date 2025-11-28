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

### System Profiles

The GUI includes pre-configured system profiles optimized for different hardware:

| Profile | Hardware | Batch | ImgSize | Cache | Notes |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 🖥️ Desktop | 5800X3D + 5070 Ti 16GB | 32 | 640 | RAM | High VRAM, full speed |
| 💼 Laptop | Ryzen AI 7 + 5070 8GB | 16 | 512 | Disk | Reduced batch for 8GB |
| 🤖 **Jetson Orin AGX** | Orin AGX 32GB | 16 | 640 | Disk | Unified memory optimized |

### 🤖 Jetson Orin AGX Presets

Special presets optimized for edge AI deployment on NVIDIA Jetson:

| Preset | Model | ImgSize | Batch | Epochs | Target |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 🚀 Jetson Realtime | yolov8n | 320 | 24 | 30 | **>60 FPS** inference |
| 🤖 Jetson Optimized | yolov8n | 480 | 16 | 80 | Best accuracy/speed trade-off |
| 🎯 High Quality | yolov8s | 640 | 8 | 100 | Maximum precision |

**Jetson-specific optimizations**:
- Workers set to 2 (ARM CPU has fewer cores than x86)
- Disk cache preserves unified memory for GPU
- Cosine LR scheduler for better convergence

### Export for Jetson (TensorRT)

After training, export your model for optimal inference on Jetson:

1. Click **"🚀 Export for Jetson (TensorRT)"**
2. Choose export format:
   - **TensorRT Engine** (.engine) - 2-3x speedup on Jetson
   - **ONNX** (.onnx) - Portable, convert on Jetson
   - **TorchScript** - PyTorch native
3. Enable **FP16** for best Jetson performance
4. Copy exported file to your Jetson device

The training view displays live metrics including **mAP50**, **mAP50-95**, **precision**, **recall**, and loss curves, updated in real-time as training progresses.

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

During detection, each identified card displays its name, confidence score (0-100%), and real-time market price fetched from the integrated price database.

---

## 📚 Navigation

⬅️ [Previous: Dataset Generation](2_DATASET_GENERATION.md) | [Back to Features Overview](../FEATURES.md) | ➡️ [Next: Price System](4_PRICE_SYSTEM.md)

---

**Last Updated**: November 28, 2025
