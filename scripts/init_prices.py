"""
Script pour initialiser le fichier Excel avec les cartes du dataset
Et mettre à jour les prix depuis TCGdex API
"""

import pandas as pd
import yaml
from pathlib import Path
import sys
sys.path.append('.')

from core.tcgdex_api import TCGdexAPI

def init_excel_with_cards():
    """Initialise l'Excel avec les cartes depuis data.yaml"""
    
    # Charger data.yaml
    data_yaml = Path("output/dataset/data.yaml")
    
    if not data_yaml.exists():
        print("❌ Fichier data.yaml non trouvé!")
        print(f"   Cherché dans: {data_yaml}")
        return
    
    print(f"📋 Lecture de {data_yaml}...")
    with open(data_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    names = data.get('names', [])
    
    if not names:
        print("❌ Aucune carte trouvée dans data.yaml!")
        return
    
    print(f"✅ Trouvé {len(names)} cartes:")
    for name in names:
        print(f"   • {name}")
    
    # Créer DataFrame
    df = pd.DataFrame({
        'Name': names,
        'Set #': names,  # Set # = même que le nom (ex: sv08_019)
        'Prix': [None] * len(names),
        'Prix max': [None] * len(names),
        'SourcePrix': [''] * len(names)
    })
    
    # Sauvegarder Excel
    excel_path = Path("excel/cards_info.xlsx")
    excel_path.parent.mkdir(exist_ok=True)
    
    print(f"\n💾 Sauvegarde dans {excel_path}...")
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print("✅ Excel créé!")
    
    # Mettre à jour les prix
    print("\n💰 Mise à jour des prix depuis TCGdex...")
    print("   (Cela peut prendre quelques secondes...)\n")
    
    # Initialiser l'API TCGdex
    api = TCGdexAPI(language='en')
    
    success_count = 0
    
    for idx, card_id in enumerate(names, 1):
        # Extraire set et number depuis l'ID
        # Format: sv08_019 = set "sv08", number "019"
        parts = card_id.split('_')
        if len(parts) >= 2:
            set_id = parts[0]  # sv08
            number = parts[1]  # 019
            
            print(f"[{idx}/{len(names)}] {card_id} (set={set_id}, num={number})...", end=' ')
            
            try:
                price, price_max, details = api.search_card_with_prices(
                    card_name="",  # On cherche par set+number
                    set_name=set_id,
                    set_hash=number
                )
                
                if price is not None:
                    df.loc[idx-1, 'Prix'] = price
                    df.loc[idx-1, 'Prix max'] = price_max if price_max else price
                    df.loc[idx-1, 'SourcePrix'] = 'TCGdex'
                    print(f"✅ {price}€")
                    success_count += 1
                else:
                    print("⚠️ Prix non trouvé")
                    
            except Exception as e:
                print(f"❌ Erreur: {e}")
        else:
            print(f"[{idx}/{len(names)}] {card_id} - ⚠️ Format invalide (attendu: setXX_XXX)")
    
    # Sauvegarder avec prix
    print(f"\n💾 Sauvegarde des prix...")
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    print(f"\n✅ Terminé!")
    print(f"   📊 {success_count}/{len(names)} cartes avec prix")
    print(f"   💾 Fichier: {excel_path}")
    print(f"\n💡 Tu peux maintenant utiliser la détection avec prix!")


if __name__ == "__main__":
    print("=" * 60)
    print("  INITIALISATION EXCEL + MISE À JOUR PRIX")
    print("=" * 60)
    print()
    
    try:
        init_excel_with_cards()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
