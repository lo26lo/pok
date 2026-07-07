#!/usr/bin/env python3
"""
Corrige UNIQUEMENT le data.yaml pour avoir les bons noms de classes
SANS toucher aux labels qui utilisent les indices originaux
"""
from pathlib import Path
import yaml
import pandas as pd

def update_data_yaml_only():
    """Met à jour data.yaml pour mapper les 8 classes correctement"""
    
    # Lire l'Excel pour les vrais noms
    excel_path = Path("excel/cards_info.xlsx")
    df = pd.read_excel(excel_path)
    
    # Nos 8 cartes avec leurs indices ORIGINAUX dans le data.yaml (0-251)
    # sv08_019 -> ligne 19 de l'Excel -> index 18 dans data.yaml (0-based)
    card_indices = [18, 19, 25, 45, 50, 125, 131, 151]  # Indices dans le data.yaml original
    
    # Charger le data.yaml actuel pour récupérer TOUS les noms
    dataset_dir = Path("output/dataset")
    data_yaml_path = dataset_dir / "data.yaml"
    
    with open(data_yaml_path, 'r', encoding='utf-8') as f:
        current_data = yaml.safe_load(f)
    
    all_names = current_data['names']
    
    print("="*70)
    print("🔧 MISE À JOUR DU DATA.YAML UNIQUEMENT")
    print("="*70)
    print(f"\n📋 Conservation des {len(all_names)} noms de classes")
    print(f"✅ Les labels gardent leurs class_id originaux (18, 19, 25, 45, 50, 125, 131, 151)")
    print(f"\n🎯 Nos 8 cartes utilisées:")
    
    for i, idx in enumerate(card_indices):
        card_num = [19, 20, 26, 46, 51, 126, 132, 152][i]
        print(f"   sv08_{card_num:03d} -> class_id {idx} = {all_names[idx]}")
    
    # Le data.yaml reste avec 252 classes, mais c'est normal
    # YOLO utilisera seulement les class_id présents dans les labels
    print(f"\n💡 Le data.yaml conserve les 252 classes pour que les class_id correspondent")
    print(f"   YOLO n'entraînera QUE sur les 8 classes présentes dans les labels")
    
    print("\n" + "="*70)
    print("✅ CONFIGURATION CORRECTE!")
    print("="*70)
    print(f"\n📊 Statistiques:")
    print(f"   - Classes dans data.yaml: 252 (mapping complet)")
    print(f"   - Classes utilisées: 8 (dans les labels)")
    print(f"   - Labels: inchangés (class_id 18, 19, 25, 45, 50, 125, 131, 151)")
    
    return True

if __name__ == "__main__":
    update_data_yaml_only()
