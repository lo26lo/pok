"""Génération de mosaïques annotées YOLO."""
import sys

from PySide6.QtWidgets import QComboBox, QPushButton, QWidget

from gui_qt.widgets import Card, form_row, view_scaffold

MODES = ["Quick (200)", "Standard (500)", "Complete (All combinations)"]
LAYOUTS = ["1 - Grid (Standard)", "2 - Grid with 3D Rotation", "3 - Random Placement"]
BACKGROUNDS = ["0 - Fake Cards Mosaic", "1 - Local Image (mosaic/)",
               "2 - Web Image (Lorem Picsum)"]
TRANSFORMS = ["0 - 2D Rotation", "1 - 3D Perspective Projection"]


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🧩 Mosaïques")

        card = Card("Configuration des mosaïques")
        self.mode = QComboBox(); self.mode.addItems(MODES); self.mode.setCurrentIndex(1)
        self.layout_mode = QComboBox(); self.layout_mode.addItems(LAYOUTS)
        self.background = QComboBox(); self.background.addItems(BACKGROUNDS)
        self.transform = QComboBox(); self.transform.addItems(TRANSFORMS)

        card.add_layout(form_row("Quantité", self.mode))
        card.add_layout(form_row("Layout", self.layout_mode))
        card.add_layout(form_row("Background", self.background))
        card.add_layout(form_row("Transformation", self.transform))

        start = QPushButton("🧩 Générer les mosaïques")
        start.setObjectName("primary")
        start.clicked.connect(self.start_mosaic)
        card.add(start)
        content.addWidget(card)

    def start_mosaic(self):
        main = self.main
        mode = self.mode.currentText()
        layout_val = int(self.layout_mode.currentText().split(' - ')[0])
        background_val = int(self.background.currentText().split(' - ')[0])
        transform_val = int(self.transform.currentText().split(' - ')[0])

        max_groups = None
        if "Quick" in mode:
            max_groups = 25       # 25 groupes × 8 cartes ≈ 200 mosaïques
        elif "Standard" in mode:
            max_groups = 62       # ≈ 500 mosaïques

        main.log(f"🧩 Génération mosaïques: {mode}")
        main.log(f"   Layout: {layout_val}, Background: {background_val}, "
                 f"Transform: {transform_val}")
        if max_groups:
            main.log(f"   Max groups: {max_groups}")

        def work(runner):
            cmd = [sys.executable, "-u", "core/mosaic_optimized.py",
                   str(layout_val), str(background_val), str(transform_val)]
            if max_groups:
                cmd.extend(["--max-groups", str(max_groups)])
            runner.stream_or_fail(cmd, "Génération échouée!")
            runner.log("✅ Mosaïques générées!")

        main.bridge.run(
            "Mosaic Generation", work,
            on_success=lambda: main.notify_info("Succès", "Mosaïques générées avec succès!"),
            on_error=lambda msg: main.notify_error("Erreur", msg))
