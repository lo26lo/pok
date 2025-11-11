#!/usr/bin/env python3
"""
Test de vérification d'une annotation spécifique
"""
import yaml
import pytest
from pathlib import Path

# Charger data.yaml
data_yaml = Path("output/dataset/data.yaml")

# Skip si dataset n'existe pas
pytestmark = pytest.mark.skipif(
    not data_yaml.exists(),
    reason="Dataset YOLO non généré (output/dataset/data.yaml manquant)"
)

def test_annotations_exist():
    """Vérifie que les annotations existent et sont valides"""
    with open(data_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    assert data is not None, "data.yaml est vide"
    assert 'names' in data, "Pas de 'names' dans data.yaml"
    print(f"✅ {len(data.get('names', {}))} classes détectées")

if __name__ == "__main__":
    # Code d'origine pour exécution standalone
    if not data_yaml.exists():
        print(f"❌ Fichier manquant: {data_yaml}")
        import sys
        sys.exit(1)
    
    with open(data_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

print("="*70)
print("🔍 VÉRIFICATION DÉTAILLÉE DES ANNOTATIONS")
print("="*70)

# Test sur sv08_051 (Quaxwell)
test_files = {
    "sv08_019": "Ho-Oh",
    "sv08_020": "Castform Sunny Form", 
    "sv08_026": "Oricorio",
    "sv08_046": "Shellos",
    "sv08_051": "Quaxwell",
    "sv08_126": "Bronzor",
    "sv08_132": "Iron Crown",
    "sv08_152": "Rufflet"
}

labels_dir = Path("output/dataset/labels")

for file_prefix, expected_name in test_files.items():
    # Trouver un fichier label pour cette carte
    label_files = list(labels_dir.glob(f"{file_prefix}_*.txt"))
    if not label_files:
        print(f"\n❌ {file_prefix}: Aucun fichier trouvé")
        continue
    
    label_file = label_files[0]
    with open(label_file, 'r') as f:
        line = f.readline().strip()
    
    if not line:
        print(f"\n❌ {file_prefix}: Label vide")
        continue
    
    class_id = int(line.split()[0])
    actual_name = data['names'][class_id]
    
    status = "✅" if actual_name == expected_name else "❌"
    print(f"\n{status} {file_prefix}:")
    print(f"   Fichier: {label_file.name}")
    print(f"   Class ID: {class_id}")
    print(f"   Nom dans data.yaml: {actual_name}")
    print(f"   Nom attendu: {expected_name}")
    if actual_name != expected_name:
        print(f"   ⚠️  ERREUR: Les noms ne correspondent pas!")

print("\n" + "="*70)
