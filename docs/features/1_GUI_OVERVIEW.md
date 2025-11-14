# 🎨 GUI Overview

This document provides a detailed overview of the main components of the Pokémon Dataset Generator's graphical user interface (GUI).

---

## 📱 Main Layout

The interface is designed to be modern, intuitive, and organized around the main workflow. It consists of three main areas:

1.  **Sidebar (Left)**: Provides navigation between the main functional tabs. It can be collapsed to maximize workspace.
2.  **Main Content Area (Center)**: Displays the active view (Dashboard, Augmentation, Training, etc.).
3.  **Footer Log Panel (Bottom)**: Shows real-time logs of all operations. It can be expanded for detailed inspection.

<p align="center">
  <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/gui_dashboard.png" alt="GUI Dashboard" width="90%"/>
</p>

---

## 📊 Dashboard (Home View)

The Dashboard is the central hub of the application, providing at-a-glance information and quick access to key functions.

### Key Components

| Component | Description |
| :--- | :--- |
| **Statistics Panel** | Displays real-time counters for source images, augmentations, mosaics, and total dataset size. |
| **System Status** | Verifies the environment: checks for the `.venv`, dependencies, and essential files. Provides a "Fix Now" button for common issues. |
| **Quick Actions** | Buttons and cards for frequently used operations, such as applying training presets or opening the latest validation report. |
| **Progress Indicators** | Animated progress bars and detailed status updates appear here during active operations. |

---

## ⚙️ Settings Dialog

The settings dialog, accessible via the "⚙️ Settings" button, allows for fine-grained control over every aspect of the application. It is organized into 8 distinct tabs.

| Tab | Description |
| :--- | :--- |
| **📁 General** | Configure default directories for images, outputs, and other generated files. |
| **🎨 Augmentation** | Set the default number of augmentations, holographic intensity, and variations. |
| **🧩 Mosaic** | Define default settings for mosaic generation: mode, layout, background, and transformations. |
| **🎲 Fake Images** | Control the parameters for the random erasing technique used to generate fake backgrounds. |
| **📥 Download** | Configure TCGdex API download settings: language, quality, format, and parallel workers. |
| **🎓 Training** | Set default training parameters: model size (n/s/m/l/x), epochs, batch size, and device. |
| **🔧 Advanced** | Enter your TCGdex API key (optional) for extended features. |
| **🐛 Debug** | Access advanced options for performance tuning and debugging: device selection, worker count, log level, cache mode, and profiling tools. |

**Access Settings**: Click the gear icon (⚙️) in the top toolbar or press `Ctrl+,` to open the settings dialog.

---

## 🗺️ Main Functional Tabs

The application workflow is organized into a series of tabs, accessible from the sidebar.

1.  **🏠 Dashboard**: The home screen.
2.  **📥 Image Download**: Download card images from the TCGdex API.
3.  **🎨 Augmentation**: Apply 22+ types of transformations to your images.
4.  **🌈 Holographic**: Add 5+ styles of realistic shiny effects.
5.  **🧩 Mosaics**: Generate complex, annotated mosaic images for training.
6.  **✅ Validation**: Verify the integrity and format of your YOLO dataset.
7.  **🎓 Training**: Train a YOLOv8 model on your generated dataset.
8.  **📹 Detection**: Use your trained model for live detection.
7.  **🅘 Workflow**: Automate the entire pipeline from augmentation to training.

---

## 📚 Navigation

⬅️ [Back to Features Overview](../FEATURES.md) | ➡️ [Next: Dataset Generation](2_DATASET_GENERATION.md)

---

**Last Updated**: November 14, 2025
