#!/usr/bin/env python3
"""Test TCGdex avec Surging Sparks"""
from tcgdex_api import TCGdexAPI

api = TCGdexAPI('en')

print("🧪 Test Surging Sparks...")
print()

# Test 1: Exeggcute #001
print("1️⃣ Exeggcute #001/191")
price, pmax, details = api.search_card_with_prices('Exeggcute', 'Surging Sparks', '001/191')
if details:
    print(f"✅ Trouvé: {details.get('name')}")
    print(f"   Set: {details.get('set', {}).get('name')}")
    print(f"   Prix: {price}€ - {pmax}€")
    pricing = details.get('pricing', {})
    if pricing.get('cardmarket'):
        cm = pricing['cardmarket']
        print(f"   Cardmarket: trend={cm.get('trend')}€, avg={cm.get('avg')}€")
else:
    print("❌ Pas trouvé")

print()

# Test 2: Durant ex #004
print("2️⃣ Durant ex #004/191")
price, pmax, details = api.search_card_with_prices('Durant ex', 'Surging Sparks', '004/191')
if details:
    print(f"✅ Trouvé: {details.get('name')}")
    print(f"   Prix: {price}€ - {pmax}€")
else:
    print("❌ Pas trouvé")

print()
print("✅ Tests terminés!")
