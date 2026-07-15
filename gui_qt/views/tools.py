"""Outils : auto-balancing, effets holographiques, dossiers du projet."""
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout, QPushButton, QSpinBox, QWidget,
)

from core.utils import PATHS
from gui_qt.widgets import Card, form_row, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🛠️ Tools")

        # --- Auto-balancing -------------------------------------------------
        balance_card = Card("⚖️ Auto-balancing des classes")
        self.balance_target = QSpinBox()
        self.balance_target.setRange(1, 10000)
        self.balance_target.setValue(50)
        balance_card.add_layout(form_row("Instances cibles / classe", self.balance_target))
        balance_btn = QPushButton("⚖️ Équilibrer le dataset")
        balance_btn.setObjectName("primary")
        balance_btn.clicked.connect(self.start_balancing)
        balance_card.add(balance_btn)
        content.addWidget(balance_card)

        # --- Holographic -----------------------------------------------------
        holo_card = Card("✨ Effets holographiques (images/ → images_holographic/)")
        self.holo_variations = QSpinBox()
        self.holo_variations.setRange(1, 20)
        self.holo_variations.setValue(int(main.config.get("holographic_variations", 3)))
        holo_card.add_layout(form_row("Variations par carte", self.holo_variations))
        holo_btn = QPushButton("✨ Appliquer l'effet")
        holo_btn.setObjectName("primary")
        holo_btn.clicked.connect(self.start_holographic)
        holo_card.add(holo_btn)
        content.addWidget(holo_card)

        # --- Dossiers ---------------------------------------------------------
        folders_card = Card("📂 Ouvrir un dossier du projet")
        row = QHBoxLayout()
        for label, key in [("Images", 'images'),
                           ("Augmented", 'output_augmented'),
                           ("Mosaïques", 'output_mosaics'),
                           ("Dataset", 'output_dataset')]:
            btn = QPushButton(f"📂 {label}")
            btn.clicked.connect(
                lambda _=False, k=key: self.open_folder(PATHS['directories'][k]))
            row.addWidget(btn)
        row.addStretch(1)
        folders_card.add_layout(row)
        content.addWidget(folders_card)

    # ------------------------------------------------------------ opérations

    def start_balancing(self):
        main = self.main
        target = self.balance_target.value()
        main.log(f"⚖️ Auto-balancing des classes (target={target})...")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "core/auto_balancer_optimized.py",
                 PATHS['directories']['output_dataset'],
                 "--strategy", "augment", "--target", str(target)],
                "Balancing échoué!")
            runner.log("✅ Balancing terminé!")

        main.bridge.run(
            "Balancing", work,
            on_success=lambda: main.notify_info("Succès", "Classes équilibrées!"),
            on_error=lambda msg: main.notify_error("Erreur", msg))

    def start_holographic(self):
        main = self.main
        variations = self.holo_variations.value()
        main.log(f"✨ Holographic augmentation: variations={variations}")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "core/holographic_augmenter_optimized.py",
                 "images", "images_holographic", "--variations", str(variations)],
                "Augmentation holographique échouée!")
            runner.log("✅ Holographic augmentation terminée!")

        main.bridge.run(
            "Holographic Augmentation", work,
            on_success=lambda: main.notify_info("Succès", "Effets holographiques appliqués!"),
            on_error=lambda msg: main.notify_error("Erreur", msg))

    def open_folder(self, folder: str):
        path = Path(folder)
        if not path.exists():
            self.main.notify_warning("Attention", f"Dossier {folder}/ introuvable!")
            return
        if sys.platform.startswith("win"):
            os_cmd = ["explorer", str(path)]
        elif sys.platform == "darwin":
            os_cmd = ["open", str(path)]
        else:
            os_cmd = ["xdg-open", str(path)]
        subprocess.Popen(os_cmd)
