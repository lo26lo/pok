"""
Thème visuel du GUI — source unique pour la palette et les constantes
de mise en page (extrait de GUI_v3.1_modern.py, Phase 4).

Palette inspirée de Catppuccin Mocha.
"""

COLORS = {
    'bg_dark': '#1e1e2e',       # Background principal
    'bg_sidebar': '#181825',     # Sidebar
    'bg_card': '#313244',        # Cartes/Panels
    'bg_hover': '#45475a',       # Hover
    'accent': '#89b4fa',         # Bleu accent
    'accent_hover': '#74c7ec',   # Bleu hover
    'success': '#a6e3a1',        # Vert success
    'warning': '#f9e2af',        # Jaune warning
    'error': '#f38ba8',          # Rouge error
    'text': '#cdd6f4',           # Texte principal
    'text_dim': '#9399b2',       # Texte secondaire
    'border': '#45475a',         # Bordures
}

# Constantes d'harmonisation (V3.1)
PADDING_VIEW = 20            # Padding externe des vues
PADDING_CARD = 20            # Padding interne des cartes
PADDING_VERTICAL = 15        # Espacement vertical entre éléments
CARD_SPACING = 20            # Espacement entre cartes

FONT_TITLE = ('Segoe UI', 20, 'bold')       # Titres de vues
FONT_CARD_TITLE = ('Segoe UI', 14, 'bold')  # Titres de cartes
FONT_TEXT = ('Segoe UI', 9)                 # Texte normal
FONT_BUTTON = ('Segoe UI', 10, 'bold')      # Boutons

SPINBOX_WIDTH = 6
COMBOBOX_WIDTH = 15
ENTRY_WIDTH = 25
