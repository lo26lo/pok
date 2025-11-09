#!/usr/bin/env python3
"""
Corrige le mapping des class_id en utilisant les vrais noms des cartes
"""
from pathlib import Path
import yaml
import shutil
import pandas as pd

def get_card_names_from_excel():
    """Récupère les noms réels des cartes depuis l'Excel"""
    excel_path = Path("excel/cards_info.xlsx")
    df = pd.read_excel(excel_path)
    
    our_card_numbers = [19, 20, 26, 46, 51, 126, 132, 152]
    names = []
    
    for card_num in our_card_numbers:
        set_num_str = f"{card_num:03d}/191"
        matching_rows = df[df['Set #'] == set_num_str]
        if not matching_rows.empty:
            names.append(matching_rows.iloc[0]['Name'])
        else:
            names.append(f"Unknown_{card_num}")
    
    return names

def fix_class_mapping_correct():
    """Remappe les class_id en utilisant les vrais noms"""
    
    # Récupérer les vrais noms depuis l'Excel
    our_card_names = get_card_names_from_excel()
    
    # Mapping: index dans data.yaml original -> nouvel index local
    # Le data.yaml original a l'index 0-251, nous devons trouver où sont nos cartes
    # sv08_019 = Ho-Oh est à l'index 18 (ligne 19)
    # sv08_020 = Castform est à l'index 19 (ligne 20)
    # etc.
    card_mapping = {
        18: 0,   # sv08_019 -> Ho-Oh (index 18 dans data.yaml)
        19: 1,   # sv08_020 -> Castform Sunny Form (index 19)
        25: 2,   # sv08_026 -> Oricorio (index 25)
        45: 3,   # sv08_046 -> Shellos (index 45)
        50: 4,   # sv08_051 -> Quaxwell (index 50)
        125: 5,  # sv08_126 -> Bronzor (index 125)
        131: 6,  # sv08_132 -> Iron Crown (index 131)
        151: 7   # sv08_152 -> Rufflet (index 151)
    }
    
    dataset_dir = Path("output/dataset")
    data_yaml_path = dataset_dir / "data.yaml"
    
    print("="*70)
    print("🔧 CORRECTION DU MAPPING DES CLASS_ID (VERSION CORRECTE)")
    print("="*70)
    print(f"\n📋 Mapping des cartes (index data.yaml -> index local):")
    for old_id, new_id in sorted(card_mapping.items(), key=lambda x: x[1]):
        print(f"   Class {old_id:3d} -> Class {new_id} ({our_card_names[new_id]})")
    
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
    total_boxes_remapped = 0
    
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
                    total_boxes_remapped += 1
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
    print(f"✅ {total_boxes_remapped} bounding boxes remappées!")
    
    if labels_errors:
        print(f"\n⚠️  {len(labels_errors)} class_id non remappés (normal si erreurs précédentes):")
        unique_errors = set(err[1] for err in labels_errors)
        for class_id in sorted(unique_errors):
            count = sum(1 for err in labels_errors if err[1] == class_id)
            print(f"   - class_id {class_id}: {count} occurrences")
    
    print("\n" + "="*70)
    print("🎉 CORRECTION TERMINÉE!")
    print("="*70)
    print(f"\n📂 Dataset corrigé: {dataset_dir}/")
    print(f"   - data.yaml: 8 classes correctes")
    print(f"   - Labels: {total_boxes_remapped} boxes remappées vers index 0-7")
    print(f"\n💡 Relancez les visualisations:")
    print(f"   python visualize_annotations.py")

if __name__ == "__main__":
    fix_class_mapping_correct()
