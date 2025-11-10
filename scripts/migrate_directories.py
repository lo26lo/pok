#!/usr/bin/env python3
"""
Script de migration automatique des répertoires
Réorganise la structure pour plus de clarté et cohérence
"""
import shutil
from pathlib import Path
from datetime import datetime
import json

def backup_current_structure():
    """Crée un backup de la structure actuelle"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_{timestamp}")
    
    print("📦 Création du backup...")
    
    dirs_to_backup = [
        "output",
        "augment",
        "fakeimg",
        "fakeimg_augmented"
    ]
    
    for dir_name in dirs_to_backup:
        src = Path(dir_name)
        if src.exists():
            dst = backup_dir / dir_name
            print(f"   Backup: {src} → {dst}")
            shutil.copytree(src, dst)
    
    print(f"✅ Backup créé: {backup_dir}/")
    return backup_dir


def create_new_structure():
    """Crée la nouvelle structure de répertoires"""
    print("\n📁 Création de la nouvelle structure...")
    
    new_dirs = [
        "backgrounds/original",
        "backgrounds/augmented",
        "output/holographic/images",
        "output/holographic/labels",
        "output/augmented/images",
        "output/augmented/labels",
        "output/mosaics/images",
        "output/mosaics/labels",
        "output/dataset/images",
        "output/dataset/labels"
    ]
    
    for dir_path in new_dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}/")
    
    print("✅ Structure créée")


def migrate_data():
    """Migre les données vers la nouvelle structure"""
    print("\n🔄 Migration des données...")
    
    migrations = []
    
    # 1. Backgrounds
    if Path("fakeimg").exists():
        migrations.append(("fakeimg", "backgrounds/original"))
    
    if Path("fakeimg_augmented").exists():
        migrations.append(("fakeimg_augmented", "backgrounds/augmented"))
    
    # 2. Holographic (augment/ → output/holographic/)
    if Path("augment").exists():
        augment_imgs = list(Path("augment").glob("*.png"))
        if augment_imgs:
            migrations.append(("augment", "output/holographic/images"))
            # Créer labels si nécessaire
            for img in augment_imgs:
                label_path = Path("output/holographic/labels") / f"{img.stem}.txt"
                if not label_path.exists():
                    # Créer un label par défaut (classe 0, bbox full)
                    with open(label_path, "w") as f:
                        f.write("0 0.5 0.5 1.0 1.0\n")
    
    # 3. Augmented (déjà dans output/augmented/, vérifier structure)
    augmented_src = Path("output/augmented/images")
    if augmented_src.exists():
        print("   ✓ output/augmented/ déjà en place")
    
    # 4. Mosaics (séparer de yolov8/)
    yolov8_imgs = Path("output/yolov8/images")
    if yolov8_imgs.exists():
        # Copier les mosaics (layout_*.png)
        mosaic_imgs = list(yolov8_imgs.glob("layout_*.png"))
        if mosaic_imgs:
            print(f"   Migration: {len(mosaic_imgs)} mosaïques → output/mosaics/")
            for img in mosaic_imgs:
                dst = Path("output/mosaics/images") / img.name
                shutil.copy2(img, dst)
                
                # Copier le label correspondant
                label_src = Path("output/yolov8/labels") / f"{img.stem}.txt"
                if label_src.exists():
                    label_dst = Path("output/mosaics/labels") / label_src.name
                    shutil.copy2(label_src, label_dst)
    
    # Exécuter migrations
    for src, dst in migrations:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if src_path.exists():
            print(f"   Migration: {src} → {dst}")
            
            if dst_path.exists():
                # Fusionner
                for item in src_path.iterdir():
                    shutil.move(str(item), str(dst_path / item.name))
            else:
                # Déplacer tout
                shutil.move(str(src_path), str(dst_path))
    
    print("✅ Migration terminée")


def update_config():
    """Met à jour gui_config.json"""
    print("\n⚙️ Mise à jour de gui_config.json...")
    
    config_path = Path("gui_config.json")
    
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    # Mettre à jour les chemins
    config["paths"] = {
        "images_source": "images",
        "backgrounds": "backgrounds",
        "backgrounds_augmented": "backgrounds/augmented",
        "output_holographic": "output/holographic",
        "output_augmented": "output/augmented",
        "output_mosaics": "output/mosaics",
        "output_dataset": "output/dataset",
        "excel_file": config.get("paths", {}).get("excel_file", "excel/cards_info.xlsx")
    }
    
    # Mettre à jour les defaults
    if "defaults" not in config:
        config["defaults"] = {}
    
    config["defaults"].update({
        "holographic_dir": "output/holographic",
        "augmented_dir": "output/augmented",
        "mosaic_dir": "output/mosaics",
        "dataset_dir": "output/dataset",
        "backgrounds_dir": "backgrounds",
        "backgrounds_augmented_dir": "backgrounds/augmented"
    })
    
    # Sauvegarder
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)
    
    print("✅ Configuration mise à jour")


def cleanup_old_structure():
    """Nettoie l'ancienne structure (optionnel)"""
    print("\n🧹 Nettoyage de l'ancienne structure...")
    
    dirs_to_remove = [
        "output/yolov8_test",
        "fakeimg",
        "fakeimg_augmented",
        "augment"
    ]
    
    for dir_name in dirs_to_remove:
        path = Path(dir_name)
        if path.exists():
            print(f"   Suppression: {dir_name}/")
            shutil.rmtree(path)
    
    print("✅ Nettoyage terminé")


def generate_report():
    """Génère un rapport de la nouvelle structure"""
    print("\n📊 Génération du rapport...")
    
    report = []
    report.append("=" * 60)
    report.append("RAPPORT DE MIGRATION")
    report.append("=" * 60)
    report.append("")
    
    # Compter fichiers par répertoire
    dirs_to_check = [
        "images",
        "backgrounds/original",
        "backgrounds/augmented",
        "output/holographic/images",
        "output/augmented/images",
        "output/mosaics/images",
        "output/dataset/images"
    ]
    
    for dir_path in dirs_to_check:
        path = Path(dir_path)
        if path.exists():
            count = len(list(path.glob("*.*")))
            report.append(f"{dir_path:<40} {count:>5} fichiers")
        else:
            report.append(f"{dir_path:<40} {'N/A':>5}")
    
    report.append("")
    report.append("=" * 60)
    
    report_text = "\n".join(report)
    print(report_text)
    
    # Sauvegarder rapport
    with open("migration_report.txt", "w") as f:
        f.write(report_text)
    
    print("\n💾 Rapport sauvegardé: migration_report.txt")


def main():
    """Fonction principale de migration"""
    print("=" * 70)
    print("🔧 MIGRATION AUTOMATIQUE DES RÉPERTOIRES")
    print("=" * 70)
    print()
    print("Ce script va réorganiser la structure des dossiers pour plus de clarté.")
    print()
    
    response = input("Continuer ? (o/n) : ").strip().lower()
    if response != 'o':
        print("❌ Migration annulée")
        return
    
    try:
        # 1. Backup
        backup_dir = backup_current_structure()
        
        # 2. Créer nouvelle structure
        create_new_structure()
        
        # 3. Migrer les données
        migrate_data()
        
        # 4. Mettre à jour config
        update_config()
        
        # 5. Nettoyer (optionnel)
        response = input("\nSupprimer l'ancienne structure ? (o/n) : ").strip().lower()
        if response == 'o':
            cleanup_old_structure()
        
        # 6. Rapport
        generate_report()
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 70)
        print()
        print(f"📦 Backup disponible: {backup_dir}/")
        print("📊 Rapport: migration_report.txt")
        print()
        print("⚠️  IMPORTANT: Mettre à jour les scripts core/ et GUI!")
        print("   Voir ANALYSE_REPERTOIRES.md pour la liste complète")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        print("\n📦 Backup disponible pour restauration")


if __name__ == "__main__":
    main()
