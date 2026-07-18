#!/usr/bin/env python3
"""
Module d'intégration TCGdex API
API communautaire gratuite avec prix Cardmarket + TCGPlayer intégrés
Documentation: https://tcgdex.dev/
"""
import requests
from typing import Optional, Tuple, Dict, List

# Import safe_print pour gérer l'encodage Unicode sur Windows
try:
    from .utils import safe_print
except ImportError:
    from utils import safe_print


class TCGdexAPI:
    """
    Client pour l'API TCGdex (gratuite, sans authentification)
    
    Avantages:
    - Gratuit et open-source
    - Pas d'authentification requise
    - Prix Cardmarket (EUR) + TCGPlayer (USD) intégrés
    - Multilingue (10+ langues)
    - Images haute qualité
    """
    
    def __init__(self, language='en', cache=None):
        """
        Initialise le client TCGdex

        Args:
            language: Code langue (en, fr, es, it, pt, de, ja, zh, id, th)
            cache: PriceCache (F10) optionnel — les prix récupérés y sont
                   enregistrés et servis hors-ligne (voir get_card_prices)
        """
        self.base_url = f"https://api.tcgdex.net/v2/{language}"
        self.language = language
        self.cache = cache
        
        # Mapping des noms de sets vers codes TCGdex — mêmes codes que
        # POPULAR_SETS de core/image_downloader.py (les demi-sets utilisent
        # la notation décimale TCGdex : sv03.5, sv04.5, sv06.5…)
        self.set_mapping = {
            'surging sparks': 'sv08',
            'stellar crown': 'sv07',
            'shrouded fable': 'sv06.5',
            'twilight masquerade': 'sv06',
            'temporal forces': 'sv05',
            'paldean fates': 'sv04.5',
            'paradox rift': 'sv04',
            '151': 'sv03.5',
            'obsidian flames': 'sv03',
            'paldea evolved': 'sv02',
            'scarlet & violet': 'sv01',
            'base set': 'base1',
            'jungle': 'base2',
            'fossil': 'base3',
            'base set 2': 'base4',
            'team rocket': 'base5',
            'gym heroes': 'base6',
            'gym challenge': 'base7',
        }
    
    def search_cards(self, card_name: str, set_name: Optional[str] = None) -> List[Dict]:
        """
        Recherche des cartes par nom (filtrage CÔTÉ SERVEUR — l'endpoint
        /cards sans filtre renvoie le catalogue complet, des dizaines de
        milliers d'entrées)

        Args:
            card_name: Nom de la carte
            set_name: Nom de l'extension (optionnel pour filtrage)

        Returns:
            Liste de cartes trouvées (objets brefs: id, localId, name, image)
        """
        try:
            from urllib.parse import quote
            url = f"{self.base_url}/cards?name={quote(card_name)}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            cards = response.json()
            if not isinstance(cards, list):
                return []

            # Re-filtrer par nom (le filtre serveur est un 'like' large)
            name_lower = card_name.lower()
            filtered = [c for c in cards if name_lower in c.get('name', '').lower()]

            # Filtrer par set si fourni. Les objets brefs de l'endpoint
            # liste n'ont PAS de champ 'set' : on filtre sur le préfixe de
            # l'id (ex: "sv08-019") via le mapping nom -> code. Set inconnu
            # du mapping : ne pas filtrer (mieux vaut trop large que vide).
            if set_name and filtered:
                set_code = self.set_mapping.get(set_name.lower().strip())
                if set_code:
                    prefix = f"{set_code}-"
                    filtered = [c for c in filtered
                                if str(c.get('id', '')).startswith(prefix)]

            return filtered

        except Exception as e:
            safe_print(f"Erreur TCGdex search_cards: {e}")
            return []
    
    def get_card(self, card_id: str) -> Optional[Dict]:
        """
        Récupère les détails complets d'une carte par son ID
        
        Args:
            card_id: ID de la carte (ex: "swsh3-136")
            
        Returns:
            Dict avec toutes les infos de la carte incluant pricing
        """
        try:
            url = f"{self.base_url}/cards/{card_id}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            safe_print(f"Erreur TCGdex get_card: {e}")
            return None
        except Exception as e:
            safe_print(f"Erreur TCGdex get_card: {e}")
            return None
    
    def extract_prices(self, card: Dict) -> Tuple[Optional[float], Optional[float], str]:
        """
        Extrait les prix d'une carte TCGdex
        
        TCGdex inclut les prix de Cardmarket (EUR) et TCGPlayer (USD)
        
        Priorité:
        1. Cardmarket trend (prix tendance Europe)
        2. TCGPlayer marketPrice (prix marché USA)
        3. Autres prix disponibles
        
        Args:
            card: Dict de la carte TCGdex
            
        Returns:
            (price_avg, price_max, source) - source indique "TCGdex(CM)" ou "TCGdex(TCP)"
        """
        if not card:
            return None, None, None
        
        pricing = card.get('pricing', {})
        
        # 1. Essayer Cardmarket (Europe, EUR)
        cardmarket = pricing.get('cardmarket', {})
        if cardmarket:
            prices = []

            # Priorité: trend > avg > low (0.0 est un prix valide)
            cm_price = next((cardmarket.get(k)
                             for k in ('trend', 'avg', 'low')
                             if cardmarket.get(k) is not None), None)

            if cm_price is not None:
                prices.append(cm_price)

            # Ajouter les prix holo si disponibles
            for key in ['trend-holo', 'avg-holo', 'low-holo']:
                val = cardmarket.get(key)
                if val is not None:
                    prices.append(val)
            
            if prices:
                return min(prices), max(prices), "TCGdex(Cardmarket)"
        
        # 2. Essayer TCGPlayer (USA, USD)
        tcgplayer = pricing.get('tcgplayer', {})
        if tcgplayer:
            prices = []
            
            # Parcourir toutes les variantes (normal, reverse, holo, etc.)
            for variant_data in tcgplayer.values():
                if isinstance(variant_data, dict):
                    # Priorité: marketPrice > midPrice > lowPrice
                    price = next((variant_data.get(k)
                                  for k in ('marketPrice', 'midPrice', 'lowPrice')
                                  if variant_data.get(k) is not None), None)
                    if price is not None:
                        prices.append(price)
            
            if prices:
                return min(prices), max(prices), "TCGdex(TCGPlayer)"
        
        return None, None, None
    
    def get_card_prices(self, card_id: str):
        """
        Prix d'une carte AVEC cache transparent (F10).

        Stratégie :
        1. cache frais (TTL) -> aucun appel réseau
        2. API -> prix extraits et enregistrés dans le cache
        3. échec réseau -> entrée périmée du cache (mode hors-ligne),
           signalée par is_stale et sa date

        Args:
            card_id: clé canonique ("swsh7_003") ou identifiant TCGdex
                     ("swsh7-3")

        Returns:
            PriceEntry (price/price_max/source/fetched_at/is_stale),
            ou None si la carte est introuvable et absente du cache.
        """
        try:
            from .price_cache import normalize_card_id, tcgdex_id_candidates
        except ImportError:
            from price_cache import normalize_card_id, tcgdex_id_candidates
        key = normalize_card_id(card_id)

        # 1. Cache frais
        if self.cache is not None:
            entry = self.cache.get(key)
            if entry is not None and not entry.is_stale:
                return entry

        # 2. API (le padding du localId dépend du set : tester les variantes)
        card = None
        for tcgdex_id in tcgdex_id_candidates(card_id):
            card = self.get_card(tcgdex_id)
            if card is not None:
                break

        if card is not None:
            price, price_max, source = self.extract_prices(card)
            if self.cache is not None:
                return self.cache.put(key, price, price_max, source)
            try:
                from .price_cache import PriceEntry
            except ImportError:
                from price_cache import PriceEntry
            import time
            return PriceEntry(key, price, price_max, source, 'EUR', time.time())

        # 3. Hors-ligne : entrée périmée acceptée
        if self.cache is not None:
            entry = self.cache.get(key)
            if entry is not None:
                safe_print(f"📴 Hors-ligne: prix de {key} du {entry.date_str} (cache)")
                return entry
        return None

    def search_card_with_prices(
        self, 
        card_name: str, 
        set_name: Optional[str] = None,
        card_number: Optional[str] = None
    ) -> Tuple[Optional[float], Optional[float], Optional[Dict]]:
        """
        Recherche une carte et récupère ses prix (tout-en-un)
        
        Args:
            card_name: Nom de la carte
            set_name: Nom de l'extension (optionnel)
            card_number: Numéro de carte (optionnel)
            
        Returns:
            (price_avg, price_max, card_details)
        """
        try:
            # STRATÉGIE 1: Si on a le set + numéro, essayer de construire l'ID directement
            if set_name and card_number:
                set_lower = set_name.lower().strip()
                set_code = self.set_mapping.get(set_lower)
                
                if set_code:
                    # Extraire juste le numéro (avant le /)
                    number = str(card_number).split('/')[0].strip()
                    # Le zero-padding du localId dépend du set : tester
                    # les deux variantes (sv08-019 puis sv08-19)
                    candidates = [f"{set_code}-{number.zfill(3)}"]
                    stripped = number.lstrip('0') or '0'
                    if f"{set_code}-{stripped}" not in candidates:
                        candidates.append(f"{set_code}-{stripped}")

                    for card_id in candidates:
                        card_full = self.get_card(card_id)
                        if card_full:
                            price_avg, price_max, source = self.extract_prices(card_full)
                            return price_avg, price_max, card_full
            
            # STRATÉGIE 2: Recherche classique par nom (plus lent, fallback)
            # 1. Rechercher les cartes
            cards = self.search_cards(card_name, set_name)
            
            if not cards:
                return None, None, None
            
            # 2. Filtrer par numéro si fourni
            if card_number:
                # Normaliser le numéro (enlever les zéros devant)
                norm_number = str(card_number).split('/')[0].strip().lstrip('0') or '0'
                cards = [c for c in cards if c.get('localId', '').lstrip('0') == norm_number]
            
            if not cards:
                return None, None, None
            
            # 3. Prendre la première carte trouvée
            card_brief = cards[0]
            card_id = card_brief.get('id')
            
            if not card_id:
                return None, None, None
            
            # 4. Récupérer les détails complets (avec pricing)
            card_full = self.get_card(card_id)
            
            if not card_full:
                return None, None, None
            
            # 5. Extraire les prix
            price_avg, price_max, source = self.extract_prices(card_full)
            
            return price_avg, price_max, card_full
            
        except Exception as e:
            safe_print(f"Erreur TCGdex search_card_with_prices pour '{card_name}': {e}")
            return None, None, None


def test_tcgdex_api():
    """Fonction de test pour vérifier l'API TCGdex"""
    safe_print("🧪 Test de l'API TCGdex...")
    
    api = TCGdexAPI(language='en')
    
    # Test 1: Recherche simple
    safe_print("\n1️⃣ Recherche 'Pikachu'...")
    cards = api.search_cards('Pikachu')
    safe_print(f"✅ Trouvé {len(cards)} cartes Pikachu")
    
    if cards:
        card = cards[0]
        safe_print(f"   Premier résultat: {card.get('name')} - {card.get('id')}")
        
        # Test 2: Détails avec prix
        safe_print("\n2️⃣ Récupération des prix...")
        card_id = card.get('id')
        card_full = api.get_card(card_id)
        
        if card_full:
            price_avg, price_max, source = api.extract_prices(card_full)
            if price_avg:
                safe_print(f"✅ Prix min: {price_avg}")
                safe_print(f"✅ Prix max: {price_max}")
                safe_print(f"✅ Source: {source}")
                
                # Afficher les détails des prix
                pricing = card_full.get('pricing', {})
                if pricing.get('cardmarket'):
                    safe_print(f"\n📊 Cardmarket (EUR):")
                    cm = pricing['cardmarket']
                    safe_print(f"   trend: {cm.get('trend')}€")
                    safe_print(f"   avg: {cm.get('avg')}€")
                    safe_print(f"   low: {cm.get('low')}€")
                
                if pricing.get('tcgplayer'):
                    safe_print(f"\n📊 TCGPlayer (USD):")
                    tcp = pricing['tcgplayer']
                    for variant, data in tcp.items():
                        if isinstance(data, dict) and variant != 'updated' and variant != 'unit':
                            market = data.get('marketPrice')
                            if market:
                                safe_print(f"   {variant}: ${market}")
            else:
                safe_print("⚠️ Pas de prix disponible")
        else:
            safe_print("❌ Impossible de récupérer les détails")
    
    # Test 3: Recherche avec tout-en-un
    safe_print("\n3️⃣ Recherche tout-en-un 'Charizard' + 'Base Set'...")
    price_avg, price_max, details = api.search_card_with_prices('Charizard', 'Base Set')
    
    if price_avg:
        safe_print(f"✅ Charizard Base Set trouvé!")
        safe_print(f"   Prix min: {price_avg}")
        safe_print(f"   Prix max: {price_max}")
        safe_print(f"   Set: {details.get('set', {}).get('name')}")
    else:
        safe_print("⚠️ Charizard Base Set non trouvé (normal, carte rare)")
    
    safe_print("\n✅ Tests terminés !")


if __name__ == "__main__":
    test_tcgdex_api()
