"""Augmentation d'images (Albumentations) + pipeline holographic."""
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSlider, QSpinBox, QWidget,
)

from core.augmentation_albumentations import AUGMENTATION_CATEGORIES
from core.utils import PATHS
from gui.task_runner import TaskError
from gui_qt.widgets import Card, form_row, view_scaffold

_CATEGORY_LABELS = {
    "brightness": "💡 Luminosité", "color": "🎨 Couleurs",
    "blur": "🌫️ Flou/Netteté", "noise": "📶 Bruit",
    "environment": "🌤️ Environnement", "geometry": "📐 Géométrie",
}


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🎨 Augmentation")

        cfg = main.config

        # --- Augmentation simple ------------------------------------------
        aug_card = Card("🎨 Augmentation (Albumentations, 25 transformations)")
        self.num_aug = QSpinBox()
        self.num_aug.setRange(1, 500)
        self.num_aug.setValue(int(cfg.get("default_augmentations", 50)))
        self.aug_type = QComboBox()
        self.aug_type.addItems(["Standard", "Holographic", "Both"])
        self.target = QLineEdit("augmented")

        aug_card.add_layout(form_row("Variations par image", self.num_aug))
        aug_card.add_layout(form_row("Type", self.aug_type))
        aug_card.add_layout(form_row("Dossier cible", self.target))

        # --- Paramètres du pipeline (F06) : intensité, nb transfos, catégories
        self.intensity = QSlider(Qt.Horizontal)
        self.intensity.setRange(10, 200)     # 0.1x – 2.0x (÷100)
        self.intensity.setValue(100)
        self.intensity_label = QLabel("1.00×")
        self.intensity.valueChanged.connect(
            lambda v: self.intensity_label.setText(f"{v / 100:.2f}×"))
        int_row = QHBoxLayout()
        int_row.addWidget(self.intensity, 1)
        int_row.addWidget(self.intensity_label)
        int_container = QWidget(); int_container.setLayout(int_row)
        aug_card.add_layout(form_row("Intensité globale", int_container))

        self.n_transforms = QSpinBox()
        self.n_transforms.setRange(0, 25)
        self.n_transforms.setSpecialValueText("aléatoire (3-6)")
        aug_card.add_layout(form_row("Transformations / image", self.n_transforms))

        aug_card.add(QLabel("Catégories incluses :"))
        cats = QGridLayout()
        self.category_boxes = {}
        for i, cat in enumerate(AUGMENTATION_CATEGORIES):
            box = QCheckBox(_CATEGORY_LABELS.get(cat, cat))
            box.setChecked(True)
            self.category_boxes[cat] = box
            cats.addWidget(box, i // 3, i % 3)
        aug_card.add_layout(cats)

        start = QPushButton("🎨 Lancer l'augmentation")
        start.setObjectName("primary")
        start.clicked.connect(self.start_augmentation)
        aug_card.add(start)
        content.addWidget(aug_card)

        # --- Pipeline Holo → Augment ----------------------------------------
        pipe_card = Card("🚀 Pipeline complet : Holographic → Augmentation")
        self.pipe_holo = QSpinBox(); self.pipe_holo.setRange(0, 20)
        self.pipe_holo.setValue(int(cfg.get("holographic_variations", 3)))
        self.pipe_aug = QSpinBox(); self.pipe_aug.setRange(0, 500); self.pipe_aug.setValue(15)

        pipe_card.add_layout(form_row("Variations holographiques", self.pipe_holo))
        pipe_card.add_layout(form_row("Augmentations par image", self.pipe_aug))

        row = QHBoxLayout()
        pipe_btn = QPushButton("🚀 Lancer le pipeline")
        pipe_btn.setObjectName("primary")
        pipe_btn.clicked.connect(self.start_pipeline)
        row.addWidget(pipe_btn)
        row.addStretch(1)
        pipe_card.add_layout(row)
        content.addWidget(pipe_card)

    # ------------------------------------------------------------ opérations

    def _param_flags(self) -> list:
        """Drapeaux CLI des paramètres calibrés (F06) pour la génération."""
        flags = ["--intensity", f"{self.intensity.value() / 100:.2f}",
                 "--transforms", str(self.n_transforms.value())]
        selected = [c for c, b in self.category_boxes.items() if b.isChecked()]
        if selected and len(selected) < len(AUGMENTATION_CATEGORIES):
            flags += ["--categories", ",".join(selected)]
        return flags

    def start_augmentation(self):
        main = self.main
        num_aug = self.num_aug.value()
        aug_type = self.aug_type.currentText()
        target = self.target.text().strip() or "augmented"
        holo_variations = int(main.config.get("holographic_variations", 3))
        param_flags = self._param_flags()

        if not any(b.isChecked() for b in self.category_boxes.values()):
            main.notify_warning("Attention",
                                "Sélectionnez au moins une catégorie d'augmentation.")
            return

        main.log(f"🎨 Augmentation ({aug_type}): {num_aug} variations → {target}/ "
                 f"(intensité {self.intensity.value() / 100:.2f}×)")

        def work(runner):
            if aug_type in ("Standard", "Both"):
                runner.log("🎨 Running standard augmentation (Albumentations)...")
                returncode = runner.stream(
                    [sys.executable, "-u", "core/augmentation_albumentations.py",
                     "--num_aug", str(num_aug), "--target", target, *param_flags])
                if returncode != 0:
                    runner.log("❌ Standard augmentation failed!")
                    if aug_type == "Standard":
                        raise TaskError("Augmentation échouée!")
                else:
                    runner.log("✅ Standard augmentation completed!")

            if aug_type in ("Holographic", "Both"):
                runner.log("✨ Running holographic augmentation...")
                output_dir = target + "_holographic" if aug_type == "Both" else target
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                     "images", output_dir, "--variations", str(holo_variations)],
                    "Augmentation holographique échouée!")
                runner.log("✅ Holographic augmentation completed!")

            runner.log("✅ All augmentations completed successfully!")

        main.bridge.run(
            "Augmentation", work,
            on_success=lambda: main.notify_info("Succès", "Augmentation terminée!"),
            on_error=lambda msg: main.notify_error("Erreur", msg))

    def start_pipeline(self):
        main = self.main
        num_holo = self.pipe_holo.value()
        num_aug = self.pipe_aug.value()

        if num_holo == 0 and num_aug == 0:
            main.notify_warning("Attention", "Au moins une opération doit être > 0 !")
            return

        steps = []
        if num_holo > 0:
            steps.append(f"🌟 Holographic: {num_holo} variations")
        if num_aug > 0:
            steps.append(f"🎨 Augmentation: {num_aug} variations")
        if not main.confirm("Confirmation",
                            "Pipeline de génération:\n\n" + "\n".join(steps)
                            + "\n\nContinuer ?"):
            return

        main.log("🚀 Démarrage du pipeline de génération...")

        def work(runner):
            if num_holo > 0:
                runner.log(f"\n🌟 ÉTAPE 1/2: Holographic ({num_holo} variations)...")
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                     PATHS['directories']['images'],
                     PATHS['directories']['output_holographic'],
                     "--variations", str(num_holo)],
                    "Holographic génération échouée!")
                runner.log("✅ Holographic terminé!")

            if num_aug > 0:
                step = "2/2" if num_holo > 0 else "1/1"
                runner.log(f"\n🎨 ÉTAPE {step}: Augmentation ({num_aug}/image)...")
                runner.stream_or_fail(
                    [sys.executable, "-u", "core/augmentation_albumentations.py",
                     "--num_aug", str(num_aug),
                     "--source", "images", "--target", "augmented"],
                    "Augmentation échouée!")
                runner.log("✅ Augmentation terminée!")

            runner.log("\n🎉 PIPELINE TERMINÉ AVEC SUCCÈS!")

        main.bridge.run(
            "Generation Pipeline", work,
            on_success=lambda: main.notify_info(
                "Succès", "Pipeline terminé!\n📂 Output: output/augmented/"),
            on_error=lambda msg: main.notify_error("Erreur", msg))
