"""
Créer l'Excel avec les VRAIES 8 cartes d'entraînement
Basé sur le fichier images/manifest.csv
"""
import pandas as pd
from core.tcgdex_api import TCGdexAPI

# Les 8 cartes réelles d'après le manifest
REAL_CARDS = {
    'sv08_019': {'id': 'sv08-019', 'name': 'Ho-Oh', 'set': 'Surging Sparks', 'number': '019'},
    'sv08_020': {'id': 'sv08-020', 'name': 'Castform', 'set': 'Surging Sparks', 'number': '020'},
    'sv08_026': {'id': 'sv08-026', 'name': 'Oricorio', 'set': 'Surging Sparks', 'number': '026'},
    'sv08_046': {'id': 'sv08-046', 'name': 'Spheal', 'set': 'Surging Sparks', 'number': '046'},
    'sv08_051': {'id': 'sv08-051', 'name': 'Quaxly', 'set': 'Surging Sparks', 'number': '051'},
    'sv08_126': {'id': 'sv08-126', 'name': 'Bronzor', 'set': 'Surging Sparks', 'number': '126'},
    'sv08_132': {'id': 'sv08-132', 'name': 'Iron Crown', 'set': 'Surging Sparks', 'number': '132'},
    'sv08_152': {'id': 'sv08-152', 'name': 'Braviary', 'set': 'Surging Sparks', 'number': '152'},
}

print("=" * 70)
print("  CRÉATION EXCEL - 8 VRAIES CARTES D'ENTRAÎNEMENT")
print("=" * 70)
print()

# Créer le DataFrame initial
data = []
for card_id, info in REAL_CARDS.items():
    data.append({
        'Name': info['name'],
        'Set #': card_id,
        'Prix': None,
        'Prix max': None,
        'SourcePrix': None
    })

df = pd.DataFrame(data)

print("📋 Cartes à ajouter:")
for card_id, info in REAL_CARDS.items():
    print(f"   • {card_id}: {info['name']}")
print()

# Sauvegarder l'Excel
print("💾 Sauvegarde dans excel/cards_info.xlsx...")
df.to_excel('excel/cards_info.xlsx', index=False, engine='openpyxl')
print("✅ Excel créé!\n")

# Récupérer les prix depuis TCGdex
print("💰 Mise à jour des prix depuis TCGdex...")
print("   (Cela peut prendre quelques secondes...)\n")

api = TCGdexAPI(language='en')
success_count = 0

for idx, (card_id, info) in enumerate(REAL_CARDS.items(), 1):
    print(f"[{idx}/8] {card_id} ({info['name']})...", end=' ')
    
    try:
        price, price_max, details = api.search_card_with_prices(
            card_name=info['name'],
            set_name=info['set'],
            card_number=info['number']
        )
        
        if price is not None:
            df.loc[df['Set #'] == card_id, 'Prix'] = price
            df.loc[df['Set #'] == card_id, 'Prix max'] = price_max
            df.loc[df['Set #'] == card_id, 'SourcePrix'] = 'TCGdex'
            print(f"✅ {price:.2f}€")
            success_count += 1
        else:
            print("❌ Prix non disponible")
    except Exception as e:
        print(f"❌ Erreur: {e}")

print()
print("💾 Sauvegarde des prix...")
df.to_excel('excel/cards_info.xlsx', index=False, engine='openpyxl')

print()
print("✅ Terminé!")
print(f"   📊 {success_count}/8 cartes avec prix")
print(f"   💾 Fichier: excel/cards_info.xlsx")
print()
print("💡 Tu peux maintenant utiliser la détection avec prix!")
print()
input("Appuyez sur Entrée pour quitter...")
