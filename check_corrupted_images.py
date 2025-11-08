import cv2
from pathlib import Path

img_dir = Path('output/yolov8/images')
corrupted = []

print("🔍 Vérification des images...")
for i, img_path in enumerate(sorted(img_dir.glob('*.png')), 1):
    img = cv2.imread(str(img_path))
    if img is None:
        corrupted.append(img_path.name)
        print(f"❌ {img_path.name}")
    if i % 500 == 0:
        print(f"   Vérifié {i} images...")

print(f"\n📊 Résultat: {len(corrupted)} images corrompues sur {i} images totales")

if corrupted:
    print(f"\n🗑️  Suppression des images corrompues...")
    for img_name in corrupted:
        img_path = img_dir / img_name
        label_path = img_dir.parent / 'labels' / img_name.replace('.png', '.txt')
        
        img_path.unlink(missing_ok=True)
        label_path.unlink(missing_ok=True)
    
    print(f"✅ {len(corrupted)} images corrompues supprimées")
else:
    print("✅ Aucune image corrompue!")
