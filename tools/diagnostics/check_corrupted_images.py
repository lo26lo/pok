import cv2
from pathlib import Path

img_dir = Path('augmented')  # Dossier augmented à la racine
corrupted = []
total_checked = 0

print("🔍 Vérification des images...")
for i, img_path in enumerate(sorted(img_dir.glob('*.png')), 1):
    total_checked = i
    img = cv2.imread(str(img_path))
    if img is None:
        corrupted.append(img_path)
        print(f"❌ {img_path.name}")
    if i % 500 == 0:
        print(f"   Vérifié {i} images...")

print(f"\n📊 Résultat: {len(corrupted)} images corrompues sur {total_checked} images totales")

if corrupted:
    print(f"\n🗑️  Suppression des images corrompues...")
    for img_path in corrupted:
        label_path = img_path.parent.parent / 'labels' / img_path.name.replace('.png', '.txt')
        
        img_path.unlink(missing_ok=True)
        label_path.unlink(missing_ok=True)
        print(f"   Supprimé: {img_path.name}")
    
    print(f"✅ {len(corrupted)} images corrompues supprimées")
else:
    print("✅ Aucune image corrompue!")
