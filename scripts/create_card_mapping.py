"""
Crée un fichier de mapping entre les noms de classes YOLO et les IDs dans l'Excel
Basé sur les 8 cartes d'entraînement
"""
import json

# Mapping manuel basé sur data.yaml et les cartes d'entraînement
# Les cartes dans l'Excel sont:
# sv08-019: Exeggcute
# sv08-020: Exeggutor
# sv08-026: Scovillain ex
# sv08-046: Milotic ex
# sv08-051: Black Kyurem ex
# sv08-126: Archaludon ex
# sv08-132: Alolan Exeggutor ex
# sv08-152: Cyrano

# Mapping des noms de classes vers les IDs Excel
card_mapping = {
    "Exeggcute": "sv08_019",
    "Exeggutor": "sv08_020",
    "Scovillain_ex": "sv08_026",
    "Milotic_ex": "sv08_046",
    "Black_Kyurem_ex": "sv08_051",
    "Archaludon_ex": "sv08_126",
    "Alolan_Exeggutor_ex": "sv08_132",
    "Cyrano": "sv08_152"
}

# Sauvegarder dans un fichier JSON
with open("card_name_to_id.json", "w", encoding="utf-8") as f:
    json.dump(card_mapping, f, indent=2, ensure_ascii=False)

print("✅ Fichier card_name_to_id.json créé!")
print(f"📋 {len(card_mapping)} cartes mappées:")
for name, card_id in card_mapping.items():
    print(f"   • {name} → {card_id}")
