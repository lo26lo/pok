"""Entraînement YOLO (TrainingManager) + presets + export ONNX/TensorRT."""
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout, QPushButton,
    QSpinBox, QWidget,
)

from core.utils import PATHS
from gui.task_runner import TaskError
from gui_qt.widgets import Card, form_row, view_scaffold

# Presets (repris de la v3.4.1, incluant Jetson Orin)
PRESETS = {
    "— Preset —": None,
    "⚡ Fast & Efficient": dict(model="yolov8n.pt", imgsz=416, batch=16, epochs=50, patience=50),
    "⚖️ Balanced": dict(model="yolov8n.pt", imgsz=512, batch=12, epochs=50, patience=50),
    "🎯 High Quality": dict(model="yolov8s.pt", imgsz=640, batch=8, epochs=100, patience=75),
    "🚀 Jetson Realtime": dict(model="yolov8n.pt", imgsz=320, batch=24, epochs=30, patience=30),
    "🤖 Jetson Optimized": dict(model="yolov8n.pt", imgsz=480, batch=16, epochs=80, patience=60),
}


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🎓 Training YOLO")

        cfg = main.config

        # --- Hyperparamètres -------------------------------------------------
        card = Card("Configuration de l'entraînement")
        self.preset = QComboBox(); self.preset.addItems(list(PRESETS.keys()))
        self.preset.currentTextChanged.connect(self.apply_preset)

        self.model = QComboBox()
        self.model.addItems(["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"])
        self.model.setCurrentText(cfg.get("default_model", "yolov8n.pt"))
        self.epochs = QSpinBox(); self.epochs.setRange(1, 2000)
        self.epochs.setValue(int(cfg.get("default_epochs", 50)))
        self.batch = QSpinBox(); self.batch.setRange(1, 256)
        self.batch.setValue(int(cfg.get("default_batch", 16)))
        self.imgsz = QComboBox()
        self.imgsz.addItems(["320", "416", "480", "512", "640", "800", "1024"])
        self.imgsz.setCurrentText("640")
        self.device = QComboBox(); self.device.setEditable(True)
        self.device.addItems(["0", "cpu", "0,1", "0,1,2,3"])
        self.device.setCurrentText(str(cfg.get("default_device", "0")))
        self.workers = QSpinBox(); self.workers.setRange(0, 32); self.workers.setValue(4)
        self.cache = QComboBox(); self.cache.addItems(["False", "ram", "disk"])

        self.lr0 = QDoubleSpinBox(); self.lr0.setDecimals(4)
        self.lr0.setRange(0.0001, 1.0); self.lr0.setSingleStep(0.001); self.lr0.setValue(0.01)
        self.lrf = QDoubleSpinBox(); self.lrf.setDecimals(4)
        self.lrf.setRange(0.0001, 1.0); self.lrf.setSingleStep(0.001); self.lrf.setValue(0.01)
        self.cosine = QCheckBox("Cosine LR scheduler")
        self.patience = QSpinBox(); self.patience.setRange(1, 1000); self.patience.setValue(50)

        for label, widget in [("Preset", self.preset), ("Modèle", self.model),
                              ("Epochs", self.epochs), ("Batch size", self.batch),
                              ("Image size", self.imgsz), ("Device", self.device),
                              ("Workers", self.workers), ("Cache", self.cache),
                              ("Learning rate (lr0)", self.lr0),
                              ("LR final (lrf)", self.lrf),
                              ("Patience (early stop)", self.patience)]:
            card.add_layout(form_row(label, widget))
        card.add(self.cosine)

        start = QPushButton("🎓 Lancer l'entraînement")
        start.setObjectName("primary")
        start.clicked.connect(self.start_training)
        card.add(start)
        content.addWidget(card)

        # --- Export ------------------------------------------------------------
        export_card = Card("🚀 Exporter le modèle entraîné (edge/Jetson)")
        self.export_format = QComboBox()
        self.export_format.addItems(["onnx", "engine", "torchscript"])
        export_card.add_layout(form_row("Format", self.export_format))
        export_btn = QPushButton("🚀 Exporter best.pt")
        export_btn.clicked.connect(self.start_export)
        export_row = QHBoxLayout()
        export_row.addWidget(export_btn)
        export_row.addStretch(1)
        export_card.add_layout(export_row)
        content.addWidget(export_card)

    # --------------------------------------------------------------- presets

    def apply_preset(self, name: str):
        preset = PRESETS.get(name)
        if not preset:
            return
        self.model.setCurrentText(preset["model"])
        self.imgsz.setCurrentText(str(preset["imgsz"]))
        self.batch.setValue(preset["batch"])
        self.epochs.setValue(preset["epochs"])
        self.patience.setValue(preset["patience"])
        self.main.log(f"✅ Preset appliqué: {name}")

    # ------------------------------------------------------------ opérations

    def start_training(self):
        main = self.main
        data_yaml = Path(PATHS['files']['dataset_data_yaml'])
        if not data_yaml.exists():
            main.notify_error("Erreur",
                              f"data.yaml non trouvé!\n{data_yaml}\n\n"
                              "Générez d'abord le dataset (Augmentation + Mosaïques + Merge).")
            return

        params = dict(
            model_name=self.model.currentText(),
            epochs=self.epochs.value(),
            batch_size=self.batch.value(),
            image_size=int(self.imgsz.currentText()),
            device=self.device.currentText(),
            workers=self.workers.value(),
            cache=self.cache.currentText(),
            lr0=self.lr0.value(),
            lrf=self.lrf.value(),
            cos_lr=self.cosine.isChecked(),
            patience=self.patience.value(),
            data_yaml=data_yaml,
        )
        results = {}

        def work(runner):
            from core.training_manager import TrainingManager, TrainingConfig
            config = TrainingConfig(**params)
            manager = TrainingManager(config)
            manager.set_log_callback(runner.log)

            runner.log(f"🎓 Démarrage entraînement: {params['model_name']} "
                       f"({params['epochs']} epochs, batch {params['batch_size']})")
            if not manager.train():
                raise TaskError("Entraînement échoué (voir logs — "
                                "ultralytics installé ? GPU disponible ?)")
            results['best'] = str(manager.get_best_model_path())
            results['metrics'] = manager.get_metrics() or {}

        def on_success():
            metrics = results.get('metrics', {})
            msg = f"✅ Entraînement terminé!\n\nModèle: {results.get('best')}"
            if metrics:
                msg += (f"\n\nmAP50: {metrics.get('mAP50', 0):.3f}"
                        f"\nmAP50-95: {metrics.get('mAP50-95', 0):.3f}")
            main.notify_info("Succès", msg)

        main.bridge.run("Training", work,
                        on_success=on_success,
                        on_error=lambda msg: main.notify_error("Erreur", msg))

    def start_export(self):
        main = self.main
        fmt = self.export_format.currentText()
        best = Path(PATHS['files']['best_model'])
        if not best.exists():
            main.notify_error("Erreur", f"Modèle non trouvé:\n{best}\n\nEntraînez d'abord.")
            return
        results = {}

        def work(runner):
            from core.training_manager import TrainingManager, TrainingConfig
            config = TrainingConfig(data_yaml=Path(PATHS['files']['dataset_data_yaml']))
            manager = TrainingManager(config)
            manager.set_log_callback(runner.log)
            runner.log(f"🚀 Export {best} → {fmt}...")
            exported = manager.export_model(model_path=best, format=fmt)
            if exported is None:
                raise TaskError(f"Export {fmt} échoué (voir logs)")
            results['path'] = str(exported)

        main.bridge.run("Model Export", work,
                        on_success=lambda: main.notify_info(
                            "Succès", f"Modèle exporté:\n{results.get('path')}"),
                        on_error=lambda msg: main.notify_error("Erreur", msg))
