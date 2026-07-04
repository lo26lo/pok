"""
Fenêtre principale du GUI Qt.

Structure: sidebar de navigation (11 vues) + QStackedWidget + dock de logs
+ barre de statut (opération en cours, progression, bouton Stop).
"""
from datetime import datetime

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QApplication, QDockWidget, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QStackedWidget, QToolBar, QWidget,
)

from gui.config import GuiConfig
from gui_qt.bridge import QtTaskBridge
from gui_qt.theme import THEMES, build_qss

import logging
gui_logger = logging.getLogger("gui_qt")

VIEWS = [
    ("home",         "🏠  Dashboard"),
    ("download",     "⬇️  Download"),
    ("augmentation", "🎨  Augmentation"),
    ("mosaic",       "🧩  Mosaïques"),
    ("validation",   "✅  Validation & Merge"),
    ("export",       "📦  Export"),
    ("training",     "🎓  Training"),
    ("detection",    "🔍  Détection"),
    ("fakeimg",      "🎲  Fake Images"),
    ("tools",        "🛠️  Tools"),
    ("settings",     "⚙️  Settings"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pokémon Dataset Generator — Qt")
        self.resize(1400, 900)

        self.config = GuiConfig()
        self.bridge = QtTaskBridge(self)

        self._build_topbar()
        self._build_body()
        self._build_log_dock()
        self._build_statusbar()

        # Câblage du bridge
        self.bridge.logged.connect(self._append_log)
        self.bridge.started.connect(self._on_task_started)
        self.bridge.finished.connect(self._on_task_finished)

        # Thème persistant (défaut: sombre, comme le GUI historique)
        self.apply_theme(self.config.get("ui_theme", "dark"))

        self.log("✅ Interface Qt initialisée")

    # ------------------------------------------------------------- structure

    def _build_topbar(self):
        bar = QToolBar()
        bar.setMovable(False)
        bar.setIconSize(QSize(18, 18))
        self.addToolBar(bar)

        title = QLabel("  🎴 Pokémon Dataset Generator")
        title.setObjectName("cardTitle")
        bar.addWidget(title)

        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding,
                             spacer.sizePolicy().verticalPolicy().Preferred)
        bar.addWidget(spacer)

        self.theme_button = QPushButton("☀️ Thème clair")
        self.theme_button.clicked.connect(self.toggle_theme)
        bar.addWidget(self.theme_button)

    def _build_body(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(210)
        for view_id, label in VIEWS:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, view_id)
            self.sidebar.addItem(item)

        self.stack = QStackedWidget()
        self.views = {}
        self._create_views()

        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(container)

    def _create_views(self):
        # Imports locaux: chaque vue est un module indépendant
        from gui_qt.views import (home, download, augmentation, mosaic,
                                  validation, export, training, detection,
                                  fakeimg, tools, settings)
        modules = {
            "home": home, "download": download, "augmentation": augmentation,
            "mosaic": mosaic, "validation": validation, "export": export,
            "training": training, "detection": detection, "fakeimg": fakeimg,
            "tools": tools, "settings": settings,
        }
        for view_id, _ in VIEWS:
            view = modules[view_id].View(self)
            self.views[view_id] = view
            self.stack.addWidget(view)

    def _build_log_dock(self):
        self.log_panel = QPlainTextEdit()
        self.log_panel.setObjectName("logPanel")
        self.log_panel.setReadOnly(True)
        self.log_panel.setMaximumBlockCount(5000)

        dock = QDockWidget("📋 Logs", self)
        dock.setWidget(self.log_panel)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        dock.setMinimumHeight(140)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.log_dock = dock

    def _build_statusbar(self):
        self.status_label = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)      # indéterminé
        self.progress.setFixedWidth(160)
        self.progress.hide()
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setObjectName("danger")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.bridge.stop)

        sb = self.statusBar()
        sb.addWidget(self.status_label, 1)
        sb.addPermanentWidget(self.progress)
        sb.addPermanentWidget(self.stop_button)

    # ----------------------------------------------------------------- thème

    def apply_theme(self, name: str):
        self._theme = name if name in THEMES else "dark"
        QApplication.instance().setStyleSheet(build_qss(THEMES[self._theme]))
        self.theme_button.setText(
            "☀️ Thème clair" if self._theme == "dark" else "🌙 Thème sombre")
        self.config.set("ui_theme", self._theme)
        self.config.save()

    def toggle_theme(self):
        self.apply_theme("light" if self._theme == "dark" else "dark")

    @property
    def theme_name(self) -> str:
        return self._theme

    # ------------------------------------------------------------------ logs

    def log(self, message: str):
        """Thread-safe: passe par le signal du bridge."""
        self.bridge.log(message)

    def _append_log(self, message: str):
        gui_logger.info(message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_panel.appendPlainText(f"[{timestamp}] {message}")

    # ------------------------------------------------------- état d'opération

    def _on_task_started(self, name: str):
        self.status_label.setText(f"Running: {name}")
        self.progress.show()
        self.stop_button.setEnabled(True)

    def _on_task_finished(self):
        self.status_label.setText("Ready")
        self.progress.hide()
        self.stop_button.setEnabled(False)
        # Rafraîchir le dashboard après chaque opération
        home = self.views.get("home")
        if home is not None:
            home.refresh_stats()

    # ------------------------------------------------------------ messageries

    def notify_info(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def notify_warning(self, title: str, message: str):
        QMessageBox.warning(self, title, message)

    def notify_error(self, title: str, message: str):
        QMessageBox.critical(self, title, message)

    def confirm(self, title: str, message: str) -> bool:
        return QMessageBox.question(self, title, message) == QMessageBox.Yes

    def goto(self, view_id: str):
        for i in range(self.sidebar.count()):
            if self.sidebar.item(i).data(Qt.UserRole) == view_id:
                self.sidebar.setCurrentRow(i)
                return
