"""Détection YOLO : webcam temps réel, image unique, dossier (DetectionManager)."""
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSlider,
    QSpinBox, QWidget,
)
from PySide6.QtCore import Qt

from core.utils import PATHS
from gui.task_runner import TaskError
from gui_qt.widgets import Card, PathPicker, form_row, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🔍 Détection")

        card = Card("Configuration de la détection")
        self.model_path = PathPicker(PATHS['files']['best_model'],
                                     directory=False,
                                     file_filter="Modèles YOLO (*.pt)")

        self.confidence = QSlider(Qt.Horizontal)
        self.confidence.setRange(5, 95)
        self.confidence.setValue(50)
        self.conf_label = QLabel("0.50")
        self.confidence.valueChanged.connect(
            lambda v: self.conf_label.setText(f"{v / 100:.2f}"))
        conf_row = QHBoxLayout()
        conf_row.addWidget(self.confidence, 1)
        conf_row.addWidget(self.conf_label)

        self.camera_id = QSpinBox()
        self.camera_id.setRange(0, 10)
        self.show_prices = QCheckBox("Afficher les prix (base cards_database.yaml)")
        self.show_prices.setChecked(True)

        card.add_layout(form_row("Modèle (.pt)", self.model_path))
        conf_container = QWidget(); conf_container.setLayout(conf_row)
        card.add_layout(form_row("Confiance min", conf_container))
        card.add_layout(form_row("Caméra (ID)", self.camera_id))
        card.add(self.show_prices)
        content.addWidget(card)

        actions = Card("Lancer")
        row = QHBoxLayout()
        webcam_btn = QPushButton("📷 Webcam temps réel")
        webcam_btn.setObjectName("primary")
        webcam_btn.clicked.connect(self.start_webcam)
        image_btn = QPushButton("🖼️ Image…")
        image_btn.clicked.connect(self.start_image)
        folder_btn = QPushButton("📁 Dossier…")
        folder_btn.clicked.connect(self.start_folder)
        for b in (webcam_btn, image_btn, folder_btn):
            row.addWidget(b)
        row.addStretch(1)
        actions.add_layout(row)

        hint = QLabel("La fenêtre de détection s'ouvre via OpenCV — touche 'q' pour quitter.")
        hint.setObjectName("dim")
        actions.add(hint)
        content.addWidget(actions)

    # ------------------------------------------------------------------ util

    def _make_config(self):
        from core.detection_manager import DetectionConfig
        model = Path(self.model_path.text())
        if not model.exists():
            self.main.notify_error("Erreur",
                                   f"Modèle non trouvé:\n{model}\n\nEntraînez d'abord un modèle.")
            return None
        return DetectionConfig(
            model_path=model,
            confidence=self.confidence.value() / 100,
            camera_id=self.camera_id.value(),
            show_prices=self.show_prices.isChecked(),
        )

    def _run(self, name, fn, success_message):
        main = self.main

        def work(runner):
            from core.detection_manager import DetectionManager
            config = self._config
            manager = DetectionManager(config)
            manager.set_log_callback(runner.log)
            try:
                fn(manager)
            except TaskError:
                raise
            except Exception as exc:
                raise TaskError(f"Détection échouée: {exc}")

        main.bridge.run(name, work,
                        on_success=lambda: main.notify_info("Terminé", success_message),
                        on_error=lambda msg: main.notify_error("Erreur", msg))

    # ------------------------------------------------------------ opérations

    def start_webcam(self):
        config = self._make_config()
        if config is None:
            return
        self._config = config
        self.main.log(f"📷 Détection webcam (caméra {config.camera_id}, "
                      f"conf {config.confidence:.2f})")
        self._run("Webcam Detection",
                  lambda m: m.detect_webcam(),
                  "Session webcam terminée.")

    def start_image(self):
        config = self._make_config()
        if config is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image", "images",
            "Images (*.png *.jpg *.jpeg *.webp)")
        if not path:
            return
        save_path = str(Path("detection_output") / Path(path).name)
        Path("detection_output").mkdir(exist_ok=True)
        self._config = config
        self.main.log(f"🖼️ Détection sur image: {path}")
        self._run("Image Detection",
                  lambda m: m.detect_image(path, save_path=save_path),
                  f"Détection terminée.\nImage annotée: {save_path}")

    def start_folder(self):
        config = self._make_config()
        if config is None:
            return
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier", "images")
        if not folder:
            return
        self._config = config
        self.main.log(f"📁 Détection sur dossier: {folder}")
        self._run("Folder Detection",
                  lambda m: m.detect_folder(folder),
                  f"Détection terminée sur\n{folder}")
