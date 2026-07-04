"""Petits widgets réutilisables du GUI Qt (cartes, sélecteurs de chemin…)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QWidget, QScrollArea,
)


class Card(QFrame):
    """Panneau à fond carte avec titre, équivalent des 'cards' Tkinter."""

    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 14)
        self._layout.setSpacing(8)
        if title:
            label = QLabel(title)
            label.setObjectName("cardTitle")
            self._layout.addWidget(label)

    @property
    def body(self) -> QVBoxLayout:
        return self._layout

    def add(self, widget: QWidget) -> QWidget:
        self._layout.addWidget(widget)
        return widget

    def add_layout(self, layout) -> None:
        self._layout.addLayout(layout)


class PathPicker(QWidget):
    """Champ chemin + bouton Parcourir (dossier ou fichier)."""

    def __init__(self, initial: str = "", directory: bool = True,
                 file_filter: str = "", parent=None):
        super().__init__(parent)
        self._directory = directory
        self._filter = file_filter
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self.edit = QLineEdit(initial)
        browse = QPushButton("📂")
        browse.setFixedWidth(44)
        browse.clicked.connect(self._browse)
        row.addWidget(self.edit, 1)
        row.addWidget(browse)

    def _browse(self):
        if self._directory:
            path = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier",
                                                    self.edit.text() or ".")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier",
                                                  self.edit.text() or ".", self._filter)
        if path:
            self.edit.setText(path)

    def text(self) -> str:
        return self.edit.text().strip()

    def set_text(self, value: str) -> None:
        self.edit.setText(value)


def form_row(label: str, widget: QWidget, label_width: int = 170) -> QHBoxLayout:
    """Ligne de formulaire 'Label : widget' alignée."""
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setFixedWidth(label_width)
    row.addWidget(lbl)
    row.addWidget(widget, 1)
    return row


def view_scaffold(view: QWidget, title: str) -> QVBoxLayout:
    """
    Installe le squelette standard d'une vue (titre + zone scrollable)
    directement sur `view`.

    Returns:
        Le layout de contenu — y ajouter les Cards.
    """
    outer = QVBoxLayout(view)
    outer.setContentsMargins(20, 16, 20, 16)
    outer.setSpacing(10)

    title_label = QLabel(title)
    title_label.setObjectName("viewTitle")
    outer.addWidget(title_label)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    inner = QWidget()
    content = QVBoxLayout(inner)
    content.setContentsMargins(0, 4, 8, 4)
    content.setSpacing(14)
    content.setAlignment(Qt.AlignTop)
    scroll.setWidget(inner)
    outer.addWidget(scroll, 1)

    return content
