"""
Mapping entre les noms de classes YOLO et les IDs des cartes
Ce fichier permet de faire le lien entre data.yaml (noms) et Excel (IDs)
"""
import json
from pathlib import Path

try:
    from .utils import PATHS
except ImportError:
    from utils import PATHS

# Cache pour le mapping
_mapping_cache = None

def load_mapping():
    """Charge le mapping depuis le fichier JSON (models/card_name_to_id.json)"""
    global _mapping_cache

    if _mapping_cache is not None:
        return _mapping_cache

    mapping_file = Path(PATHS['files']['card_name_to_id_json'])
    
    if mapping_file.exists():
        with open(mapping_file, 'r', encoding='utf-8') as f:
            _mapping_cache = json.load(f)
            print(f"✅ Mapping chargé: {len(_mapping_cache)} cartes depuis {mapping_file}")
    else:
        # Fallback: mapping hardcodé
        _mapping_cache = {
            "Exeggcute": "sv08_019",
            "Exeggutor": "sv08_020",
            "Scovillain_ex": "sv08_026",
            "Milotic_ex": "sv08_046",
            "Black_Kyurem_ex": "sv08_051",
            "Archaludon_ex": "sv08_126",
            "Alolan_Exeggutor_ex": "sv08_132",
            "Cyrano": "sv08_152",
        }
        print(f"⚠️ Fichier {mapping_file} non trouvé, utilisation du mapping par défaut")
    
    return _mapping_cache


def get_card_id_from_class_name(class_name: str) -> str:
    """
    Obtient l'ID de carte depuis le nom de classe
    
    Args:
        class_name: Nom de la classe (ex: "Exeggcute")
        
    Returns:
        ID de la carte (ex: "sv08_019") ou None si non trouvé
    """
    mapping = load_mapping()
    return mapping.get(class_name)


def get_class_name_from_card_id(card_id: str) -> str:
    """
    Obtient le nom de classe depuis l'ID de carte
    
    Args:
        card_id: ID de la carte (ex: "sv08_019")
        
    Returns:
        Nom de la classe ou None si non trouvé
    """
    mapping = load_mapping()
    # Créer le mapping inverse
    inverse = {v: k for k, v in mapping.items() if v is not None}
    return inverse.get(card_id)
