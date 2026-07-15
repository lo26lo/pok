"""Téléchargement des images de cartes depuis l'API TCGdex."""
from PySide6.QtWidgets import (
    QComboBox, QLineEdit, QPushButton, QWidget,
)

from core.utils import get_message
from gui.task_runner import TaskError
from gui_qt.widgets import Card, PathPicker, form_row, view_scaffold


class View(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        content = view_scaffold(self, "⬇️ Download — cartes TCGdex")

        card = Card("Configuration du téléchargement")
        cfg = main.config

        self.set_query = QLineEdit()
        self.set_query.setPlaceholderText("ID ou nom du set (ex: xyp, sv08, Surging Sparks)")

        from core.image_downloader import LANGUAGES
        self.language = QComboBox()
        self.language.addItems(list(LANGUAGES.keys()))

        self.quality = QComboBox()
        self.quality.addItems(["high", "low"])
        self.quality.setCurrentText(cfg.get("default_download_quality", "high"))

        self.img_format = QComboBox()
        self.img_format.addItems(["png", "jpg", "jpeg", "webp"])
        self.img_format.setCurrentText(cfg.get("default_download_format", "png"))

        self.output_dir = PathPicker(cfg.get("default_download_dir", "images"))

        card.add_layout(form_row("Set Pokémon", self.set_query))
        card.add_layout(form_row("Langue", self.language))
        card.add_layout(form_row("Qualité", self.quality))
        card.add_layout(form_row("Format", self.img_format))
        card.add_layout(form_row("Destination", self.output_dir))

        start = QPushButton("⬇️ Télécharger le set")
        start.setObjectName("primary")
        start.clicked.connect(self.start_download)
        card.add(start)
        content.addWidget(card)

        from PySide6.QtWidgets import QLabel
        note = Card("ℹ️ Après le téléchargement")
        note_label = QLabel("cards_database.yaml est régénéré automatiquement "
                            "depuis le manifest du set téléchargé.")
        note_label.setObjectName("dim")
        note.add(note_label)
        content.addWidget(note)

    # ------------------------------------------------------------- opération

    def start_download(self):
        main = self.main
        set_value = self.set_query.text().strip()
        if not set_value:
            main.notify_error("Erreur", "Saisissez un set Pokémon (id ou nom)!")
            return
        # Format "Nom (id)" accepté
        if '(' in set_value and ')' in set_value:
            set_query = set_value.split('(')[-1].strip(')')
        else:
            set_query = set_value

        from core.image_downloader import LANGUAGES
        lang_name = self.language.currentText()
        lang_code = LANGUAGES.get(lang_name, 'en')
        quality = self.quality.currentText()
        ext = self.img_format.currentText()
        output_dir = self.output_dir.text() or "images"

        if not main.confirm("⬇️ Télécharger",
                            f"Set : {set_query}\nLangue : {lang_name} ({lang_code})\n"
                            f"Qualité : {quality} — Format : {ext}\n"
                            f"Destination : {output_dir}\n\nLancer le téléchargement ?"):
            return

        results = {}

        def work(runner):
            from core.image_downloader import ImageDownloader

            def progress_callback(current, total, card_name=""):
                if card_name:
                    runner.log(f"📥 [{current}/{total}] {card_name}")

            downloader = ImageDownloader(progress_callback=progress_callback)
            runner.log(f"🔍 Recherche du set '{set_query}'...")

            set_info = downloader.resolve_set(set_query, lang=lang_code)
            if not set_info:
                raise TaskError(f"Set non trouvé: {set_query}")

            set_id = set_info.get('id', set_query)
            name_data = set_info.get('name', set_id)
            set_name = (name_data if isinstance(name_data, str)
                        else name_data.get(lang_code, set_id))
            runner.log(f"✅ Set: {set_name} ({set_id})")

            ok, fail, total = downloader.download_set(
                set_query=set_query, output_dir=output_dir,
                lang=lang_code, quality=quality, ext=ext, workers=8)

            runner.log(f"\n{'='*60}")
            runner.log(get_message('console.download_success', ok=ok, total=total))
            if fail > 0:
                runner.log(get_message('console.download_failure', fail=fail, total=total))

            # Régénérer la base de cartes depuis le manifest
            if ok > 0:
                runner.log("\n📋 Génération de cards_database.yaml...")
                try:
                    from core.manifest_tools import generate_yaml_from_manifest
                    count = generate_yaml_from_manifest(
                        f"{output_dir}/manifest.csv", set_id, set_name)
                    runner.log(f"✅ Base de cartes générée ({count} cartes)")
                except Exception as yaml_err:
                    runner.log(f"⚠️ Génération YAML échouée: {yaml_err}")

            results.update(ok=ok, fail=fail, total=total,
                           set_id=set_id, output_dir=output_dir)

        def on_success():
            if results.get('fail', 0) == 0:
                main.notify_info("✅ Succès",
                                 f"Téléchargement terminé !\n\n"
                                 f"✅ {results.get('ok', 0)} cartes\n"
                                 f"💾 {results.get('output_dir')}/{results.get('set_id')}/")
            else:
                main.notify_warning("⚠️ Terminé avec erreurs",
                                    f"✅ {results.get('ok', 0)} réussies — "
                                    f"❌ {results.get('fail', 0)} échecs")

        main.bridge.run("Image Download", work,
                        on_success=on_success,
                        on_error=lambda msg: main.notify_error("Erreur", msg))
