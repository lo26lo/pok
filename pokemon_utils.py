#!/usr/bin/env python3
"""
Module utilitaire commun pour le projet Pokemon Dataset
Contient les fonctions partagées pour éviter la duplication de code
"""
import os
import cv2
import pandas as pd
import numpy as np
import re
from glob import glob
from typing import Dict, List, Tuple, Optional

# Correction pour NumPy 2.0 - centralisée ici
np.float_ = np.float64

# Configuration globale
CONFIG = {
    'target_size': (280, 380),
    'excel_file': 'cards_info.xlsx',
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
    
    Args:
        filename: Nom du fichier (ex: "pokemon_en_001_xyz.jpg")
        
    Returns:
        Numéro de carte (ex: "001") ou None si non trouvé
    """
    match = re.search(r'_en_(\d{3})_', filename)
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

if __name__ == "__main__":
    # Tests basiques
    print("Test du module utilitaire...")
    if validate_environment():
        print("Module prêt à être utilisé !")
    else:
        print("Veuillez corriger les problèmes avant d'utiliser le module")