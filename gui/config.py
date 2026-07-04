"""
GuiConfig — accès centralisé à config/gui_config.json.

Remplace les lectures/écritures JSON dispersées entre ModernPokemonGUI
et SettingsDialog. Indépendant de Tkinter, testable sans display.
"""
import json
from pathlib import Path

DEFAULT_CONFIG_FILE = "gui_config.json"

DEFAULTS = {
    "paths": {
        "images_source": "images",
        "fakeimg": "fakeimg",
        "output": "output",
    },
    "last_used": {
        "num_aug": 15,
    },
}


class GuiConfig:
    """
    Configuration du GUI persistée en JSON.

    Usage:
        cfg = GuiConfig()               # charge gui_config.json (ou défauts)
        cfg.get("holographic_intensity", 0.7)
        cfg.set("theme", "dark")
        cfg.save()
    """

    def __init__(self, path: str = DEFAULT_CONFIG_FILE):
        self.path = Path(path)
        self.data = {}
        self.load()

    def load(self) -> dict:
        """(Re)charge le fichier; en cas d'erreur, repart des défauts."""
        if self.path.exists():
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.data = json.loads(json.dumps(DEFAULTS))
        else:
            self.data = json.loads(json.dumps(DEFAULTS))
        return self.data

    def get(self, key: str, default=None):
        """Lit une clé de premier niveau (comme dict.get)."""
        return self.data.get(key, default)

    def set(self, key: str, value) -> None:
        self.data[key] = value

    def update(self, values: dict) -> None:
        """Met à jour plusieurs clés d'un coup."""
        self.data.update(values)

    def save(self) -> bool:
        """Écrit le fichier. Retourne False en cas d'échec (disque, droits)."""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False
