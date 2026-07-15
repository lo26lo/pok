"""Export du dataset vers d'autres formats (COCO, VOC, TFRecord, Roboflow)."""
import sys

from PySide6.QtWidgets import QCheckBox, QPushButton, QWidget

from core.utils import PATHS
from gui_qt.widgets import Card, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "📦 Export multi-format")

        card = Card("Formats à exporter")
        self.formats = {
            "coco": QCheckBox("COCO JSON"),
            "voc": QCheckBox("Pascal VOC"),
            "tfrecord": QCheckBox("TFRecord"),
            "roboflow": QCheckBox("Roboflow ZIP"),
        }
        self.formats["coco"].setChecked(True)
        for cb in self.formats.values():
            card.add(cb)

        start = QPushButton("📦 Exporter")
        start.setObjectName("primary")
        start.clicked.connect(self.start_export)
        card.add(start)
        content.addWidget(card)

    def start_export(self):
        main = self.main
        selected = [name for name, cb in self.formats.items() if cb.isChecked()]
        if not selected:
            main.notify_warning("Attention", "Sélectionnez au moins un format!")
            return
        main.log(f"📦 Export: {', '.join(selected)}")

        def work(runner):
            for fmt in selected:
                runner.log(f"\n📦 Export format: {fmt}")
                returncode = runner.stream(
                    [sys.executable, "-u", "core/dataset_exporter.py",
                     PATHS['directories']['output_dataset'], "--format", fmt])
                if returncode != 0:
                    runner.log(f"❌ Export {fmt} échoué")
            runner.log("\n✅ Export terminé!")

        main.bridge.run(
            "Export", work,
            on_success=lambda: main.notify_info(
                "Succès", f"Export terminé!\n\nFormats: {', '.join(selected)}"),
            on_error=lambda msg: main.notify_error("Erreur", msg))
