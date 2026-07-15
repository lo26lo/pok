"""Validation du dataset + fusion augmented/mosaics + rapport HTML."""
import sys
import webbrowser
from pathlib import Path

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget

from core.utils import PATHS
from gui_qt.widgets import Card, PathPicker, form_row, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "✅ Validation & Merge")

        # --- Merge ---------------------------------------------------------
        merge_card = Card("🔀 Fusionner le dataset (augmented + mosaics)")
        merge_btn = QPushButton("🔀 Merge Dataset")
        merge_btn.setObjectName("primary")
        merge_btn.clicked.connect(self.start_merge)
        merge_card.add(merge_btn)
        content.addWidget(merge_card)

        # --- Validation ------------------------------------------------------
        valid_card = Card("✅ Valider les annotations YOLO")
        self.dataset_path = PathPicker(PATHS['directories']['output_dataset'])
        self.html_report = QCheckBox("Générer le rapport HTML")
        self.html_report.setChecked(True)
        valid_card.add_layout(form_row("Dataset", self.dataset_path))
        valid_card.add(self.html_report)

        buttons = QHBoxLayout()
        validate_btn = QPushButton("✅ Valider")
        validate_btn.setObjectName("primary")
        validate_btn.clicked.connect(self.start_validation)
        report_btn = QPushButton("📄 Ouvrir le rapport")
        report_btn.clicked.connect(self.open_report)
        buttons.addWidget(validate_btn)
        buttons.addWidget(report_btn)
        buttons.addStretch(1)
        valid_card.add_layout(buttons)
        content.addWidget(valid_card)

    # ----------------------------------------------------------- opérations

    def start_merge(self):
        main = self.main
        main.log("🔀 Fusion du dataset (augmented + mosaics)...")

        def work(runner):
            scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            import merge_dataset

            import io
            from contextlib import redirect_stdout
            output = io.StringIO()
            with redirect_stdout(output):
                merge_dataset.merge_dataset()
            for line in output.getvalue().split('\n'):
                if line.strip():
                    runner.log(line)
            runner.log("✅ Dataset fusionné avec succès!")

        main.bridge.run(
            "Merge Dataset", work,
            on_success=lambda: main.notify_info(
                "Succès",
                f"Dataset fusionné!\n\n📂 {PATHS['directories']['output_dataset']}\n"
                "✓ train.txt / val.txt / data.yaml\n\nPrêt pour l'entraînement!"),
            on_error=lambda msg: main.notify_error("Erreur", f"Erreur lors du merge:\n{msg}"))

    def start_validation(self):
        main = self.main
        dataset = self.dataset_path.text()
        html = self.html_report.isChecked()

        if not Path(dataset).exists():
            main.notify_error("Erreur", f"Dataset non trouvé:\n{dataset}")
            return
        main.log(f"✅ Validation: {dataset}")

        def work(runner):
            cmd = [sys.executable, "-u", "core/dataset_validator.py", dataset]
            if html:
                cmd.append("--html")
            runner.stream_or_fail(cmd, "Validation échouée!")
            runner.log("✅ Validation terminée!")
            if html:
                runner.log("📄 Rapport: validation_report.html")

        main.bridge.run(
            "Validation", work,
            on_success=lambda: main.notify_info(
                "Succès", "Validation terminée!\nVoir validation_report.html"),
            on_error=lambda msg: main.notify_error("Erreur", msg))

    def open_report(self):
        report = Path("validation_report.html")
        if report.exists():
            webbrowser.open(str(report.absolute()))
        else:
            self.main.notify_warning("Attention",
                                     "Rapport non trouvé!\nValidez d'abord le dataset.")
