"""Test complet de la chaîne: class_name -> card_id -> prix"""
import sys
sys.path.insert(0, '.')

from core.card_mapping import get_card_id_from_class_name
from core.utils import load_prices

print("=" * 70)
print("TEST COMPLET: CLASS_NAME -> CARD_ID -> PRIX")
print("=" * 70)
print()

# Charger les prix depuis YAML
prices = load_prices("models/cards_database.yaml")
print(f"✅ {len(prices)} prix chargés depuis YAML\n")

# Tester pour chaque carte
test_class_names = [
    "Exeggcute",
    "Exeggutor", 
    "Scovillain_ex",
    "Milotic_ex",
    "Black_Kyurem_ex",
    "Archaludon_ex",
    "Alolan_Exeggutor_ex",
    "Cyrano"
]

print("Résultats:")
print("-" * 70)

for class_name in test_class_names:
    # Étape 1: class_name -> card_id
    card_id = get_card_id_from_class_name(class_name)
    
    if not card_id:
        print(f"❌ {class_name:25} -> Pas de mapping")
        continue
    
    # Étape 2: card_id -> prix
    if card_id in prices:
        info = prices[card_id]
        price = info['price']
        price_max = info['price_max']
        print(f"✅ {class_name:25} -> {card_id:12} -> {price}€ / {price_max}€")
    else:
        print(f"⚠️ {class_name:25} -> {card_id:12} -> PAS DANS EXCEL")
        print(f"   Clés disponibles dans Excel: {list(prices.keys())[:3]}...")

print("-" * 70)
print()
print("🔍 Debug - Clés dans le dictionnaire prices:")
for key in list(prices.keys()):
    print(f"   '{key}' (type: {type(key).__name__})")

print()
print("=" * 70)
