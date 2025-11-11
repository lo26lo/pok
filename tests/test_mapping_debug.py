"""Test rapide du système de mapping et prix"""
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("TEST DU SYSTÈME DE MAPPING ET PRIX")
print("=" * 60)
print()

# Test 1: Mapping
print("1️⃣ Test du mapping card_name_to_id.json...")
from core.card_mapping import get_card_id_from_class_name

test_cards = ["Exeggcute", "Exeggutor", "Milotic_ex", "Cyrano", "Unknown_Card"]
for card_name in test_cards:
    card_id = get_card_id_from_class_name(card_name)
    print(f"   {card_name:20} -> {card_id if card_id else 'Non trouvé'}")

print()

# Test 2: Chargement des prix
print("2️⃣ Test du chargement des prix...")
from core.utils import load_prices

prices = load_prices("models/cards_database.yaml")
print(f"   Nombre de prix chargés: {len(prices)}")
print(f"   Clés dans prices: {list(prices.keys())[:5]}...")  # Afficher seulement les 5 premières
print()

# Test 3: Vérification de la correspondance
print("3️⃣ Test de la correspondance complète...")
for card_name in ["Exeggcute", "Milotic_ex", "Cyrano"]:
    card_id = get_card_id_from_class_name(card_name)
    if card_id:
        if card_id in prices:
            info = prices[card_id]
            print(f"   ✅ {card_name} -> {card_id} -> Prix: {info['price']}€")
        else:
            print(f"   ❌ {card_name} -> {card_id} -> PRIX NON TROUVÉ dans Excel")
            print(f"      Excel contient: {list(prices.keys())}")
    else:
        print(f"   ❌ {card_name} -> Pas de mapping")

print()
print("=" * 60)
