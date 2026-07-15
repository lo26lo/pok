"""Détection YOLO : webcam temps réel, image unique, dossier (DetectionManager).

Inclut les fonctionnalités des vagues 3 & 4 (parité avec le GUI Tkinter) :
identification fine F01, grading F02, scan de collection F03, et le cache de
prix hors-ligne F10 (préchargement + indicateur de snapshot). L'historique et
les alertes de prix F09 sont dans la fenêtre « 💹 Price History ».
"""
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSlider,
    QSpinBox, QWidget,
)

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
        self.show_prices = QCheckBox("💰 Afficher les prix (base cards_database.yaml + cache)")
        self.show_prices.setChecked(True)
        # Vagues 3 & 4
        self.identify_cards = QCheckBox(
            "🎴 Identifier les cartes (index d'embeddings — set + numéro exact)")
        self.grade_cards = QCheckBox(
            "🔍 Estimer l'état (centrage/coins → badge NM/EX/GD/PL, prix pondéré)")

        card.add_layout(form_row("Modèle (.pt)", self.model_path))
        conf_container = QWidget(); conf_container.setLayout(conf_row)
        card.add_layout(form_row("Confiance min", conf_container))
        card.add_layout(form_row("Caméra (ID)", self.camera_id))
        card.add(self.show_prices)
        card.add(self.identify_cards)
        card.add(self.grade_cards)
        content.addWidget(card)

        # --- Prix hors-ligne (F10) ------------------------------------------
        price_card = Card("💾 Prix hors-ligne")
        self.snapshot_label = QLabel(self._snapshot_text())
        self.snapshot_label.setObjectName("dim")
        preload_row = QHBoxLayout()
        preload_btn = QPushButton("⬇ Précharger les prix")
        preload_btn.clicked.connect(self.preload_prices)
        history_btn = QPushButton("💹 Historique && alertes")
        history_btn.clicked.connect(self.open_price_history)
        preload_row.addWidget(preload_btn)
        preload_row.addWidget(history_btn)
        preload_row.addStretch(1)
        price_card.add(self.snapshot_label)
        price_card.add_layout(preload_row)
        content.addWidget(price_card)

        # --- Actions --------------------------------------------------------
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

        scan_row = QHBoxLayout()
        scan_btn = QPushButton("🧺 Scan de collection")
        scan_btn.setObjectName("primary")
        scan_btn.clicked.connect(self.start_collection_scan)
        open_scans_btn = QPushButton("📂 Dossier des scans")
        open_scans_btn.clicked.connect(self.open_scans_folder)
        scan_row.addWidget(scan_btn)
        scan_row.addWidget(open_scans_btn)
        scan_row.addStretch(1)
        actions.add_layout(scan_row)

        hint = QLabel("La fenêtre de détection s'ouvre via OpenCV — touche 'q' pour quitter.")
        hint.setObjectName("dim")
        actions.add(hint)
        content.addWidget(actions)

    # ------------------------------------------------------------------ util

    @staticmethod
    def _snapshot_text() -> str:
        try:
            from core.price_cache import snapshot_status
            status = snapshot_status()
        except Exception:
            status = None
        return f"💾 {status}" if status else "💾 Aucun snapshot de prix hors-ligne"

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
            identify_cards=self.identify_cards.isChecked(),
            grade_cards=self.grade_cards.isChecked(),
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

    # ------------------------------------------------- scan de collection F03

    def start_collection_scan(self):
        config = self._make_config()
        if config is None:
            return
        # L'identification exacte est fortement recommandée pour le scan
        config.identify_cards = True
        self._config = config
        main = self.main
        main.log("🧺 Démarrage du scan de collection… "
                 "(présentez vos cartes, 'q' pour terminer)")

        def work(runner):
            from core.detection_manager import DetectionManager
            from core.collection_scanner import CollectionScanner
            manager = DetectionManager(self._config)
            manager.set_log_callback(runner.log)
            scanner = CollectionScanner()
            try:
                manager.detect_webcam(scanner=scanner)
            except Exception as exc:
                raise TaskError(f"Scan échoué: {exc}")

            s = scanner.summary()
            csv_path = scanner.export_csv()
            xlsx_path = scanner.export_excel()
            runner.log(f"🧺 Scan terminé: {s['unique_cards']} cartes uniques, "
                       f"{s['total_quantity']} exemplaires, "
                       f"valeur {s['total_value']:.2f}-{s['total_value_max']:.2f}€")
            runner.log(f"   💾 Inventaire: {csv_path}")
            if xlsx_path:
                runner.log(f"   💾 Excel: {xlsx_path}")
            self._last_scan_summary = (s, csv_path, xlsx_path)

        def on_success():
            s, csv_path, xlsx_path = getattr(
                self, "_last_scan_summary", (None, None, None))
            if not s:
                return
            unpriced = (f"\nCartes sans prix: {s['unpriced_cards']}"
                        if s['unpriced_cards'] else "")
            exports = f"CSV: {csv_path}" + (f"\nExcel: {xlsx_path}"
                                            if xlsx_path else "")
            main.notify_info(
                "Scan de collection terminé",
                f"🧺 {s['unique_cards']} cartes uniques "
                f"({s['total_quantity']} exemplaires)\n"
                f"💰 Valeur estimée: {s['total_value']:.2f}€ "
                f"à {s['total_value_max']:.2f}€\n"
                f"⏱️ Durée: {s['duration_s']:.0f}s{unpriced}\n\n{exports}")

        main.bridge.run("Collection Scan", work,
                        on_success=on_success,
                        on_error=lambda msg: main.notify_error("Erreur", msg))

    def open_scans_folder(self):
        folder = Path(PATHS['directories'].get(
            "output_collection_scans", "output/collection_scans"))
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder.resolve())))

    # ---------------------------------------------------------- prix F10 / F09

    def preload_prices(self):
        main = self.main
        main.log("⬇️ Préchargement des prix (cartes de la base locale)…")

        def work(runner):
            from core.price_cache import database_card_ids, preload_prices
            card_ids = database_card_ids()
            if not card_ids:
                raise TaskError("models/cards_database.yaml vide — rien à précharger")
            self._preload_result = preload_prices(
                card_ids=card_ids,
                progress_callback=lambda msg, cur, tot: runner.log(msg))

        def on_success():
            self.snapshot_label.setText(self._snapshot_text())
            result = getattr(self, "_preload_result", {})
            alerts = result.get("alerts", [])
            for t in alerts:
                main.log(f"🔔 ALERTE PRIX: {t.describe()}")
            if alerts:
                main.notify_info("🔔 Alertes de prix",
                                 "\n".join(f"• {t.describe()}" for t in alerts))
            else:
                main.notify_info("Préchargement terminé",
                                 f"{result.get('priced', 0)} cartes avec prix.")

        main.bridge.run("Preload Prices", work,
                        on_success=on_success,
                        on_error=lambda msg: main.notify_error("Erreur", msg))

    def open_price_history(self):
        try:
            from gui_qt.price_history_dialog import PriceHistoryDialog
        except Exception as exc:
            self.main.notify_error("Erreur",
                                   f"Impossible d'ouvrir l'historique:\n{exc}")
            return
        dialog = PriceHistoryDialog(self.main)
        dialog.exec()
