"""
Script OPTIMISÉ pour mettre à jour les prix dans models/cards_database.yaml depuis TCGdex API
Version avec requêtes parallèles (concurrent) pour 5-10x speedup
"""

import sys
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, Optional

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import safe_print

# Charger paths depuis config
def load_paths():
    config_path = Path("config/paths.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

PATHS = load_paths()


def update_single_card(card_id: str, card_info: dict, api) -> Tuple[str, Optional[dict]]:
    """
    Met à jour le prix d'une seule carte
    
    Args:
        card_id: ID de la carte (ex: sv08_019)
        card_info: Dict avec les infos actuelles de la carte
        api: Instance de TCGdexAPI
        
    Returns:
        (card_id, updated_info) - None si échec
    """
    from datetime import datetime
    
    # Extraire set et number depuis card_id (ex: sv08_019)
    parts = card_id.split('_')
    if len(parts) < 2:
        return card_id, None
    
    set_code = parts[0]  # sv08
    number = parts[1]  # 019
    
    # Récupérer le nom complet du set depuis card_info
    set_name = card_info.get('set', '')  # "Surging Sparks"
    
    try:
        # Rechercher le prix via TCGdex
        price, price_max, details = api.search_card_with_prices(
            card_name=card_info['name'],
            set_name=set_name,  # Passer le nom complet, pas le code
            card_number=number
        )
        
        if price is not None:
            # Créer une copie mise à jour
            updated_info = card_info.copy()
            updated_info['price'] = price
            updated_info['price_max'] = price_max if price_max else price
            updated_info['price_source'] = 'TCGdex'
            updated_info['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            return card_id, updated_info
        else:
            return card_id, None
            
    except Exception as e:
        safe_print(f"Erreur pour {card_id}: {e}")
        return card_id, None


def update_prices_yaml_fast(max_workers: int = 8):
    """
    Met à jour les prix dans le fichier YAML avec requêtes parallèles
    
    Args:
        max_workers: Nombre de threads simultanés (défaut: 8)
                    Ajuster selon votre connexion (4-16 recommandé)
    """
    import yaml
    from datetime import datetime
    from core.tcgdex_api import TCGdexAPI
    import time
    
    yaml_path = Path(PATHS['files']['cards_database_yaml'])
    
    safe_print("=" * 70)
    safe_print("  MISE A JOUR RAPIDE DES PRIX (YAML - Parallele)")
    safe_print("=" * 70)
    safe_print(f"  Workers: {max_workers} requetes simultanees")
    safe_print("=" * 70)
    safe_print("")
    
    # Vérifier que le fichier YAML existe
    if not yaml_path.exists():
        safe_print(f"Fichier YAML non trouve: {yaml_path}")
        safe_print("   Creez d'abord le fichier avec init_prices.py")
        return False
    
    # Lire le YAML
    safe_print(f"Lecture de {yaml_path}...")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        total = len(data['cards'])
        safe_print(f"   OK {total} cartes trouvees")
    except Exception as e:
        safe_print(f"   Erreur lecture YAML: {e}")
        return False
    
    safe_print("")
    
    # Initialiser l'API TCGdex
    safe_print("Initialisation TCGdex API...")
    api = TCGdexAPI(language='en')
    safe_print("   API prete")
    safe_print("")
    
    # Mettre à jour les prix EN PARALLÈLE
    safe_print(f"Mise a jour des prix ({max_workers} workers)...")
    safe_print("   (Cela devrait etre beaucoup plus rapide !)")
    safe_print("")
    
    start_time = time.time()
    success_count = 0
    completed_count = 0
    
    # Créer un pool de threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumettre toutes les tâches
        future_to_card = {
            executor.submit(update_single_card, card_id, card_info, api): card_id
            for card_id, card_info in data['cards'].items()
        }
        
        # Traiter les résultats au fur et à mesure qu'ils arrivent
        for future in as_completed(future_to_card):
            card_id = future_to_card[future]
            completed_count += 1
            
            try:
                result_card_id, updated_info = future.result()
                
                if updated_info:
                    # Mettre à jour dans le dict principal
                    data['cards'][result_card_id] = updated_info
                    price = updated_info.get('price', 'N/A')
                    name = updated_info.get('name', 'Unknown')
                    safe_print(f"[{completed_count}/{total}] {result_card_id} ({name}): OK {price}€")
                    success_count += 1
                else:
                    name = data['cards'][result_card_id].get('name', 'Unknown')
                    safe_print(f"[{completed_count}/{total}] {result_card_id} ({name}): Prix non trouve")
                    
            except Exception as e:
                safe_print(f"[{completed_count}/{total}] {card_id}: Erreur: {e}")
    
    elapsed_time = time.time() - start_time
    
    safe_print("")
    safe_print(f"Temps total: {elapsed_time:.2f}s")
    safe_print(f"   Vitesse: {total/elapsed_time:.1f} cartes/seconde")
    safe_print("")
    
    # Mettre à jour les métadonnées
    data['metadata']['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # Sauvegarder
    safe_print(f"Sauvegarde des prix...")
    try:
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        safe_print(f"   YAML mis a jour!")
    except Exception as e:
        safe_print(f"   Erreur sauvegarde: {e}")
        return False
    
    safe_print("")
    safe_print("=" * 70)
    safe_print("MISE A JOUR RAPIDE TERMINEE!")
    safe_print("=" * 70)
    safe_print("")
    safe_print(f"   {success_count}/{total} cartes avec prix")
    safe_print(f"   Temps: {elapsed_time:.2f}s")
    safe_print(f"   Vitesse: {total/elapsed_time:.1f} cartes/sec")
    safe_print(f"   Fichier: {yaml_path}")
    safe_print("")
    safe_print("Tu peux maintenant utiliser la detection avec prix!")
    safe_print("")
    
    return True


if __name__ == "__main__":
    import argparse
    
    safe_print("")
    
    # Parser les arguments
    parser = argparse.ArgumentParser(description="Mise à jour rapide des prix (parallèle)")
    parser.add_argument('--workers', type=int, default=8,
                       help='Nombre de workers simultanés (défaut: 8, recommandé: 4-16)')
    args = parser.parse_args()
    
    try:
        success = update_prices_yaml_fast(max_workers=args.workers)
        safe_print("")
        
        if success:
            safe_print("Mise a jour reussie!")
        else:
            safe_print("Mise a jour echouee.")
    except KeyboardInterrupt:
        safe_print("\n\nInterruption utilisateur (Ctrl+C)")
        safe_print("   Les prix partiellement mis a jour ont ete sauvegardes.")
    except Exception as e:
        safe_print(f"\nErreur: {e}")
        import traceback
        traceback.print_exc()
    
    safe_print("")
    input("Appuyez sur Entree pour quitter...")
