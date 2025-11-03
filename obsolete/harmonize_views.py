#!/usr/bin/env python3
"""
Script pour harmoniser toutes les vues de GUI_v3.1_modern.py
Applique les constantes de padding, fonts ET widgets de manière cohérente
"""
import re

def harmonize_gui():
    """Harmoniser le fichier GUI"""
    file_path = "GUI_v3.1_modern.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns à remplacer
    replacements = [
        # Headers des vues - container padding
        (r'container\.pack\(fill=tk\.BOTH, expand=True, padx=30, pady=20\)',
         'container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)'),
        
        (r'container\.pack\(fill=tk\.BOTH, expand=True, padx=20, pady=20\)',
         'container.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_VIEW, pady=self.PADDING_VIEW)'),
        
        # Titres principaux des vues
        (r"font=\('Segoe UI', 24, 'bold'\)",
         'font=self.FONT_TITLE'),
        
        # Sous-titres
        (r"font=\('Segoe UI', 11\)",
         'font=self.FONT_TEXT'),
        
        # Titres de cartes
        (r"font=\('Segoe UI', 14, 'bold'\)",
         'font=self.FONT_CARD_TITLE'),
        
        (r"font=\('Segoe UI', 12, 'bold'\)",
         'font=self.FONT_CARD_TITLE'),
        
        # Texte normal
        (r"font=\('Segoe UI', 10\)",
         'font=self.FONT_TEXT'),
        
        # Boutons
        (r"font=\('Segoe UI', 10, 'bold'\)",
         'font=self.FONT_BUTTON'),
        
        # Padding après sous-titre
        (r'subtitle\.pack\(anchor=\'w\', pady=\(0, 30\)\)',
         'subtitle.pack(anchor=\'w\', pady=(0, self.CARD_SPACING))'),
        
        # Padding entre cartes
        (r'\.pack\(fill=tk\.X, pady=20\)',
         '.pack(fill=tk.X, pady=self.CARD_SPACING)'),
        
        (r'\.pack\(fill=tk\.X, pady=\(0, 20\)\)',
         '.pack(fill=tk.X, pady=(0, self.CARD_SPACING))'),
        
        # Padding interne des cartes
        (r'\.pack\(fill=tk\.X, padx=20, pady=15\)',
         '.pack(fill=tk.X, padx=self.PADDING_CARD, pady=self.PADDING_VERTICAL)'),
        
        (r'\.pack\(fill=tk\.BOTH, expand=True, padx=20, pady=20\)',
         '.pack(fill=tk.BOTH, expand=True, padx=self.PADDING_CARD, pady=self.PADDING_CARD)'),
        
        # Spinbox widths - réduire toutes les largeurs
        (r'ttk\.Spinbox\([^)]+, width=10\)',
         lambda m: m.group(0).replace('width=10', 'width=self.SPINBOX_WIDTH')),
        
        (r'ttk\.Spinbox\([^)]+, width=12\)',
         lambda m: m.group(0).replace('width=12', 'width=self.SPINBOX_WIDTH')),
        
        (r'ttk\.Spinbox\([^)]+, width=15\)',
         lambda m: m.group(0).replace('width=15', 'width=self.SPINBOX_WIDTH')),
        
        # Combobox widths - réduire toutes les largeurs
        (r'ttk\.Combobox\([^)]+, width=25\)',
         lambda m: m.group(0).replace('width=25', 'width=self.COMBOBOX_WIDTH')),
        
        (r'ttk\.Combobox\([^)]+, width=30\)',
         lambda m: m.group(0).replace('width=30', 'width=self.COMBOBOX_WIDTH')),
        
        (r'ttk\.Combobox\([^)]+, width=20\)',
         lambda m: m.group(0).replace('width=20', 'width=self.COMBOBOX_WIDTH')),
        
        # Entry widths - réduire
        (r'ttk\.Entry\([^)]+, width=40\)',
         lambda m: m.group(0).replace('width=40', 'width=self.ENTRY_WIDTH')),
        
        (r'ttk\.Entry\([^)]+, width=35\)',
         lambda m: m.group(0).replace('width=35', 'width=self.ENTRY_WIDTH')),
    ]
    
    # Appliquer les remplacements
    for pattern, replacement in replacements:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Harmonisation terminée!")
    print("   - Padding des vues: self.PADDING_VIEW (20px)")
    print("   - Padding des cartes: self.PADDING_CARD (20px)")
    print("   - Espacement vertical: self.PADDING_VERTICAL (15px)")
    print("   - Espacement entre cartes: self.CARD_SPACING (20px)")
    print("   - Titres: self.FONT_TITLE (20pt)")
    print("   - Titres cartes: self.FONT_CARD_TITLE (14pt)")
    print("   - Texte: self.FONT_TEXT (9pt)")
    print("   - Boutons: self.FONT_BUTTON (10pt)")
    print("   - Spinbox: self.SPINBOX_WIDTH (8)")
    print("   - Combobox: self.COMBOBOX_WIDTH (18)")
    print("   - Entry: self.ENTRY_WIDTH (30)")

if __name__ == "__main__":
    harmonize_gui()
