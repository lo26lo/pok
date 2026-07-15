"""
Thèmes Qt — clair (Catppuccin Latte) et sombre (Catppuccin Mocha).

Le thème sombre reprend exactement la palette du GUI Tkinter
(gui/theme.py). La feuille de style QSS est générée depuis la palette,
donc les deux thèmes restent structurellement identiques.
"""

DARK = {   # Catppuccin Mocha — identique à gui.theme.COLORS
    'bg_dark': '#1e1e2e',
    'bg_sidebar': '#181825',
    'bg_card': '#313244',
    'bg_hover': '#45475a',
    'accent': '#89b4fa',
    'accent_hover': '#74c7ec',
    'success': '#a6e3a1',
    'warning': '#f9e2af',
    'error': '#f38ba8',
    'text': '#cdd6f4',
    'text_dim': '#9399b2',
    'border': '#45475a',
    'on_accent': '#11111b',
}

LIGHT = {  # Catppuccin Latte
    'bg_dark': '#eff1f5',
    'bg_sidebar': '#e6e9ef',
    'bg_card': '#dce0e8',
    'bg_hover': '#ccd0da',
    'accent': '#1e66f5',
    'accent_hover': '#209fb5',
    'success': '#40a02b',
    'warning': '#df8e1d',
    'error': '#d20f39',
    'text': '#4c4f69',
    'text_dim': '#6c6f85',
    'border': '#bcc0cc',
    'on_accent': '#ffffff',
}

THEMES = {'dark': DARK, 'light': LIGHT}


def build_qss(palette: dict) -> str:
    """Feuille de style Qt générée depuis une palette."""
    p = palette
    return f"""
QMainWindow, QDialog, QWidget {{
    background-color: {p['bg_dark']};
    color: {p['text']};
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 10pt;
}}
QListWidget#sidebar {{
    background-color: {p['bg_sidebar']};
    border: none;
    outline: none;
    padding-top: 8px;
}}
QListWidget#sidebar::item {{
    padding: 10px 14px;
    color: {p['text_dim']};
    border-left: 3px solid transparent;
}}
QListWidget#sidebar::item:hover {{
    background-color: {p['bg_card']};
    color: {p['text']};
}}
QListWidget#sidebar::item:selected {{
    background-color: {p['bg_hover']};
    color: {p['accent']};
    border-left: 3px solid {p['accent']};
}}
QFrame#card {{
    background-color: {p['bg_card']};
    border: 1px solid {p['border']};
    border-radius: 8px;
}}
QLabel#viewTitle {{
    font-size: 17pt;
    font-weight: bold;
    color: {p['text']};
}}
QLabel#cardTitle {{
    font-size: 12pt;
    font-weight: bold;
    color: {p['accent']};
}}
QLabel#statValue {{
    font-size: 16pt;
    font-weight: bold;
    color: {p['accent']};
}}
QLabel#dim {{ color: {p['text_dim']}; }}
QPushButton {{
    background-color: {p['bg_hover']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: bold;
}}
QPushButton:hover {{ background-color: {p['border']}; }}
QPushButton:disabled {{ color: {p['text_dim']}; }}
QPushButton#primary {{
    background-color: {p['accent']};
    color: {p['on_accent']};
    border: none;
}}
QPushButton#primary:hover {{ background-color: {p['accent_hover']}; }}
QPushButton#danger {{
    background-color: {p['error']};
    color: {p['on_accent']};
    border: none;
}}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {p['bg_card']};
    color: {p['text']};
    border: 1px solid {p['border']};
    border-radius: 5px;
    padding: 5px 8px;
    selection-background-color: {p['accent']};
}}
QComboBox QAbstractItemView {{
    background-color: {p['bg_card']};
    color: {p['text']};
    selection-background-color: {p['bg_hover']};
}}
QPlainTextEdit#logPanel {{
    background-color: {p['bg_sidebar']};
    color: {p['text']};
    border: 1px solid {p['border']};
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 9pt;
}}
QCheckBox, QRadioButton {{ color: {p['text']}; spacing: 8px; }}
QProgressBar {{
    background-color: {p['bg_card']};
    border: 1px solid {p['border']};
    border-radius: 5px;
    text-align: center;
    color: {p['text']};
}}
QProgressBar::chunk {{ background-color: {p['accent']}; border-radius: 4px; }}
QTabWidget::pane {{ border: 1px solid {p['border']}; border-radius: 6px; }}
QTabBar::tab {{
    background-color: {p['bg_card']};
    color: {p['text_dim']};
    padding: 7px 14px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{ background-color: {p['bg_hover']}; color: {p['accent']}; }}
QStatusBar {{ background-color: {p['bg_sidebar']}; color: {p['text_dim']}; }}
QDockWidget::title {{
    background-color: {p['bg_sidebar']};
    color: {p['text_dim']};
    padding: 5px;
}}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{
    background: {p['bg_dark']}; width: 10px; border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {p['bg_hover']}; border-radius: 5px; min-height: 24px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QSlider::groove:horizontal {{
    background: {p['bg_card']}; height: 6px; border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {p['accent']}; width: 14px; margin: -5px 0; border-radius: 7px;
}}
"""
