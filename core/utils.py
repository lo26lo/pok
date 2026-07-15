#!/usr/bin/env python3
"""
Module utilitaire commun pour le projet Pokemon Dataset
Contient les fonctions partagées pour éviter la duplication de code

Ce module centralise:
- Patterns regex pour extraction de numéros de cartes
- Fonctions utilitaires communes (load_card_data, extract_card_number, resize_cards)
- Configuration globale du projet

Usage:
    from core.utils import (
        safe_print,
        extract_card_number,
        load_card_data,
        resize_cards,
        CONFIG
    )
"""
import os
import sys
import cv2
import numpy as np
import re
import json
from pathlib import Path
from glob import glob
from typing import Dict, List, Tuple, Optional

# pandas n'est importé qu'à la demande (branche Excel legacy de load_card_data).
# Import paresseux volontaire: le pipeline par défaut utilise YAML, donc un
# pandas absent OU cassé (ex: mismatch ABI numpy/pandas) ne doit pas empêcher
# le GUI et tout le reste de démarrer.

# ==================== Regex Patterns ====================
# Compiled regex patterns for card number extraction (performance optimization)
# Ces patterns sont partagés par tous les modules
PATTERN_NEW_FORMAT = re.compile(r'_([A-Za-z0-9]+)_[a-z]{2}(?:_holo\d+)?(?:_aug_\d+)?\.')
PATTERN_OLD_FORMAT = re.compile(r'_(?:en_)?(\d{3})_', re.IGNORECASE)
PATTERN_FALLBACK_1 = re.compile(r'_(\w+)_')
PATTERN_FALLBACK_2 = re.compile(r'(\d{3})')


# ==================== PATHS CONFIGURATION ====================
def load_paths() -> Dict:
    """
    Load centralized paths from config/paths.json
    NO HELPER - Direct JSON loading
    """
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to default paths if file doesn't exist
        return {
            "directories": {
                "images": "images",
                "excel": "excel",
                "models": "models",
                "output_base": "output"
            },
            "files": {
                "cards_info_excel": "excel/cards_info.xlsx",
                "cards_database_yaml": "models/cards_database.yaml"
            }
        }

# Load paths at module import
PATHS = load_paths()
# ============================================================


# ==================== UI MESSAGES CONFIGURATION ====================
def load_ui_messages(language: str = 'fr') -> Dict:
    """
    Load centralized UI messages from config/ui_messages[_LANG].json
    NO HELPER - Direct JSON loading
    
    Args:
        language: Language code ('fr', 'en', 'es', etc.)
    
    Returns:
        Dictionary with all UI messages
    """
    # Try language-specific file first
    if language != 'fr':
        config_path = Path(__file__).parent.parent / "config" / f"ui_messages_{language}.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass  # Fallback to French
    
    # Default: French version
    config_path = Path(__file__).parent.parent / "config" / "ui_messages.json"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English messages if file doesn't exist
        return {
            "console": {
                "download_start": "Downloading images...",
                "download_complete": "Download complete!",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                "success": "Success"
            },
            "gui": {
                "title": "Pokémon Dataset Generator",
                "labels": {},
                "buttons": {},
                "status": {}
            }
        }

# Load UI messages at module import
UI_MESSAGES = load_ui_messages()
# ============================================================


def get_message(key_path: str, **kwargs) -> str:
    """
    Get UI message by dot-separated key path with optional formatting
    
    Examples:
        get_message('console.download_start')
        get_message('console.download_success', ok=10, total=15)
        get_message('gui.buttons.start_download')
    """
    keys = key_path.split('.')
    value = UI_MESSAGES
    
    try:
        for key in keys:
            value = value[key]
        
        # Format if kwargs provided and value is string
        if kwargs and isinstance(value, str):
            return value.format(**kwargs)
        return value
    except (KeyError, TypeError):
        # Fallback if key not found
        return key_path


def safe_print(*args, **kwargs):
    """
    Print avec gestion d'encodage pour Windows
    Évite les erreurs UnicodeEncodeError avec les emojis sur console Windows
    Accepte les mêmes arguments que print()
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: retirer les emojis et caractères non-ASCII
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', 'ignore').decode('ascii'))
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)


# Configuration globale
CONFIG = {
    'target_size': (280, 380),
    'excel_file': PATHS['files']['cards_info_excel'],
    'base_images_dir': PATHS['directories']['images'],
    'augmented_dir': 'images_aug',  # Legacy, will be removed
    'output_dir': PATHS['directories']['output_base'],
    'yolo_format': True
}

def load_card_data(source_path: str = None) -> Tuple[Dict[str, str], Dict[str, int]]:
    """
    Charge les données des cartes depuis YAML (prioritaire) ou Excel (fallback)

    ⚠️ SOURCE UNIQUE DE VÉRITÉ pour le mapping de classes YOLO.
    Les class_id sont 0-indexés (standard YOLO) et suivent l'ordre de
    déclaration des cartes dans le fichier source. Tous les modules
    (augmentation, mosaïques, merge) doivent passer par cette fonction.

    Supporte deux formats:
    - YAML: models/cards_database.yaml (nouveau format recommandé)
    - Excel: excel/cards_info.xlsx (legacy, rétrocompatibilité)

    Args:
        source_path: Chemin vers le fichier (YAML ou Excel).
                    Si None, utilise PATHS['files']['cards_database_yaml']

    Returns:
        Tuple contenant (card_dict, class_map)
        - card_dict: {clé: card_name}
        - class_map: {clé: class_id} (0-indexed)
        Pour le format YAML, chaque carte est indexée sous DEUX clés:
        l'identifiant complet (ex: "sv08_019") ET le numéro court (ex: "019"),
        toutes deux associées au même class_id.

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        Exception: Si erreur lors de la lecture

    Example:
        >>> card_dict, class_map = load_card_data("models/cards_database.yaml")
        >>> class_map["sv08_019"] == class_map["019"]
        True
    """
    if source_path is None:
        source_path = PATHS['files']['cards_database_yaml']

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Fichier non trouvé : {source_path}")

    card_dict = {}
    class_map = {}

    # Détection automatique du format
    if source_path.endswith('.yaml') or source_path.endswith('.yml'):
        # Charger depuis YAML
        import yaml

        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier YAML : {e}")

        if 'cards' not in data:
            raise Exception(f"Structure YAML invalide (clé 'cards' manquante)")

        for class_id, (card_id, card_info) in enumerate(data['cards'].items()):
            name = card_info['name'].replace(" ", "_")

            # Clé 1: identifiant complet (ex: "sv08_019")
            if card_id not in card_dict:
                card_dict[card_id] = name
                class_map[card_id] = class_id

            # Clé 2: numéro court (ex: "019"), padder si numérique
            number = card_id.split('_')[-1] if '_' in card_id else card_id
            if number.isdigit():
                number = number.zfill(3)
            if number not in card_dict:
                card_dict[number] = name
                class_map[number] = class_id
    else:
        # Charger depuis Excel (legacy) — pandas importé ici seulement
        try:
            import pandas as pd
            df = pd.read_excel(source_path, usecols=["Set #", "Name"])
        except ImportError:
            raise Exception(
                "pandas est requis pour lire un fichier Excel (format legacy). "
                "Installez-le (pip install pandas openpyxl) ou utilisez le "
                "format YAML (models/cards_database.yaml).")
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier Excel : {e}")

        class_id = 0
        for _, row in df.iterrows():
            number = str(row["Set #"]).split('/')[0].zfill(3)
            name = str(row["Name"]).replace(" ", "_")
            if number not in card_dict:
                card_dict[number] = name
                class_map[number] = class_id
                class_id += 1

    return card_dict, class_map


def build_class_names_list(card_dict: Dict[str, str], class_map: Dict[str, int]) -> List[str]:
    """
    Construit la liste des noms de classes ordonnée par class_id (pour data.yaml)

    Args:
        card_dict: {clé: card_name} retourné par load_card_data
        class_map: {clé: class_id} retourné par load_card_data

    Returns:
        Liste de noms indexée par class_id (les IDs sans carte → "unused")
    """
    if not class_map:
        return []
    names = ["unused"] * (max(class_map.values()) + 1)
    for key, class_id in class_map.items():
        names[class_id] = card_dict[key]
    return names

def extract_card_number(filename: str) -> Optional[str]:
    """
    Extrait le numéro de carte depuis le nom de fichier
    
    Supporte plusieurs formats:
    - sv08_001_en.png → "001"
    - sv08_001_en_aug_042.png → "001" (avec augmentation)
    - xyp_XY05_en.png → "XY05"
    - SSP_001_R_EN_SM.png → "001"
    - pokemon_en_001_xyz.jpg → "001"
    - card_001.jpg → "001"
    
    Args:
        filename: Nom du fichier (avec ou sans chemin)
        
    Returns:
        Numéro de carte ou None si non trouvé
        
    Example:
        >>> extract_card_number("sv08_019_en.png")
        '019'
        >>> extract_card_number("sv08_019_en_aug_042.png")
        '019'
        >>> extract_card_number("xyp_XY05_en.png")
        'XY05'
    """
    # Format nouveau: {set}_{number}_{lang}.ext (supporte aussi _aug_XXX)
    match = PATTERN_NEW_FORMAT.search(filename)
    if match:
        num = match.group(1)
        # Padder si numérique pur
        return num.zfill(3) if num.isdigit() else num
    
    # Format ancien: _en_XXX_ ou _XXX_
    match = PATTERN_OLD_FORMAT.search(filename)
    if match:
        return match.group(1)
    
    # Fallback: XXX_XXX_XXX
    match = PATTERN_FALLBACK_1.search(filename)
    if match and re.match(r'\d{3}', match.group(1)):
        return match.group(1)
    
    # Dernier recours
    match = PATTERN_FALLBACK_2.search(filename)
    return match.group(1) if match else None

def resize_cards(image_paths: List[str], target_size: Tuple[int, int] = None) -> List[Tuple[np.ndarray, str]]:
    """
    Redimensionne les images aux dimensions cibles
    
    Gère automatiquement la conversion RGBA → RGB si nécessaire
    
    Args:
        image_paths: Liste des chemins d'images
        target_size: Taille cible (largeur, hauteur). 
                    Si None, utilise CONFIG['target_size']
        
    Returns:
        Liste de tuples (image_redimensionnée, chemin_original)
        
    Example:
        >>> paths = ["image1.png", "image2.jpg"]
        >>> resized = resize_cards(paths, (280, 380))
        >>> for img, path in resized:
        ...     print(f"{path}: {img.shape}")
    """
    if target_size is None:
        target_size = CONFIG['target_size']
    
    resized_images = []
    for img_path in image_paths:
        if not os.path.exists(img_path):
            safe_print(f"Attention: Image non trouvée : {img_path}")
            continue
            
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            safe_print(f"Attention: Impossible de charger l'image : {img_path}")
            continue
        
        # Convertir RGBA en RGB si nécessaire
        if len(img.shape) == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        resized_images.append((img, img_path))
    
    return resized_images

def ensure_directories(*directories: str) -> None:
    """
    Crée les répertoires s'ils n'existent pas
    
    Args:
        *directories: Chemins des répertoires à créer
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def get_image_paths(directory: str, extensions: List[str] = None) -> List[str]:
    """
    Récupère tous les chemins d'images dans un répertoire
    
    Args:
        directory: Répertoire à scanner
        extensions: Extensions de fichiers à inclure
        
    Returns:
        Liste des chemins d'images
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob(os.path.join(directory, f"*{ext}")))
        image_paths.extend(glob(os.path.join(directory, f"*{ext.upper()}")))
    
    return sorted(image_paths)

def validate_environment() -> bool:
    """
    Valide que l'environnement est correctement configuré
    
    Returns:
        True si l'environnement est valide
    """
    issues = []
    
    # Vérifier les répertoires essentiels
    if not os.path.exists(CONFIG['base_images_dir']):
        issues.append(f"Répertoire d'images manquant : {CONFIG['base_images_dir']}")
    
    # Vérifier le fichier Excel
    if not os.path.exists(CONFIG['excel_file']):
        issues.append(f"Fichier Excel manquant : {CONFIG['excel_file']}")
    
    if issues:
        print("❌ Problèmes détectés dans l'environnement :")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    print("✅ Environnement validé avec succès")
    return True

def clean_old_files(pattern: str, directory: str = ".") -> int:
    """
    Nettoie les anciens fichiers selon un pattern
    
    Args:
        pattern: Pattern des fichiers à supprimer
        directory: Répertoire à nettoyer
        
    Returns:
        Nombre de fichiers supprimés
    """
    files_to_remove = glob(os.path.join(directory, pattern))
    count = 0
    
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            count += 1
        except Exception as e:
            print(f"Erreur lors de la suppression de {file_path}: {e}")
    
    return count

def load_prices_from_yaml(yaml_path: str = None) -> Dict[str, Dict[str, any]]:
    """
    Charge les informations de prix depuis le fichier YAML
    
    Args:
        yaml_path: Chemin vers le fichier YAML (default: from paths.json)
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
        
    Example:
        >>> prices = load_prices_from_yaml()
        >>> print(prices['sv08_019'])
        {'name': 'Ho-Oh', 'price': 0.15, 'price_max': 0.25}
    """
    if yaml_path is None:
        yaml_path = PATHS['files']['cards_database_yaml']
    
    if not os.path.exists(yaml_path):
        safe_print(f"⚠️ Fichier YAML non trouvé: {yaml_path}")
        return {}
    
    try:
        import yaml
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        prices_dict = {}
        
        # Vérifier que la structure est valide
        if not data or 'cards' not in data:
            safe_print(f"⚠️ Structure YAML invalide dans {yaml_path}")
            return {}
        
        # Parcourir les cartes
        for card_id, card_info in data['cards'].items():
            name = card_info.get('name', 'Unknown')
            prix = card_info.get('price')
            prix_max = card_info.get('price_max')
            
            # Stocker dans le dictionnaire
            prices_dict[card_id] = {
                'name': name,
                'price': prix,
                'price_max': prix_max
            }
        
        safe_print(f"✅ Chargé {len(prices_dict)} cartes avec prix depuis {yaml_path}")
        return prices_dict
        
    except Exception as e:
        safe_print(f"❌ Erreur lors du chargement de {yaml_path}: {e}")
        return {}


def load_prices(yaml_path: str = None) -> Dict[str, Dict[str, any]]:
    """
    Charge les prix depuis YAML
    
    Args:
        yaml_path: Chemin vers le fichier YAML (default: from paths.json)
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
    """
    if yaml_path is None:
        yaml_path = PATHS['files']['cards_database_yaml']

    if os.path.exists(yaml_path):
        safe_print(f"📄 Chargement de {yaml_path}")
        return load_prices_from_yaml(yaml_path)

    safe_print(f"⚠️ Fichier YAML non trouvé: {yaml_path}")
    return {}


if __name__ == "__main__":
    # Tests basiques
    print("Test du module utilitaire...")
    if validate_environment():
        print("Module prêt à être utilisé !")
    else:
        print("Veuillez corriger les problèmes avant d'utiliser le module")