#!/usr/bin/env python3
"""
Module utilitaire commun pour le projet Pokemon Dataset
Contient les fonctions partagées pour éviter la duplication de code

Ce module centralise:
- Patches de compatibilité NumPy (pour imgaug)
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
import pandas as pd
import numpy as np
import re
from glob import glob
from typing import Dict, List, Tuple, Optional

# ==================== NumPy Compatibility Patches ====================
# Patch de compatibilité NumPy 2.0 pour imgaug
# Ces patches doivent être appliqués AVANT l'import de imgaug
np.float_ = np.float64

# Patches additionnels pour compatibilité complète
if not hasattr(np, 'bool'):
    np.bool = np.bool_
if not hasattr(np, 'int'):
    np.int = np.int_
if not hasattr(np, 'float'):
    np.float = np.float64
if not hasattr(np, 'complex'):
    np.complex = np.complex128
if not hasattr(np, 'object'):
    np.object = np.object_
if not hasattr(np, 'str'):
    np.str = np.str_

# ==================== Regex Patterns ====================
# Compiled regex patterns for card number extraction (performance optimization)
# Ces patterns sont partagés par tous les modules
PATTERN_NEW_FORMAT = re.compile(r'_([A-Za-z0-9]+)_[a-z]{2}(?:_aug_\d+)?\.')
PATTERN_OLD_FORMAT = re.compile(r'_(?:en_)?(\d{3})_', re.IGNORECASE)
PATTERN_FALLBACK_1 = re.compile(r'_(\w+)_')
PATTERN_FALLBACK_2 = re.compile(r'(\d{3})')

# Legacy names for backward compatibility (deprecated)
_PATTERN_NEW_FORMAT = PATTERN_NEW_FORMAT
_PATTERN_OLD_FORMAT = PATTERN_OLD_FORMAT
_PATTERN_FALLBACK_1 = PATTERN_FALLBACK_1
_PATTERN_FALLBACK_2 = PATTERN_FALLBACK_2


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
    'excel_file': 'excel/cards_info.xlsx',
    'base_images_dir': 'images',
    'augmented_dir': 'images_aug',
    'output_dir': 'output',
    'yolo_format': True
}

def load_card_data(source_path: str = None) -> Tuple[Dict[str, str], Dict[str, int]]:
    """
    Charge les données des cartes depuis YAML (prioritaire) ou Excel (fallback)
    
    Supporte deux formats:
    - YAML: models/cards_database.yaml (nouveau format recommandé)
    - Excel: excel/cards_info.xlsx (legacy, rétrocompatibilité)
    
    Args:
        source_path: Chemin vers le fichier (YAML ou Excel). 
                    Si None, utilise CONFIG['excel_file']
                    
    Returns:
        Tuple contenant (card_dict, class_map)
        - card_dict: {card_number: card_name}
        - class_map: {card_number: class_id}
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
        Exception: Si erreur lors de la lecture
        
    Example:
        >>> card_dict, class_map = load_card_data("models/cards_database.yaml")
        >>> print(card_dict["019"])
        'Ho-Oh'
        >>> print(class_map["019"])
        19
    """
    if source_path is None:
        source_path = CONFIG['excel_file']
        
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
        
        class_id = 1
        for card_id, card_info in data['cards'].items():
            # Extraire le numéro (ex: sv08_019 -> 019)
            number = card_id.split('_')[-1].zfill(3)
            name = card_info['name'].replace(" ", "_")
            
            if number not in card_dict:
                card_dict[number] = name
                class_map[number] = class_id
                class_id += 1
    else:
        # Charger depuis Excel (legacy)
        try:
            df = pd.read_excel(source_path, usecols=["Set #", "Name"])
        except Exception as e:
            raise Exception(f"Erreur lors de la lecture du fichier Excel : {e}")
        
        class_id = 1
        for _, row in df.iterrows():
            number = row["Set #"].split('/')[0].zfill(3)
            name = row["Name"].replace(" ", "_")
            if number not in card_dict:
                card_dict[number] = name
                class_map[number] = class_id
                class_id += 1
    
    return card_dict, class_map

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

def load_prices_from_yaml(yaml_path: str = "models/cards_database.yaml") -> Dict[str, Dict[str, any]]:
    """
    Charge les informations de prix depuis le fichier YAML
    
    Args:
        yaml_path: Chemin vers le fichier YAML
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
        
    Example:
        >>> prices = load_prices_from_yaml()
        >>> print(prices['sv08_019'])
        {'name': 'Ho-Oh', 'price': 0.15, 'price_max': 0.25}
    """
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


def load_prices(yaml_path: str = "models/cards_database.yaml") -> Dict[str, Dict[str, any]]:
    """
    Charge les prix depuis YAML
    
    Args:
        yaml_path: Chemin vers le fichier YAML
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
    """
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