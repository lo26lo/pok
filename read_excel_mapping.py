#!/usr/bin/env python3
"""
Lit le fichier Excel pour obtenir la vraie correspondance des cartes
"""
import pandas as pd
from pathlib import Path

def read_cards_mapping():
    """Lit cards_info.xlsx pour obtenir le mapping correct"""
    excel_path = Path("excel/cards_info.xlsx")
    
    if not excel_path.exists():
        print(f"❌ Fichier non trouvé: {excel_path}")
        return
    
    print("="*70)
    print("📖 LECTURE DU MAPPING DES CARTES")
    print("="*70)
    
    # Lire le fichier Excel
    df = pd.read_excel(excel_path)
    
    print(f"\n📊 Colonnes disponibles:")
    for col in df.columns:
        print(f"   - {col}")
    
    print(f"\n📋 Premières lignes du fichier:")
    print(df.head(20))
    
    print(f"\n🔍 Recherche de nos cartes (19, 20, 26, 46, 51, 126, 132, 152):")
    our_card_numbers = [19, 20, 26, 46, 51, 126, 132, 152]
    
    mapping = {}
    for card_num in our_card_numbers:
        # Format: "019/191"
        set_num_str = f"{card_num:03d}/191"
        matching_rows = df[df['Set #'] == set_num_str]
        
        if not matching_rows.empty:
            row = matching_rows.iloc[0]
            name = row['Name']
            mapping[card_num] = name
            print(f"\n  sv08_{card_num:03d} -> {name}")
        else:
            print(f"\n  Card #{card_num}: ❌ NON TROUVÉ")
    
    print(f"\n\n📋 MAPPING POUR LE SCRIPT:")
    print("card_mapping = {")
    for i, (card_num, name) in enumerate(sorted(mapping.items())):
        print(f"    {card_num}: {i},  # sv08_{card_num:03d} -> {name}")
    print("}")

if __name__ == "__main__":
    read_cards_mapping()
