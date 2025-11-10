"""
Crée le mapping entre les noms de classes YOLO et les vraies cartes
Basé sur data.yaml et les 8 vraies images d'entraînement
"""
import json

# Mapping des noms de classes YOLO vers les IDs Excel
# Basé sur ce qui est dans data.yaml et le manifest
card_mapping = {
    "Ho-Oh": "sv08_019",
    "Castform_Sunny_Form": "sv08_020",
    "Oricorio": "sv08_026",
    "Spheal": "sv08_046",
    "Quaxly": "sv08_051",
    "Bronzor": "sv08_126",
    "Iron_Crown": "sv08_132",
    "Braviary": "sv08_152"
}

# Sauvegarder dans un fichier JSON
with open("card_name_to_id.json", "w", encoding="utf-8") as f:
    json.dump(card_mapping, f, indent=2, ensure_ascii=False)

print("✅ Fichier card_name_to_id.json créé!")
print(f"📋 {len(card_mapping)} cartes mappées:")
for name, card_id in card_mapping.items():
    print(f"   • {name:25} → {card_id}")
