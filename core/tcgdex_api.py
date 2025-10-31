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
    
    def __init__(self, language='en'):
        """
        Initialise le client TCGdex
        
        Args:
            language: Code langue (en, fr, es, it, pt, de, ja, zh, id, th)
        """
        self.base_url = f"https://api.tcgdex.net/v2/{language}"
        self.language = language
        
        # Mapping des noms de sets vers codes TCGdex (les plus récents et courants)
        self.set_mapping = {
            'surging sparks': 'sv08',
            'stellar crown': 'sv07',
            'shrouded fable': 'sv06',
            'twilight masquerade': 'sv05',
            'temporal forces': 'sv04',
            'paldean fates': 'sv03',
            'paradox rift': 'sv02',
            'obsidian flames': 'sv01',
            '151': 'sv151',
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
        Recherche des cartes par nom
        
        Args:
            card_name: Nom de la carte
            set_name: Nom de l'extension (optionnel pour filtrage)
            
        Returns:
            Liste de cartes trouvées
        """
        try:
            url = f"{self.base_url}/cards"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            cards = response.json()
            
            # Filtrer par nom (case-insensitive)
            name_lower = card_name.lower()
            filtered = [c for c in cards if name_lower in c.get('name', '').lower()]
            
            # Filtrer par set si fourni
            if set_name and filtered:
                set_lower = set_name.lower()
                filtered = [c for c in filtered if set_lower in c.get('set', {}).get('name', '').lower()]
            
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
            
            # Priorité: trend > avg > low
            cm_price = cardmarket.get('trend') or cardmarket.get('avg') or cardmarket.get('low')
            
            if cm_price:
                prices.append(cm_price)
            
            # Ajouter les prix holo si disponibles
            for key in ['trend-holo', 'avg-holo', 'low-holo']:
                val = cardmarket.get(key)
                if val:
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
                    price = (
                        variant_data.get('marketPrice') or 
                        variant_data.get('midPrice') or 
                        variant_data.get('lowPrice')
                    )
                    if price:
                        prices.append(price)
            
            if prices:
                return min(prices), max(prices), "TCGdex(TCGPlayer)"
        
        return None, None, None
    
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
                    # Construire l'ID: sv08-001
                    card_id = f"{set_code}-{number.zfill(3)}"
                    
                    # Essayer de récupérer directement
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
