#!/usr/bin/env python3
"""
Vérification détaillée avec affichage des noms de cartes
"""
import yaml
from pathlib import Path

# Charger data.yaml
data_yaml = Path("output/dataset/data.yaml")
with open(data_yaml, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print("="*70)
print("🔍 VÉRIFICATION ULTRA-DÉTAILLÉE DES CORRESPONDANCES")
print("="*70)

# Les 8 cartes avec les vrais noms français (sur les cartes physiques)
nos_cartes_fr = {
    "sv08_019": ("Ho-Oh", 18),
    "sv08_020": ("Morphéo Solaire", 19),  # Castform Sunny Form
    "sv08_026": ("Plumeline", 25),  # Oricorio  
    "sv08_046": ("Sancoki", 45),  # Shellos
    "sv08_051": ("Canarbello", 50),  # Quaxwell
    "sv08_126": ("Archéomire", 125),  # Bronzor
    "sv08_132": ("Chef-de-Fer", 131),  # Iron Crown
    "sv08_152": ("Furaiglon", 151)  # Rufflet
}

print("\n📋 Vérification des correspondances:")
print("\nFormat: Fichier -> Nom FR (sur carte) -> Class ID -> Nom EN (data.yaml)\n")

labels_dir = Path("output/dataset/labels")

for file_prefix, (nom_fr, class_id_attendu) in nos_cartes_fr.items():
    # Trouver un fichier
    label_files = list(labels_dir.glob(f"{file_prefix}_*.txt"))
    if not label_files:
        print(f"❌ {file_prefix}: Aucun fichier trouvé")
        continue
    
    label_file = label_files[0]
    with open(label_file, 'r') as f:
        line = f.readline().strip()
    
    if not line:
        print(f"❌ {file_prefix}: Label vide")
        continue
    
    class_id = int(line.split()[0])
    nom_en = data['names'][class_id]
    
    # Vérifier la correspondance
    correct = (class_id == class_id_attendu)
    status = "✅" if correct else "❌"
    
    print(f"{status} {file_prefix}")
    print(f"   Nom FR attendu:     {nom_fr}")
    print(f"   Class ID trouvé:    {class_id} (attendu: {class_id_attendu})")
    print(f"   Nom EN (data.yaml): {nom_en}")
    
    if not correct:
        print(f"   ⚠️  ERREUR: Class ID {class_id} au lieu de {class_id_attendu}")
    print()

# Vérifier une mosaïque
print("\n" + "="*70)
print("🎨 VÉRIFICATION D'UNE MOSAÏQUE")
print("="*70)

mosaic_files = list(labels_dir.glob("layout_*.txt"))
if mosaic_files:
    mosaic_file = mosaic_files[0]
    print(f"\nFichier: {mosaic_file.name}")
    
    with open(mosaic_file, 'r') as f:
        lines = f.readlines()
    
    print(f"Nombre de cartes: {len(lines)}\n")
    
    for i, line in enumerate(lines, 1):
        parts = line.strip().split()
        if len(parts) < 5:
            continue
        
        class_id = int(parts[0])
        nom_en = data['names'][class_id]
        
        # Trouver le nom FR correspondant
        nom_fr = "?"
        for prefix, (fr, cid) in nos_cartes_fr.items():
            if cid == class_id:
                nom_fr = fr
                break
        
        print(f"  Carte {i}: Class {class_id:3d} = {nom_en:20s} (FR: {nom_fr})")

print("\n" + "="*70)
