"""
Settings — configuration persistée dans gui_config.json via GuiConfig.

Construction déclarative: SPEC décrit chaque onglet et ses champs
(clé de config, label, type, défaut). Mêmes clés que le SettingsDialog
Tkinter → les deux interfaces partagent le même fichier de config.
"""
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDoubleSpinBox, QLineEdit, QPushButton,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from core.utils import PATHS
from gui.config import GuiConfig
from gui_qt.widgets import Card, form_row, view_scaffold

D = PATHS['directories']

# (clé, label, type, défaut) — types: str, int, float, bool, ou liste de choix
SPEC = {
    "📁 Chemins": [
        ("default_images_dir", "Images source", str, D['images']),
        ("default_output_dir", "Output", str, D['output_base']),
        ("default_augmented_dir", "Augmented", str, D['output_augmented']),
        ("default_mosaic_dir", "Mosaïques", str, D['output_mosaics']),
        ("default_dataset_dir", "Dataset", str, D['output_dataset']),
        ("default_fakeimg_dir", "Fake images", str, D['output_backgrounds']),
        ("default_holographic_dir", "Holographic", str, D['output_holographic']),
    ],
    "🎨 Génération": [
        ("default_augmentations", "Augmentations / image", int, 50),
        ("holographic_intensity", "Intensité holographic", float, 0.7),
        ("holographic_variations", "Variations holographic", int, 3),
        ("default_mosaic_mode", "Mode mosaïque", ["standard", "quick", "complete"], "standard"),
        ("default_mosaic_layout", "Layout mosaïque", int, 1),
        ("default_mosaic_background", "Background mosaïque", int, 0),
        ("default_mosaic_transform", "Transform mosaïque", int, 0),
    ],
    "🎓 Training": [
        ("default_model", "Modèle", ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt"], "yolov8n.pt"),
        ("default_epochs", "Epochs", int, 50),
        ("default_batch", "Batch size", int, 16),
        ("default_device", "Device", str, "0"),
    ],
    "⬇️ Download": [
        ("default_download_dir", "Destination", str, "images"),
        ("default_download_lang", "Langue", str, "English"),
        ("default_download_quality", "Qualité", ["high", "low"], "high"),
        ("default_download_format", "Format", ["png", "jpg", "jpeg", "webp"], "png"),
        ("default_download_workers", "Téléchargements parallèles", int, 8),
    ],
    "🎲 Fake Images": [
        ("fakeimg_input_dir", "Dossier source", str, D['images']),
        ("fakeimg_output_dir", "Dossier destination", str, "fakeimg"),
        ("fakeimg_p", "Probabilité (p)", float, 0.5),
        ("fakeimg_sl", "Aire min (sl)", float, 0.02),
        ("fakeimg_sh", "Aire max (sh)", float, 0.4),
        ("fakeimg_r1", "Ratio min (r1)", float, 0.3),
        ("fakeimg_r2", "Ratio max (r2)", float, 3.33),
    ],
    "🌐 API": [
        ("tcgdex_api_key", "Clé API TCGdex (optionnel)", str, ""),
        ("auto_save_logs", "Sauvegarde auto des logs", bool, False),
        ("enable_notifications", "Notifications", bool, True),
    ],
    "🐛 Debug": [
        ("debug_device", "Device", ["auto", "cpu", "gpu", "0", "1"], "auto"),
        ("debug_workers", "Workers", int, 4),
        ("debug_log_level", "Niveau de log", ["ERROR", "WARNING", "INFO", "DEBUG", "TRACE"], "INFO"),
        ("debug_cache_mode", "Cache", ["ram", "disk", "disabled"], "ram"),
        ("debug_profiling", "Profiling", bool, False),
        ("debug_benchmark", "Benchmark", bool, False),
        ("debug_save_logs", "Sauvegarder les logs", bool, False),
        ("debug_multiprocessing", "Multiprocessing debug", bool, False),
        ("debug_memory_profiling", "Profiling mémoire", bool, False),
    ],
}


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "⚙️ Settings")

        self._widgets = {}
        tabs = QTabWidget()
        cfg = GuiConfig()

        for tab_name, fields in SPEC.items():
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setSpacing(8)
            for key, label, kind, default in fields:
                value = cfg.get(key, default)
                widget = self._make_widget(kind, value, default)
                self._widgets[key] = (widget, kind)
                if isinstance(widget, QCheckBox):
                    widget.setText(label)
                    layout.addWidget(widget)
                else:
                    layout.addLayout(form_row(label, widget, label_width=200))
            layout.addStretch(1)
            tabs.addTab(page, tab_name)

        card = Card("")
        card.add(tabs)
        save_btn = QPushButton("💾 Sauvegarder les paramètres")
        save_btn.setObjectName("primary")
        save_btn.clicked.connect(self.save)
        card.add(save_btn)
        content.addWidget(card)

    # ------------------------------------------------------------------ util

    @staticmethod
    def _make_widget(kind, value, default):
        if isinstance(kind, list):                       # liste de choix
            combo = QComboBox()
            combo.addItems([str(item) for item in kind])
            combo.setCurrentText(str(value if value is not None else default))
            return combo
        if kind is bool:
            box = QCheckBox()
            box.setChecked(bool(value))
            return box
        if kind is int:
            spin = QSpinBox()
            spin.setRange(-1, 100000)
            spin.setValue(int(value if value is not None else default))
            return spin
        if kind is float:
            spin = QDoubleSpinBox()
            spin.setRange(0.0, 100000.0)
            spin.setDecimals(3)
            spin.setValue(float(value if value is not None else default))
            return spin
        return QLineEdit(str(value if value is not None else default))

    @staticmethod
    def _read_widget(widget, kind):
        if isinstance(kind, list):
            return widget.currentText()
        if kind is bool:
            return widget.isChecked()
        if kind in (int, float):
            return widget.value()
        return widget.text()

    # ------------------------------------------------------------------ save

    def save(self):
        values = {key: self._read_widget(widget, kind)
                  for key, (widget, kind) in self._widgets.items()}
        cfg = GuiConfig()
        cfg.update(values)   # préserve paths/last_used/ui_theme, etc.
        if cfg.save():
            self.main.config.load()   # recharger la config partagée
            self.main.log("💾 Paramètres sauvegardés (gui_config.json)")
            self.main.notify_info("Succès", "✅ Paramètres sauvegardés!")
        else:
            self.main.notify_error("Erreur", "Écriture de gui_config.json impossible")
