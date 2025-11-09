"""
Script simplifié pour mettre à jour UNIQUEMENT les prix des 8 cartes d'entraînement
Format attendu dans data.yaml: sv08_019, sv08_020, etc.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')

from core.tcgdex_api import TCGdexAPI

# Définir manuellement les 8 cartes d'entraînement
TRAINING_CARDS = {
    'sv08-019': {'name': 'Exeggcute', 'set': 'Surging Sparks', 'number': '019'},
    'sv08-020': {'name': 'Exeggutor', 'set': 'Surging Sparks', 'number': '020'},
    'sv08-026': {'name': 'Scovillain ex', 'set': 'Surging Sparks', 'number': '026'},
    'sv08-046': {'name': 'Milotic ex', 'set': 'Surging Sparks', 'number': '046'},
    'sv08-051': {'name': 'Black Kyurem ex', 'set': 'Surging Sparks', 'number': '051'},
    'sv08-126': {'name': 'Archaludon ex', 'set': 'Surging Sparks', 'number': '126'},
    'sv08-132': {'name': 'Alolan Exeggutor ex', 'set': 'Surging Sparks', 'number': '132'},
    'sv08-152': {'name': 'Cyrano', 'set': 'Surging Sparks', 'number': '152'},
}

def init_excel_with_prices():
    """Initialise l'Excel avec les 8 cartes d'entraînement + prix"""
    
    print("📋 Cartes à ajouter:")
    for card_id, info in TRAINING_CARDS.items():
        print(f"   • {card_id}: {info['name']}")
    
    # Créer DataFrame
    df = pd.DataFrame({
        'Name': [info['name'] for info in TRAINING_CARDS.values()],
        'Set #': [f"sv08_{num}" for num in [info['number'] for info in TRAINING_CARDS.values()]],
        'Prix': [None] * len(TRAINING_CARDS),
        'Prix max': [None] * len(TRAINING_CARDS),
        'SourcePrix': [''] * len(TRAINING_CARDS)
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
    
    for idx, (card_id, info) in enumerate(TRAINING_CARDS.items(), 1):
        print(f"[{idx}/{len(TRAINING_CARDS)}] {card_id} ({info['name']})...", end=' ')
        
        try:
            # Recherche par set + numéro
            price, price_max, details = api.search_card_with_prices(
                card_name=info['name'],
                set_name=info['set'],
                card_number=info['number']
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
    
    # Sauvegarder avec prix
    print(f"\n💾 Sauvegarde des prix...")
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    print(f"\n✅ Terminé!")
    print(f"   📊 {success_count}/{len(TRAINING_CARDS)} cartes avec prix")
    print(f"   💾 Fichier: {excel_path}")
    print(f"\n💡 Tu peux maintenant utiliser la détection avec prix!")


if __name__ == "__main__":
    print("=" * 60)
    print("  INITIALISATION EXCEL - 8 CARTES D'ENTRAÎNEMENT")
    print("=" * 60)
    print()
    
    try:
        init_excel_with_prices()
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Appuyez sur Entrée pour quitter...")
