import pandas as pd
import json

# Lire l'Excel
df = pd.read_excel('excel/cards_info.xlsx')
print("Contenu de l'Excel:")
print(df)
print("\nColonne 'Set #':")
print(df['Set #'].tolist())

# Lire le mapping
with open('card_name_to_id.json', 'r') as f:
    mapping = json.load(f)
print("\nMapping JSON:")
for k, v in mapping.items():
    print(f"  {k} -> {v}")

print("\n⚠️ PROBLÈME IDENTIFIÉ:")
print(f"  Excel utilise des underscores: sv08_019")
print(f"  Mapping produit: {list(mapping.values())}")
print(f"  Les clés matchent? {mapping['Exeggcute'] in df['Set #'].values}")
