"""Fake images : random erasing sur cartes + génération de faux backgrounds."""
import os
import sys

from PySide6.QtWidgets import (
    QDoubleSpinBox, QPushButton, QSpinBox, QWidget,
)

from core.utils import PATHS
from gui_qt.widgets import Card, PathPicker, form_row, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "🎲 Fake Images")

        # --- Random erasing --------------------------------------------------
        erase_card = Card("🎲 Random Erasing (cartes partiellement masquées)")
        cfg = main.config
        self.input_dir = PathPicker(cfg.get("fakeimg_input_dir", PATHS['directories']['images']))
        self.output_dir = PathPicker(cfg.get("fakeimg_output_dir", "fakeimg"))

        def dspin(value, lo=0.0, hi=10.0, step=0.05):
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setDecimals(2)
            s.setValue(float(value))
            return s

        self.p = dspin(cfg.get("fakeimg_p", 0.5), 0.0, 1.0)
        self.sl = dspin(cfg.get("fakeimg_sl", 0.02), 0.0, 1.0, 0.01)
        self.sh = dspin(cfg.get("fakeimg_sh", 0.4), 0.0, 1.0, 0.01)
        self.r1 = dspin(cfg.get("fakeimg_r1", 0.3), 0.01, 10.0, 0.1)
        self.r2 = dspin(cfg.get("fakeimg_r2", 3.33), 0.01, 10.0, 0.1)

        erase_card.add_layout(form_row("Dossier source", self.input_dir))
        erase_card.add_layout(form_row("Dossier destination", self.output_dir))
        erase_card.add_layout(form_row("Probabilité (p)", self.p))
        erase_card.add_layout(form_row("Aire min (sl)", self.sl))
        erase_card.add_layout(form_row("Aire max (sh)", self.sh))
        erase_card.add_layout(form_row("Ratio min (r1)", self.r1))
        erase_card.add_layout(form_row("Ratio max (r2)", self.r2))

        erase_btn = QPushButton("🎲 Générer")
        erase_btn.setObjectName("primary")
        erase_btn.clicked.connect(self.start_erasing)
        erase_card.add(erase_btn)
        content.addWidget(erase_card)

        # --- Fake backgrounds -------------------------------------------------
        bg_card = Card("📋 Faux backgrounds (bruit) pour mosaïques")
        self.bg_count = QSpinBox(); self.bg_count.setRange(1, 5000); self.bg_count.setValue(50)
        self.bg_output = PathPicker(PATHS['directories']['output_backgrounds'])
        self.bg_min_noise = QSpinBox(); self.bg_min_noise.setRange(0, 255); self.bg_min_noise.setValue(10)
        self.bg_max_noise = QSpinBox(); self.bg_max_noise.setRange(0, 255); self.bg_max_noise.setValue(50)

        bg_card.add_layout(form_row("Nombre d'images", self.bg_count))
        bg_card.add_layout(form_row("Destination", self.bg_output))
        bg_card.add_layout(form_row("Bruit min", self.bg_min_noise))
        bg_card.add_layout(form_row("Bruit max", self.bg_max_noise))

        bg_btn = QPushButton("📋 Générer les backgrounds")
        bg_btn.setObjectName("primary")
        bg_btn.clicked.connect(self.start_backgrounds)
        bg_card.add(bg_btn)
        content.addWidget(bg_card)

    # ------------------------------------------------------------ opérations

    def start_erasing(self):
        main = self.main
        input_dir = self.input_dir.text()
        output_dir = self.output_dir.text()
        p, sl, sh = self.p.value(), self.sl.value(), self.sh.value()
        r1, r2 = self.r1.value(), self.r2.value()

        if not os.path.exists(input_dir):
            main.notify_error("Erreur",
                              f"Dossier source '{input_dir}' introuvable!\n"
                              "Téléchargez d'abord des cartes (vue Download).")
            return
        if sl >= sh:
            main.notify_error("Erreur", "Aire min (sl) doit être < aire max (sh)!")
            return
        if r1 >= r2:
            main.notify_error("Erreur", "Ratio min (r1) doit être < ratio max (r2)!")
            return

        main.log(f"🎲 Random erasing: {input_dir} → {output_dir}")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "core/random_erasing.py",
                 "--input_dir", input_dir, "--output_dir", output_dir,
                 "--p", str(p), "--sl", str(sl), "--sh", str(sh),
                 "--r1", str(r1), "--r2", str(r2)],
                "Génération échouée!")

        def on_success():
            count = 0
            if os.path.exists(output_dir):
                count = len([f for f in os.listdir(output_dir)
                             if f.endswith(('.png', '.jpg', '.jpeg'))])
            main.notify_info("Succès", f"{count} fake images générées dans {output_dir}/")

        main.bridge.run("Fake Image Generation", work,
                        on_success=on_success,
                        on_error=lambda msg: main.notify_error("Erreur", msg))

    def start_backgrounds(self):
        main = self.main
        count = self.bg_count.value()
        output = self.bg_output.text()
        min_noise, max_noise = self.bg_min_noise.value(), self.bg_max_noise.value()
        main.log(f"📋 Génération de {count} faux backgrounds...")

        def work(runner):
            runner.stream_or_fail(
                [sys.executable, "-u", "tools/generate_fake_backgrounds.py",
                 "--count", str(count), "--output", output,
                 "--min-noise", str(min_noise), "--max-noise", str(max_noise)],
                "Génération échouée!")
            runner.log(f"✅ {count} backgrounds générés dans {output}/")

        main.bridge.run("Fake Background Generation", work,
                        on_success=lambda: main.notify_info(
                            "Succès", f"{count} backgrounds générés!"),
                        on_error=lambda msg: main.notify_error("Erreur", msg))
