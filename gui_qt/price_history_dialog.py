"""
Fenêtre « 💹 Price History » (F09) — version Qt.

Historique d'évolution du prix d'une carte (sparkline QPainter) depuis la
table append-only du cache F10 (`models/price_cache.db`), plus gestion des
alertes de seuil. Réutilise `core.price_cache` (logique métier partagée avec
la version Tkinter `gui/price_history_view.py`).
"""
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDoubleSpinBox, QHBoxLayout, QLabel, QListWidget,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from core.price_cache import PriceCache, load_prices_with_cache

SPARK_W, SPARK_H, SPARK_PAD = 560, 160, 14


def sparkline_points(values, width=SPARK_W, height=SPARK_H, pad=SPARK_PAD):
    """
    Série de prix (chronologique) → points (x, y) pour un tracé (y inversé).
    Pur — testable sans Qt. Série vide → [] ; série plate → ligne médiane.
    """
    values = [v for v in values if v is not None]
    if not values:
        return []
    lo, hi = min(values), max(values)
    span_x = max(1, len(values) - 1)
    inner_w, inner_h = width - 2 * pad, height - 2 * pad
    points = []
    for i, v in enumerate(values):
        x = pad + i * inner_w / span_x
        y = height / 2.0 if hi == lo else pad + (hi - v) * inner_h / (hi - lo)
        points.append((x, y))
    return points


def format_history_label(entries) -> str:
    """Synthèse d'un historique (PriceEntry, du plus récent au plus ancien)."""
    priced = [e for e in entries if e.price is not None]
    if not priced:
        return "Aucun relevé de prix"
    current = priced[0]
    prices = [e.price for e in priced]
    label = (f"{current.price:.2f}€ actuellement — min {min(prices):.2f}€ / "
             f"max {max(prices):.2f}€ sur {len(priced)} relevés")
    if len(priced) > 1:
        first = priced[-1]
        delta = current.price - first.price
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "＝")
        label += f" ({arrow} {delta:+.2f}€ depuis le {first.date_str})"
    return label


class Sparkline(QWidget):
    """Petit tracé d'évolution dessiné au QPainter."""

    def __init__(self, accent="#89b4fa", parent=None):
        super().__init__(parent)
        self.setFixedSize(SPARK_W, SPARK_H)
        self._values = []
        self._accent = QColor(accent)

    def set_values(self, values):
        self._values = [v for v in values if v is not None]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#313244"))
        points = sparkline_points(self._values, self.width(), self.height())
        if len(points) >= 2:
            painter.setPen(QPen(self._accent, 2))
            qpts = [QPointF(x, y) for x, y in points]
            for a, b in zip(qpts, qpts[1:]):
                painter.drawLine(a, b)
        if points:
            x, y = points[-1]
            painter.setBrush(QColor("#a6e3a1"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), 4, 4)


class PriceHistoryDialog(QDialog):
    """Historique des prix + alertes de seuil (F09), version Qt."""

    def __init__(self, main, db_path=None):
        super().__init__(main)
        self.setWindowTitle("💹 Price History")
        self.resize(640, 560)
        self.cache = PriceCache(db_path)
        try:
            self._names = {cid: (info.get("name") or "")
                           for cid, info in load_prices_with_cache().items()}
        except Exception:
            self._names = {}

        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Carte :"))
        self.card_combo = QComboBox()
        self.card_combo.currentIndexChanged.connect(self._refresh_chart)
        top.addWidget(self.card_combo, 1)
        layout.addLayout(top)

        accent = getattr(main, "theme_name", "dark") and "#89b4fa"
        self.spark = Sparkline(accent=accent)
        layout.addWidget(self.spark, 0, Qt.AlignHCenter)

        self.summary = QLabel("")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        # --- Alertes ---
        layout.addWidget(QLabel("🔔 Alertes de seuil"))
        alert_row = QHBoxLayout()
        alert_row.addWidget(QLabel("Seuil (€):"))
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0.01, 100000.0)
        self.threshold.setValue(1.0)
        alert_row.addWidget(self.threshold)
        self.direction = QComboBox()
        self.direction.addItems(["above", "below"])
        alert_row.addWidget(self.direction)
        set_btn = QPushButton("➕ Ajouter")
        set_btn.clicked.connect(self._set_alert)
        remove_btn = QPushButton("➖ Retirer")
        remove_btn.clicked.connect(self._remove_alert)
        check_btn = QPushButton("🔔 Vérifier")
        check_btn.clicked.connect(self._check_alerts)
        for b in (set_btn, remove_btn, check_btn):
            alert_row.addWidget(b)
        alert_row.addStretch(1)
        layout.addLayout(alert_row)

        self.alerts_list = QListWidget()
        layout.addWidget(self.alerts_list, 1)

        self._reload_cards()
        self._refresh_alerts()

    # ---------- Données ----------

    def _selected_card_id(self):
        data = self.card_combo.currentData()
        return data

    def _reload_cards(self):
        self.card_combo.clear()
        cards = sorted(self.cache.latest_all().keys())
        for cid in cards:
            name = self._names.get(cid) or "?"
            self.card_combo.addItem(f"{cid} — {name}", cid)
        if not cards:
            self.summary.setText(
                "Cache vide — préchargez d'abord des prix "
                "(bouton ⬇ Précharger les prix de la vue Détection).")

    def _refresh_chart(self):
        cid = self._selected_card_id()
        if not cid:
            return
        entries = self.cache.history(cid, limit=100)
        self.summary.setText(format_history_label(entries))
        self.spark.set_values([e.price for e in reversed(entries)])

    # ---------- Alertes ----------

    def _refresh_alerts(self):
        self.alerts_list.clear()
        for alert in self.cache.list_alerts():
            state = "armée" if alert.armed else "déclenchée"
            name = self._names.get(alert.card_id) or ""
            self.alerts_list.addItem(f"{alert.describe()}  [{state}]  {name}")

    def _set_alert(self):
        cid = self._selected_card_id()
        if not cid:
            QMessageBox.warning(self, "Alerte", "Sélectionnez une carte")
            return
        try:
            self.cache.set_alert(cid, float(self.threshold.value()),
                                 self.direction.currentText())
        except ValueError as exc:
            QMessageBox.critical(self, "Alerte", f"Seuil invalide: {exc}")
            return
        self._refresh_alerts()

    def _remove_alert(self):
        cid = self._selected_card_id()
        if cid:
            self.cache.remove_alert(cid)
            self._refresh_alerts()

    def _check_alerts(self):
        triggered = self.cache.check_alerts()
        self._refresh_alerts()
        if triggered:
            for t in triggered:
                t.name = self._names.get(t.alert.card_id) or None
            QMessageBox.information(
                self, "🔔 Alertes déclenchées",
                "\n".join(f"• {t.describe()}" for t in triggered))
        else:
            QMessageBox.information(
                self, "Alertes",
                "Aucun seuil franchi sur les derniers relevés.")
