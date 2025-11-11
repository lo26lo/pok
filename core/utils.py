#!/usr/bin/env python3
"""
Module utilitaire commun pour le projet Pokemon Dataset
Contient les fonctions partagées pour éviter la duplication de code
"""
import os
import sys
import cv2
import pandas as pd
import numpy as np
import re
from glob import glob
from typing import Dict, List, Tuple, Optional

# Correction pour NumPy 2.0 - centralisée ici
np.float_ = np.float64

# Compiled regex patterns for card number extraction (performance optimization)
_PATTERN_NEW_FORMAT = re.compile(r'_([A-Za-z0-9]+)_[a-z]{2}\.')
_PATTERN_OLD_FORMAT = re.compile(r'_(?:en_)?(\d{3})_', re.IGNORECASE)
_PATTERN_FALLBACK_1 = re.compile(r'_(\w+)_')
_PATTERN_FALLBACK_2 = re.compile(r'(\d{3})')


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

def load_card_data(excel_path: str = None) -> Tuple[Dict[str, str], Dict[str, int]]:
    """
    Charge les données des cartes depuis le fichier Excel
    
    Args:
        excel_path: Chemin vers le fichier Excel (par défaut CONFIG['excel_file'])
        
    Returns:
        Tuple contenant (card_dict, class_map)
        
    Raises:
        FileNotFoundError: Si le fichier Excel n'existe pas
        pandas.errors.EmptyDataError: Si le fichier est vide
    """
    if excel_path is None:
        excel_path = CONFIG['excel_file']
        
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Fichier Excel non trouvé : {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, usecols=["Set #", "Name"])
    except Exception as e:
        raise pd.errors.EmptyDataError(f"Erreur lors de la lecture du fichier Excel : {e}")
    
    card_dict = {}
    class_map = {}
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
    - xyp_XY05_en.png → "XY05"
    - SSP_001_R_EN_SM.png → "001"
    - pokemon_en_001_xyz.jpg → "001"
    
    Args:
        filename: Nom du fichier
        
    Returns:
        Numéro de carte ou None si non trouvé
    """
    # Format nouveau: {set}_{number}_{lang}.ext
    match = _PATTERN_NEW_FORMAT.search(filename)
    if match:
        num = match.group(1)
        # Padder si numérique pur
        return num.zfill(3) if num.isdigit() else num
    
    # Format ancien: _en_XXX_ ou _XXX_
    match = _PATTERN_OLD_FORMAT.search(filename)
    if match:
        return match.group(1)
    
    # Fallback: XXX_XXX_XXX
    match = _PATTERN_FALLBACK_1.search(filename)
    if match and re.match(r'\d{3}', match.group(1)):
        return match.group(1)
    
    # Dernier recours
    match = _PATTERN_FALLBACK_2.search(filename)
    return match.group(1) if match else None

def resize_cards(image_paths: List[str], target_size: Tuple[int, int] = None) -> List[Tuple[np.ndarray, str]]:
    """
    Redimensionne les images aux dimensions cibles
    
    Args:
        image_paths: Liste des chemins d'images
        target_size: Taille cible (largeur, hauteur)
        
    Returns:
        Liste de tuples (image_redimensionnée, chemin_original)
    """
    if target_size is None:
        target_size = CONFIG['target_size']
    
    resized_images = []
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"Attention: Image non trouvée : {img_path}")
            continue
            
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Attention: Impossible de charger l'image : {img_path}")
            continue
            
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

def load_prices_from_excel(excel_path: str = "excel/cards_info.xlsx") -> Dict[str, Dict[str, any]]:
    """
    Charge les informations de prix depuis le fichier Excel
    
    Args:
        excel_path: Chemin vers le fichier Excel
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
        
    Example:
        >>> prices = load_prices_from_excel()
        >>> print(prices['sv08_019'])
        {'name': 'Exeggcute', 'price': 0.15, 'price_max': 0.25}
    """
    if not os.path.exists(excel_path):
        safe_print(f"⚠️ Fichier Excel non trouvé: {excel_path}")
        return {}
    
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        
        prices_dict = {}
        
        for _, row in df.iterrows():
            # Récupérer les informations
            card_id = row.get('Set #', '')  # ex: sv08_019
            name = row.get('Name', 'Unknown')
            prix = row.get('Prix', None)
            prix_max = row.get('Prix max', None)
            
            # Nettoyer le card_id
            if isinstance(card_id, str):
                card_id = card_id.strip()
            else:
                card_id = str(card_id)
            
            # Convertir les prix en float
            try:
                prix = float(prix) if prix is not None and not pd.isna(prix) else None
            except (ValueError, TypeError):
                prix = None
                
            try:
                prix_max = float(prix_max) if prix_max is not None and not pd.isna(prix_max) else None
            except (ValueError, TypeError):
                prix_max = None
            
            # Stocker dans le dictionnaire
            if card_id:
                prices_dict[card_id] = {
                    'name': name,
                    'price': prix,
                    'price_max': prix_max
                }
        
        safe_print(f"✅ Chargé {len(prices_dict)} cartes avec prix depuis {excel_path}")
        return prices_dict
        
    except Exception as e:
        safe_print(f"❌ Erreur lors du chargement de {excel_path}: {e}")
        return {}


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


def load_prices(yaml_path: str = "models/cards_database.yaml", 
                excel_path: str = "excel/cards_info.xlsx") -> Dict[str, Dict[str, any]]:
    """
    Charge les prix depuis YAML (prioritaire) ou Excel (fallback)
    
    Args:
        yaml_path: Chemin vers le fichier YAML
        excel_path: Chemin vers le fichier Excel (fallback)
        
    Returns:
        Dictionnaire {card_id: {'name': str, 'price': float, 'price_max': float}}
    """
    # Priorité 1: YAML
    if os.path.exists(yaml_path):
        safe_print(f"📄 Utilisation de {yaml_path}")
        return load_prices_from_yaml(yaml_path)
    
    # Fallback: Excel
    if os.path.exists(excel_path):
        safe_print(f"📊 Fallback vers {excel_path}")
        return load_prices_from_excel(excel_path)
    
    safe_print("⚠️ Aucun fichier de prix trouvé (ni YAML ni Excel)")
    return {}


if __name__ == "__main__":
    # Tests basiques
    print("Test du module utilitaire...")
    if validate_environment():
        print("Module prêt à être utilisé !")
    else:
        print("Veuillez corriger les problèmes avant d'utiliser le module")