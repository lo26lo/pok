"""Dashboard : statistiques du projet + workflow automatique + accès rapides."""
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QWidget,
)

from core.utils import PATHS
from core.workflow_manager import WorkflowManager, WorkflowConfig
from gui_qt.widgets import Card, form_row, view_scaffold


def _count_images(directory: str) -> int:
    path = Path(directory)
    if not path.exists():
        return 0
    return sum(1 for f in path.iterdir()
               if f.suffix.lower() in ('.png', '.jpg', '.jpeg'))


def _dir_size_mb(directory: str) -> float:
    total = 0
    for root, _, files in os.walk(directory):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except OSError:
                pass
    return total / (1024 * 1024)


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🏠 Dashboard")

        # --- Statistiques -------------------------------------------------
        stats_card = Card("📊 Statistiques du projet")
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        self._stat_labels = {}
        for col, (key, label) in enumerate([
                ("source", "Images source"),
                ("augmented", "Augmentées"),
                ("mosaics", "Mosaïques"),
                ("dataset", "Dataset final"),
                ("size", "Taille output")]):
            value = QLabel("—")
            value.setObjectName("statValue")
            caption = QLabel(label)
            caption.setObjectName("dim")
            grid.addWidget(value, 0, col)
            grid.addWidget(caption, 1, col)
            self._stat_labels[key] = value
        stats_card.add_layout(grid)

        refresh = QPushButton("🔄 Rafraîchir")
        refresh.clicked.connect(self.refresh_stats)
        stats_card.add(refresh)
        content.addWidget(stats_card)

        # --- Workflow automatique ----------------------------------------
        wf_card = Card("🚀 Workflow automatique (Augment → Mosaïques → Merge → …)")
        self.wf_aug = QSpinBox(); self.wf_aug.setRange(1, 500); self.wf_aug.setValue(15)
        self.wf_mode = QComboBox(); self.wf_mode.addItems(["quick", "standard", "complete"])
        self.wf_mode.setCurrentText("standard")
        self.wf_validate = QCheckBox("Validation"); self.wf_validate.setChecked(True)
        self.wf_balance = QCheckBox("Auto-balancing")
        self.wf_train = QCheckBox("Entraînement YOLO")

        wf_card.add_layout(form_row("Augmentations / image", self.wf_aug))
        wf_card.add_layout(form_row("Mode mosaïques", self.wf_mode))
        options = QHBoxLayout()
        for cb in (self.wf_validate, self.wf_balance, self.wf_train):
            options.addWidget(cb)
        options.addStretch(1)
        wf_card.add_layout(options)

        start = QPushButton("🚀 Lancer le workflow complet")
        start.setObjectName("primary")
        start.clicked.connect(self.start_workflow)
        wf_card.add(start)
        content.addWidget(wf_card)

        # --- Accès rapides -------------------------------------------------
        quick = Card("⚡ Accès rapides")
        row = QHBoxLayout()
        for label, view_id in [("⬇️ Download", "download"),
                               ("🎨 Augmentation", "augmentation"),
                               ("🧩 Mosaïques", "mosaic"),
                               ("🎓 Training", "training"),
                               ("🔍 Détection", "detection")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _=False, v=view_id: self.main.goto(v))
            row.addWidget(btn)
        quick.add_layout(row)
        content.addWidget(quick)

        self.refresh_stats()

    # ------------------------------------------------------------------ API

    def refresh_stats(self):
        dirs = PATHS['directories']
        self._stat_labels["source"].setText(str(_count_images(dirs['images'])))
        self._stat_labels["augmented"].setText(
            str(_count_images(dirs['output_augmented_images'])))
        self._stat_labels["mosaics"].setText(
            str(_count_images(dirs['output_mosaics_images'])))
        self._stat_labels["dataset"].setText(
            str(_count_images(str(Path(dirs['output_dataset']) / "images"))))
        size = _dir_size_mb(dirs['output_base']) if Path(dirs['output_base']).exists() else 0
        self._stat_labels["size"].setText(f"{size:.0f} MB")

    def start_workflow(self):
        num_aug = self.wf_aug.value()
        mode = self.wf_mode.currentText()
        do_validate = self.wf_validate.isChecked()
        do_balance = self.wf_balance.isChecked()
        do_train = self.wf_train.isChecked()

        summary = (f"1️⃣ Augmentation : {num_aug} variations\n"
                   f"2️⃣ Mosaïques : mode {mode}\n"
                   f"3️⃣ Validation : {'✅' if do_validate else '❌'}\n"
                   f"4️⃣ Auto-balancing : {'✅' if do_balance else '❌'}\n"
                   f"5️⃣ Entraînement : {'✅' if do_train else '❌'}\n\nContinuer ?")
        if not self.main.confirm("🚀 Lancer le workflow", summary):
            return

        main = self.main

        def work(runner):
            config = WorkflowConfig(
                num_augmentations=num_aug,
                mosaic_mode=mode,
                enable_validation=do_validate,
                enable_balancing=do_balance,
                enable_training=do_train,
            )
            manager = WorkflowManager(config)
            manager.set_log_callback(runner.log)
            manager.run()
            if not manager.is_success():
                from gui.task_runner import TaskError
                raise TaskError("Workflow échoué (voir logs)")

        main.bridge.run(
            "Auto Workflow", work,
            on_success=lambda: main.notify_info("Succès", "🎉 Workflow terminé !"),
            on_error=lambda msg: main.notify_error("Erreur", msg))
