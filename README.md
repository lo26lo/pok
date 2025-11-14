<div align="center">

<img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/banner.png" alt="Pokemon Dataset Generator Banner" width="100%"/>

# 🎮 Pokémon Dataset Generator v3.2

**A complete YOLO pipeline with a modern GUI: from Dataset Generation to Live Price Detection.**

<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge&logo=python" alt="Python 3.12"></a>
    <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License: MIT"></a>
    <a href="https://ultralytics.com/"><img src="https://img.shields.io/badge/YOLOv8-Ultralytics-purple.svg?style=for-the-badge" alt="YOLOv8"></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge" alt="Code style: black"></a>
</p>

[**📖 Full Documentation**](docs/README_COMPLET.md) • [**🚀 Feature List**](docs/FEATURES.md) • [**📜 Changelog**](docs/CHANGELOG.md)

</div>

---

### ✨ The All-in-One Toolkit for Pokémon Card Recognition

This project provides a powerful and intuitive graphical interface to manage the entire lifecycle of a custom YOLO object detector for Pokémon cards. From data creation to final deployment, every step is included.

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/gui_dashboard.png" alt="GUI Dashboard" width="100%"/>
      <br><em>Modern dashboard with real-time stats.</em>
    </td>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/detection_with_prices.png" alt="Detection with Prices" width="100%"/>
      <br><em>Live detection with market prices.</em>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/example_layout_annotated.png" alt="Annotated Mosaic" width="100%"/>
      <br><em>Generate complex, annotated mosaics for training.</em>
    </td>
    <td align="center" width="50%">
      <img src="https://raw.githubusercontent.com/lo26lo/pok/main/examples/gui_settings.png" alt="Settings" width="100%"/>
      <br><em>Fine-tune every parameter in the settings.</em>
    </td>
  </tr>
</table>

---

### 🚀 Core Pipeline: Generate → Train → Detect

Our philosophy is to simplify the complex workflow of creating a detector into three intuitive stages.

| Step | Icon | Description | Key Features |
| :--- | :---: | :--- | :--- |
| **1. Generate** | 🖼️ | **Create rich, diverse datasets.** Automatically download cards, apply augmentations, create holographic effects, and build complex annotated mosaics. | `Augmentation` `Mosaics` `Holographic` |
| **2. Train** | 🎓 | **Train a state-of-the-art YOLOv8 model.** Use your generated dataset to train a powerful detector with a single click, right from the GUI. | `YOLOv8` `One-Click` `Metrics` |
| **3. Detect** | 📹 | **Deploy your model for live detection.** Use your webcam or video files to find cards and instantly see their market price from Cardmarket & TCGPlayer. | `Live Detection` `Price API` `Real-time` |

---

### 🌟 Feature Spotlight

This project is packed with features to make your life easier. Here are some highlights:

| Category | Features |
| :--- | :--- |
| 🎨 **Interface & UX** | <ul><li>Modern GUI with a real-time dashboard</li><li>Collapsible sidebar for more workspace</li><li>Instantly switch between Dark & Light themes</li><li>8-tab settings dialog, including an advanced `Debug` menu</li><li>Live log panel in the footer</li><li>Dashboard quick actions for presets and reports</li></ul> |
| ⚙️ **Dataset Generation** | <ul><li>Automatic card image downloader (TCGdex API)</li><li>22+ augmentation techniques via `imgaug`</li><li>5+ realistic holographic effects (rainbow, metallic, etc.)</li><li>Annotated mosaic generation for robust training</li><li>Automatic class balancing to prevent dataset bias</li></ul> |
| 🎓 **Training & Detection** | <ul><li>Support for multiple YOLO architectures (v8, v11)</li><li>One-click model training directly from the GUI</li><li>Live detection from webcam, video, or image files</li><li>Real-time market price integration (Cardmarket, TCGPlayer)</li><li>Export datasets to COCO, VOC, and other standard formats</li></ul> |
| 🛠️ **Project & Maintenance** | <ul><li>Centralized script system (`run_script.bat`, `run_test.bat`)</li><li>Isolated `.venv` environment for clean dependency management</li><li>Project integrity tests to validate structure and dependencies</li><li>Comprehensive documentation for every feature</li></ul> |

> For a complete list and detailed explanations, check out the [**Features Guide**](docs/FEATURES.md).

---

### 🛠️ Tech Stack

This project leverages a modern stack for computer vision and application development:

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch"></a>
  <a href="https://ultralytics.com/"><img src="https://img.shields.io/badge/YOLOv8-0052D4?style=for-the-badge" alt="YOLOv8"></a>
  <a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"></a>
  <a href="https://docs.python.org/3/library/tkinter.html"><img src="https://img.shields.io/badge/Tkinter-2B5B84?style=for-the-badge&logo=tcl&logoColor=white" alt="Tkinter"></a>
</p>

---

### ⚡ Quick Start

Get up and running in two simple steps.

**1. Prerequisites**
- Windows 10/11
- Python 3.10, 3.11, or 3.12
- NVIDIA GPU (recommended for training)

**2. Installation & Launch**
```batch
:: 1. Install all dependencies into a virtual environment
INSTALL.bat

:: 2. Launch the application
START.bat
```
That's it! The application is ready to use.

---

### 📚 Documentation Hub

All documentation is located in the `docs/` folder. Here are some important starting points:

| Guide | Description |
| :--- | :--- |
| 📖 **[Complete Guide](docs/README_COMPLET.md)** | The main documentation with in-depth details on everything. |
| 🚀 **[Features Overview](docs/FEATURES.md)** | High-level overview with links to detailed feature guides. |
| 🎨 **[GUI Overview](docs/features/1_GUI_OVERVIEW.md)** | Complete interface documentation. |
| ⚙️ **[Dataset Generation](docs/features/2_DATASET_GENERATION.md)** | Download, augmentation, mosaics, and balancing. |
| 🎓 **[Training & Detection](docs/features/3_TRAINING_AND_DETECTION.md)** | YOLO training and live detection. |
| 💰 **[Price System](docs/features/4_PRICE_SYSTEM.md)** | Card mapping and price integration. |
| 🖥️ **[GUI Guide](docs/GUI_V3_GUIDE.md)** | Detailed GUI walkthrough. |
| 🛠️ **[Scripts Reference](docs/MAINTENANCE_SCRIPTS_REFERENCE.md)** | All maintenance and utility scripts. |
| 📜 **[Changelog](docs/CHANGELOG.md)** | Complete history of changes, features, and fixes. |

---

### 🤝 Contributing

Contributions are welcome! Please read the [contributing guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
