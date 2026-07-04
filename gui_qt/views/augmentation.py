"""Augmentation d'images (Albumentations) + pipeline holographic."""
import sys

from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QWidget,
)

from core.utils import PATHS
from gui.task_runner import TaskError
from gui_qt.widgets import Card, form_row, view_scaffold


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

    def start_augmentation(self):
        main = self.main
        num_aug = self.num_aug.value()
        aug_type = self.aug_type.currentText()
        target = self.target.text().strip() or "augmented"
        holo_variations = int(main.config.get("holographic_variations", 3))

        main.log(f"🎨 Augmentation ({aug_type}): {num_aug} variations → {target}/")

        def work(runner):
            if aug_type in ("Standard", "Both"):
                runner.log("🎨 Running standard augmentation (Albumentations)...")
                returncode = runner.stream(
                    [sys.executable, "-u", "core/augmentation_albumentations.py",
                     "--num_aug", str(num_aug), "--target", target])
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
