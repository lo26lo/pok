#!/usr/bin/env python3
"""
Workflow complet optimisé GPU pour génération de dataset Pokémon
Utilise tous les scripts optimisés avec support GPU
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Ajouter le parent au path pour importer core
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import safe_print, get_message, load_paths, PATHS, UI_MESSAGES

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat"""
    safe_print(f"\n{'='*70}")
    safe_print(f"⚙️  {description}")
    safe_print(f"{'='*70}")
    
    start = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    duration = time.time() - start
    
    if result.returncode != 0:
        safe_print(f"❌ Échec après {duration:.1f}s")
        return False
    
    safe_print(f"✅ Terminé en {duration:.1f}s")
    return True

def main():
    safe_print("\n" + "="*70)
    safe_print(get_message('console.workflow_start').replace('...', '').upper())
    safe_print("="*70)
    
    # Vérifier environnement
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        safe_print(get_message('console.venv_not_found'))
        sys.exit(1)
    
    python_exe = str(venv_python.absolute())
    
    # Configuration
    num_variations_holo = 3  # Nombre de variations holographiques par carte
    num_augmentations = 50  # Nombre d'augmentations par image holographique
    num_mosaics = 150  # Nombre de mosaïques à générer
    
    safe_print(f"\n📋 Configuration:")
    safe_print(f"   - Variations holographiques : {num_variations_holo}")
    safe_print(f"   - Augmentations par variation : {num_augmentations}")
    safe_print(f"   - Mosaïques : {num_mosaics}")
    
    total_images = 8  # Nombre de cartes source
    total_holo = total_images * num_variations_holo
    total_aug = total_holo * num_augmentations
    total_final = total_aug + num_mosaics
    
    safe_print(f"\n📊 Images attendues:")
    safe_print(f"   - Sources : {total_images}")
    safe_print(f"   - Holographiques : {total_holo}")
    safe_print(f"   - Augmentées : {total_aug}")
    safe_print(f"   - Mosaïques : {num_mosaics}")
    safe_print(f"   - TOTAL DATASET : {total_final}")
    
    # Nettoyage
    safe_print("\n🧹 Nettoyage des dossiers de sortie...")
    for folder in [
        PATHS['directories']['output_holographic'],
        PATHS['directories']['output_augmented'],
        PATHS['directories']['output_mosaics'],
        PATHS['directories']['output_dataset']
    ]:
        if Path(folder).exists():
            import shutil
            shutil.rmtree(folder)
            safe_print(f"   ✓ {folder} supprimé")
    
    # ÉTAPE 1: Augmentation holographique (GPU)
    if not run_command(
        f'{python_exe} core/holographic_augmenter_optimized.py {PATHS["directories"]["images"]} {PATHS["directories"]["output_holographic"]} --variations {num_variations_holo}',
        f"ÉTAPE 1/5 - Augmentation holographique GPU ({num_variations_holo} variations)"
    ):
        return False
    
    # Vérifier sortie
    holo_count = len(list(Path(PATHS['directories']['output_holographic']).glob("*.png")))
    safe_print(f"   📊 {holo_count} images holographiques générées (attendu: {total_holo})")
    
    # ÉTAPE 2: Augmentation standard (depuis images ORIGINALES, pas holo)
    if not run_command(
        f'{python_exe} core/augmentation_albumentations.py --num_aug {num_augmentations} --source images --target augmented',
        f"ÉTAPE 2/5 - Augmentation Albumentations ({num_augmentations} par image)"
    ):
        return False
    
    # Vérifier sortie
    aug_count = len(list(Path(PATHS['directories']['output_augmented_images']).glob("*.png")))
    safe_print(f"   📊 {aug_count} images augmentées générées (attendu: {total_aug})")
    
    # ÉTAPE 3: Génération mosaïques (GPU)
    if not run_command(
        f'{python_exe} core/mosaic_optimized.py 1 1 0 --max-groups {num_mosaics}',
        f"ÉTAPE 3/5 - Génération mosaïques GPU ({num_mosaics} layouts)"
    ):
        return False
    
    # Vérifier sortie
    mosaic_count = len(list(Path(PATHS['directories']['output_mosaics_images']).glob("*.png")))
    safe_print(f"   📊 {mosaic_count} mosaïques générées (attendu: {num_mosaics})")
    
    # ÉTAPE 4: Fusion dataset
    if not run_command(
        f'{python_exe} scripts/merge_dataset.py',
        "ÉTAPE 4/5 - Fusion du dataset final"
    ):
        return False
    
    # Vérifier sortie
    dataset_count = len(list(Path(PATHS['directories']['output_dataset_images']).glob("*.png")))
    safe_print(f"   📊 {dataset_count} images dans le dataset final (attendu: {total_final})")
    
    # ÉTAPE 5: Vérification annotations
    safe_print("\n" + "="*70)
    safe_print("⚙️  ÉTAPE 5/5 - Vérification des annotations YOLO")
    safe_print("="*70)
    
    images_dir = Path(PATHS['directories']['output_dataset_images'])
    labels_dir = Path(PATHS['directories']['output_dataset_labels'])
    
    images = set(f.stem for f in images_dir.glob("*.png"))
    labels = set(f.stem for f in labels_dir.glob("*.txt"))
    
    missing_labels = images - labels
    orphan_labels = labels - images
    
    if missing_labels:
        safe_print(f"⚠️  {len(missing_labels)} images sans labels:")
        for name in list(missing_labels)[:5]:
            safe_print(f"   - {name}")
        if len(missing_labels) > 5:
            safe_print(f"   ... et {len(missing_labels)-5} autres")
    
    if orphan_labels:
        safe_print(f"⚠️  {len(orphan_labels)} labels orphelins:")
        for name in list(orphan_labels)[:5]:
            safe_print(f"   - {name}")
        if len(orphan_labels) > 5:
            safe_print(f"   ... et {len(orphan_labels)-5} autres")
    
    if not missing_labels and not orphan_labels:
        safe_print("✅ Toutes les images ont des labels correspondants!")
    
    # Vérifier contenu labels
    empty_labels = []
    for label_file in labels_dir.glob("*.txt"):
        if label_file.stat().st_size == 0:
            empty_labels.append(label_file.name)
    
    if empty_labels:
        safe_print(f"\n⚠️  {len(empty_labels)} labels vides:")
        for name in empty_labels[:5]:
            safe_print(f"   - {name}")
        if len(empty_labels) > 5:
            safe_print(f"   ... et {len(empty_labels)-5} autres")
    else:
        safe_print("✅ Aucun label vide détecté!")
    
    # Résumé final
    safe_print("\n" + "="*70)
    safe_print(get_message('console.workflow_complete').upper())
    safe_print("="*70)
    safe_print(f"\n📂 Dataset final : {PATHS['directories']['output_dataset']}/")
    safe_print(f"   ├── images/ ({dataset_count} fichiers)")
    safe_print(f"   ├── labels/ ({len(labels)} fichiers)")
    safe_print(f"   ├── train.txt")
    safe_print(f"   ├── val.txt")
    safe_print(f"   └── data.yaml")
    
    safe_print(f"\n🎓 Prêt pour l'entraînement:")
    safe_print(f"   python core/training_manager.py --epochs 50 --batch 16")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
