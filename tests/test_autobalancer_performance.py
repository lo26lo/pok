#!/usr/bin/env python3
"""
Benchmark auto_balancer.py vs auto_balancer_optimized.py
Compare la vitesse de génération d'images pour équilibrer les classes
"""
import os
import sys
import time
import shutil
from pathlib import Path

def safe_print(msg):
    """Print UTF-8 safe"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('utf-8', errors='ignore').decode('utf-8'))

def create_test_dataset(output_dir, num_images_per_class=[5, 10, 15, 20]):
    """Crée un petit dataset de test"""
    dataset_dir = Path(output_dir)
    images_dir = dataset_dir / "images"
    labels_dir = dataset_dir / "labels"
    
    # Nettoyer si existe
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    
    images_dir.mkdir(parents=True)
    labels_dir.mkdir(parents=True)
    
    # Créer des images factices
    import cv2
    import numpy as np
    
    img_idx = 0
    for class_id, count in enumerate(num_images_per_class):
        for i in range(count):
            # Image aléatoire
            img = np.random.randint(0, 255, (380, 280, 3), dtype=np.uint8)
            img_name = f"test_{img_idx:04d}"
            
            # Sauvegarder image
            cv2.imwrite(str(images_dir / f"{img_name}.jpg"), img)
            
            # Créer label YOLO (une seule bbox au centre)
            with open(labels_dir / f"{img_name}.txt", "w") as f:
                f.write(f"{class_id} 0.5 0.5 0.3 0.3\n")
            
            img_idx += 1
    
    safe_print(f"✅ Dataset de test créé: {len(num_images_per_class)} classes")
    for class_id, count in enumerate(num_images_per_class):
        safe_print(f"   Classe {class_id}: {count} images")
    
    return str(dataset_dir)

def test_balancer(script_name, dataset_dir, target_count):
    """Test un balancer et retourne le temps d'exécution"""
    import subprocess
    
    safe_print(f"\n{'='*60}")
    safe_print(f"🧪 Test: {script_name}")
    safe_print(f"{'='*60}")
    
    cmd = [
        sys.executable, "-u", 
        os.path.join("core", script_name),
        dataset_dir,
        "--target", str(target_count),
        "--strategy", "augment"
    ]
    
    safe_print(f"▶️  Commande: {' '.join(cmd)}\n")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            safe_print(f"\n✅ Succès!")
            safe_print(f"📊 Temps d'exécution: {elapsed:.2f} secondes")
            return elapsed
        else:
            safe_print(f"\n❌ Erreur:")
            safe_print(result.stderr)
            return None
    except subprocess.TimeoutExpired:
        safe_print(f"\n⏱️  Timeout après 5 minutes!")
        return None
    except Exception as e:
        safe_print(f"\n❌ Exception: {e}")
        return None

def main():
    safe_print("="*60)
    safe_print("🚀 BENCHMARK: Auto-Balancer Original vs Optimisé")
    safe_print("="*60)
    
    # Créer dataset de test
    safe_print("\n📦 Création du dataset de test...")
    test_dataset = create_test_dataset("test_balancer_dataset", [1, 2, 3, 5, 8])
    target_count = 20
    
    safe_print(f"\n🎯 Target: {target_count} images par classe")
    safe_print(f"📈 Classes à augmenter: 5")
    safe_print(f"🔢 Images à générer: {(20-1) + (20-2) + (20-3) + (20-5) + (20-8)} = 82 images")
    
    # Test 1: Version ORIGINALE
    safe_print("\n\n" + "🔵"*30)
    safe_print("TEST 1: Version ORIGINALE (auto_balancer.py)")
    safe_print("🔵"*30)
    time_original = test_balancer("auto_balancer.py", test_dataset, target_count)
    
    # Restaurer le dataset pour le test 2
    if Path(test_dataset).exists():
        shutil.rmtree(test_dataset)
    test_dataset = create_test_dataset("test_balancer_dataset", [1, 2, 3, 5, 8])
    
    # Pause
    safe_print("\n⏸️  Pause de 2 secondes...")
    time.sleep(2)
    
    # Test 2: Version OPTIMISÉE
    safe_print("\n\n" + "🟢"*30)
    safe_print("TEST 2: Version OPTIMISÉE (auto_balancer_optimized.py)")
    safe_print("🟢"*30)
    time_optimized = test_balancer("auto_balancer_optimized.py", test_dataset, target_count)
    
    # Résultats
    safe_print("\n\n" + "="*60)
    safe_print("📊 RÉSULTATS DU BENCHMARK")
    safe_print("="*60)
    
    if time_original and time_optimized:
        speedup = time_original / time_optimized
        time_saved = time_original - time_optimized
        
        safe_print(f"\n⏱️  Temps version ORIGINALE:  {time_original:.2f} secondes")
        safe_print(f"⏱️  Temps version OPTIMISÉE:  {time_optimized:.2f} secondes")
        safe_print(f"\n🚀 ACCÉLÉRATION: {speedup:.1f}x plus rapide!")
        safe_print(f"💾 TEMPS GAGNÉ:  {time_saved:.2f} secondes")
        
        # Projection pour dataset réel
        safe_print(f"\n📈 PROJECTION pour balancing réel (100 classes à augmenter):")
        projected_original = (time_original / 82) * 2000  # ~2000 images à générer
        projected_optimized = (time_optimized / 82) * 2000
        projected_saved = projected_original - projected_optimized
        
        safe_print(f"   Version originale:  ~{projected_original/60:.1f} minutes")
        safe_print(f"   Version optimisée:  ~{projected_optimized/60:.1f} minutes")
        safe_print(f"   ⏰ GAIN ESTIMÉ:     ~{projected_saved/60:.1f} minutes!")
        
        # Message de conclusion
        if speedup >= 10:
            safe_print(f"\n🎉 EXCELLENT! Accélération de {speedup:.0f}x - optimisation très efficace!")
        elif speedup >= 5:
            safe_print(f"\n✅ TRÈS BIEN! Accélération de {speedup:.1f}x - amélioration significative!")
        elif speedup >= 2:
            safe_print(f"\n👍 BIEN! Accélération de {speedup:.1f}x - bonne amélioration!")
        else:
            safe_print(f"\n⚠️  Accélération modeste de {speedup:.1f}x - amélioration limitée")
    else:
        safe_print("\n❌ Impossible de calculer le speedup (échec d'un ou plusieurs tests)")
    
    # Nettoyage
    safe_print(f"\n🧹 Nettoyage du dataset de test...")
    if Path(test_dataset).exists():
        shutil.rmtree(test_dataset)
    
    safe_print("\n" + "="*60)
    safe_print("✅ Benchmark terminé!")
    safe_print("="*60)

if __name__ == "__main__":
    main()
