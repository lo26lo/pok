#!/usr/bin/env python3
"""
Fusionne les images augmentées et les mosaïques dans un dataset YOLO final
Crée train/val split et data.yaml
"""
import shutil
from pathlib import Path
from typing import List, Tuple
import random
import yaml

def copy_files(src_images: Path, src_labels: Path, 
               dst_images: Path, dst_labels: Path) -> int:
    """
    Copie les images et labels d'un dossier source vers destination
    
    Returns:
        Nombre de fichiers copiés
    """
    count = 0
    
    if not src_images.exists():
        print(f"⚠️  {src_images} n'existe pas")
        return 0
    
    for img in src_images.glob("*.png"):
        # Copier image
        shutil.copy2(img, dst_images / img.name)
        
        # Copier label si existe
        label = src_labels / f"{img.stem}.txt"
        if label.exists():
            shutil.copy2(label, dst_labels / label.name)
            count += 1
        else:
            print(f"⚠️  Label manquant pour {img.name}")
    
    return count


def create_train_val_split(images_dir: Path, train_ratio: float = 0.8) -> Tuple[List[str], List[str]]:
    """
    Crée un split train/val
    
    Args:
        images_dir: Dossier contenant les images
        train_ratio: Ratio pour le train (0.8 = 80% train, 20% val)
    
    Returns:
        (train_files, val_files)
    """
    all_images = list(images_dir.glob("*.png"))
    random.shuffle(all_images)
    
    split_idx = int(len(all_images) * train_ratio)
    train_files = all_images[:split_idx]
    val_files = all_images[split_idx:]
    
    # Convertir en chemins relatifs
    train_paths = [f"images/{img.name}" for img in train_files]
    val_paths = [f"images/{img.name}" for img in val_files]
    
    return train_paths, val_paths


def extract_class_info(labels_dir: Path) -> dict:
    """
    Extrait les informations sur les classes depuis les labels YOLO
    
    Returns:
        {class_id: count}
    """
    class_counts = {}
    
    for label_file in labels_dir.glob("*.txt"):
        with open(label_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
    
    return class_counts


def create_data_yaml(dataset_dir: Path, class_names: dict):
    """
    Crée le fichier data.yaml pour YOLO
    
    Args:
        dataset_dir: Dossier du dataset
        class_names: {class_id: class_name}
    """
    max_class_id = max(class_names.keys()) if class_names else 0
    
    # Créer liste de noms avec tous les IDs
    names_list = ["unused"] * (max_class_id + 1)
    for class_id, name in class_names.items():
        names_list[class_id] = name
    
    data = {
        'path': str(dataset_dir.absolute()),
        'train': 'train.txt',
        'val': 'val.txt',
        'nc': max_class_id + 1,
        'names': names_list
    }
    
    yaml_path = dataset_dir / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ data.yaml créé avec {max_class_id + 1} classes")


def merge_dataset():
    """Fonction principale de fusion"""
    print("=" * 70)
    print("📦 FUSION DU DATASET FINAL")
    print("=" * 70)
    print()
    
    # Chemins
    augmented_dir = Path("output/augmented")
    mosaics_dir = Path("output/mosaics")
    dataset_dir = Path("output/dataset")
    
    # Vérifier sources
    if not augmented_dir.exists():
        print(f"❌ {augmented_dir} n'existe pas!")
        return
    
    # Créer structure dataset
    (dataset_dir / "images").mkdir(parents=True, exist_ok=True)
    (dataset_dir / "labels").mkdir(parents=True, exist_ok=True)
    
    print("📁 Structure dataset créée")
    print()
    
    # Copier augmented
    print("📋 Copie des images augmentées...")
    count_aug = copy_files(
        augmented_dir / "images",
        augmented_dir / "labels",
        dataset_dir / "images",
        dataset_dir / "labels"
    )
    print(f"   ✓ {count_aug} images augmentées copiées")
    
    # Copier mosaics (si existe)
    count_mosaic = 0
    if mosaics_dir.exists():
        print("\n🧩 Copie des mosaïques...")
        count_mosaic = copy_files(
            mosaics_dir / "images",
            mosaics_dir / "labels",
            dataset_dir / "images",
            dataset_dir / "labels"
        )
        print(f"   ✓ {count_mosaic} mosaïques copiées")
    else:
        print(f"\n⚠️  {mosaics_dir} n'existe pas (ignoré)")
    
    total = count_aug + count_mosaic
    print(f"\n📊 Total: {total} images dans le dataset")
    
    # Créer train/val split
    print("\n🔀 Création du split train/val...")
    train_files, val_files = create_train_val_split(dataset_dir / "images", train_ratio=0.8)
    
    with open(dataset_dir / "train.txt", "w") as f:
        f.write("\n".join(train_files))
    
    with open(dataset_dir / "val.txt", "w") as f:
        f.write("\n".join(val_files))
    
    print(f"   ✓ Train: {len(train_files)} images ({len(train_files)/total*100:.1f}%)")
    print(f"   ✓ Val: {len(val_files)} images ({len(val_files)/total*100:.1f}%)")
    
    # Analyser classes
    print("\n🔍 Analyse des classes...")
    class_counts = extract_class_info(dataset_dir / "labels")
    
    print(f"   ✓ {len(class_counts)} classes détectées")
    sorted_classes = sorted(class_counts.items())
    for class_id, count in sorted_classes[:10]:  # Afficher top 10
        print(f"      Classe {class_id}: {count} instances")
    
    if len(sorted_classes) > 10:
        print(f"      ... et {len(sorted_classes) - 10} autres classes")
    
    # Créer data.yaml (avec noms de classes si disponible)
    print("\n📝 Création de data.yaml...")
    
    # Essayer de récupérer les noms depuis augmented/data.yaml
    class_names = {}
    augmented_yaml = augmented_dir / "data.yaml"
    if augmented_yaml.exists():
        with open(augmented_yaml, "r") as f:
            aug_data = yaml.safe_load(f)
            if 'names' in aug_data:
                for idx, name in enumerate(aug_data['names']):
                    class_names[idx] = name
    else:
        # Sinon, utiliser IDs
        for class_id in class_counts.keys():
            class_names[class_id] = f"class_{class_id}"
    
    create_data_yaml(dataset_dir, class_names)
    
    print("\n" + "=" * 70)
    print("✅ DATASET FINAL CRÉÉ AVEC SUCCÈS!")
    print("=" * 70)
    print()
    print(f"📂 Emplacement: {dataset_dir.absolute()}")
    print(f"📊 Statistiques:")
    print(f"   - Total images: {total}")
    print(f"   - Train: {len(train_files)}")
    print(f"   - Val: {len(val_files)}")
    print(f"   - Classes: {len(class_counts)}")
    print()
    print("🎓 Prêt pour l'entraînement YOLO:")
    print(f"   yolo train data={dataset_dir / 'data.yaml'} model=yolov8n.pt epochs=50")


if __name__ == "__main__":
    try:
        merge_dataset()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
