import requests
import json

# Charger la clé API depuis le fichier de configuration
with open("api_config.json", "r") as f:
    config = json.load(f)
    API_KEY = config["pokemon_tcg_api_key"]

BASE_URL = "https://api.pokemontcg.io/v2/cards"
HEADERS = {"X-Api-Key": API_KEY}

# Test 1: Recherche par nom d'extension
print("=" * 60)
print("Test 1: Recherche avec set.name")
params = {
    "q": 'set.name:"Surging Sparks"',
    "page": 1,
    "pageSize": 10
}
response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
print(f"URL: {response.url}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total trouvé: {data.get('totalCount', 0)}")
    print(f"Cartes dans cette page: {len(data.get('data', []))}")
    if data.get('data'):
        print(f"Première carte: {data['data'][0].get('name')}")
else:
    print(f"Erreur: {response.text[:500]}")

# Test 2: Lister toutes les extensions disponibles
print("\n" + "=" * 60)
print("Test 2: Liste des extensions récentes")
response = requests.get("https://api.pokemontcg.io/v2/sets", headers=HEADERS, timeout=30)
if response.status_code == 200:
    sets = response.json().get('data', [])
    print(f"Total d'extensions: {len(sets)}")
    print("\nDernières extensions:")
    for s in sets[:10]:
        print(f"  - {s['name']} (ID: {s['id']}, Total: {s.get('total', 'N/A')} cartes)")

# Test 3: Recherche par ID d'extension
print("\n" + "=" * 60)
print("Test 3: Recherche avec set.id")
params = {
    "q": 'set.id:"sv08"',  # Essayons avec l'ID
    "page": 1,
    "pageSize": 10
}
response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
print(f"URL: {response.url}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Total trouvé: {data.get('totalCount', 0)}")
    print(f"Cartes dans cette page: {len(data.get('data', []))}")
