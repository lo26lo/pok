#!/usr/bin/env python3
"""
Corrige le mapping des class_id pour correspondre à nos 8 cartes uniquement
"""
from pathlib import Path
import yaml
import shutil

def fix_class_mapping():
    """Remappe les class_id de l'index global (0-251) vers l'index local (0-7)"""
    
    # Mapping des cartes: numéro de carte -> index local
    # Basé sur les noms de fichiers sv08_XXX_fr.png
    card_mapping = {
        19: 0,   # sv08_019 -> Ho-Oh
        20: 1,   # sv08_020 -> Castform_Sunny_Form
        26: 2,   # sv08_026 -> Dipplin
        46: 3,   # sv08_046 -> Gliscor
        51: 4,   # sv08_051 -> Drapion
        126: 5,  # sv08_126 -> Thwackey
        132: 6,  # sv08_132 -> Quaquaval
        152: 7   # sv08_152 -> Munkidori
    }
    
    # Charger le data.yaml original pour récupérer les noms
    dataset_dir = Path("output/dataset")
    data_yaml_path = dataset_dir / "data.yaml"
    
    with open(data_yaml_path, 'r', encoding='utf-8') as f:
        original_data = yaml.safe_load(f)
    
    # Extraire uniquement les noms de nos 8 cartes
    all_names = original_data['names']
    our_card_names = [all_names[card_num] for card_num in sorted(card_mapping.keys())]
    
    print("="*70)
    print("🔧 CORRECTION DU MAPPING DES CLASS_ID")
    print("="*70)
    print(f"\n📋 Mapping des cartes:")
    for old_id, new_id in sorted(card_mapping.items(), key=lambda x: x[1]):
        print(f"   Class {old_id:3d} -> Class {new_id} ({all_names[old_id]})")
    
    # Sauvegarder l'ancien data.yaml
    backup_path = dataset_dir / "data.yaml.backup"
    shutil.copy(data_yaml_path, backup_path)
    print(f"\n💾 Backup créé: {backup_path}")
    
    # Créer le nouveau data.yaml avec seulement 8 classes
    new_data = {
        'path': str(dataset_dir.absolute()),
        'train': 'train.txt',
        'val': 'val.txt',
        'nc': 8,
        'names': our_card_names
    }
    
    with open(data_yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(new_data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n✅ Nouveau data.yaml créé avec {len(our_card_names)} classes:")
    for i, name in enumerate(our_card_names):
        print(f"   {i}: {name}")
    
    # Remapper tous les labels
    labels_dir = dataset_dir / "labels"
    labels_fixed = 0
    labels_errors = []
    
    print(f"\n🔄 Remapping des labels...")
    for label_file in labels_dir.glob("*.txt"):
        try:
            with open(label_file, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                
                old_class_id = int(parts[0])
                
                # Remapper le class_id
                if old_class_id in card_mapping:
                    new_class_id = card_mapping[old_class_id]
                    new_line = f"{new_class_id} {' '.join(parts[1:])}\n"
                    new_lines.append(new_line)
                else:
                    labels_errors.append((label_file.name, old_class_id))
            
            # Écrire le fichier corrigé
            with open(label_file, 'w') as f:
                f.writelines(new_lines)
            
            labels_fixed += 1
            
            if labels_fixed % 200 == 0:
                print(f"   ✓ {labels_fixed} labels corrigés...")
        
        except Exception as e:
            print(f"   ⚠️  Erreur sur {label_file.name}: {e}")
    
    print(f"\n✅ {labels_fixed} fichiers labels remappés!")
    
    if labels_errors:
        print(f"\n⚠️  {len(labels_errors)} erreurs de mapping:")
        for filename, class_id in labels_errors[:5]:
            print(f"   - {filename}: class_id {class_id} inconnu")
        if len(labels_errors) > 5:
            print(f"   ... et {len(labels_errors)-5} autres")
    
    print("\n" + "="*70)
    print("🎉 CORRECTION TERMINÉE!")
    print("="*70)
    print(f"\n📂 Dataset corrigé: {dataset_dir}/")
    print(f"   - data.yaml: 8 classes (au lieu de 252)")
    print(f"   - Labels: remappés vers index 0-7")
    print(f"\n💡 Vous pouvez maintenant relancer les visualisations:")
    print(f"   python visualize_annotations.py")

if __name__ == "__main__":
    fix_class_mapping()
