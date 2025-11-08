#!/usr/bin/env python3
"""
Test de performance: ancienne version vs optimisée
"""
import time
import sys
from pathlib import Path
import cv2
import numpy as np

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_performance():
    """Compare les performances"""
    print("="*60)
    print("🧪 Test de Performance - Holographic Augmenter")
    print("="*60)
    
    # Créer une image de test
    test_image = np.random.randint(0, 255, (500, 350, 3), dtype=np.uint8)
    
    print("\n1️⃣  Test de la version OPTIMISÉE...")
    print("-" * 60)
    
    try:
        from core.holographic_augmenter_optimized import HolographicAugmenterOptimized
        
        augmenter_opt = HolographicAugmenterOptimized(use_gpu=True)
        
        # Warm-up
        _ = augmenter_opt.apply_holographic_effect(test_image.copy(), 'medium')
        
        # Benchmark
        start = time.time()
        num_iterations = 10
        for i in range(num_iterations):
            result = augmenter_opt.apply_holographic_effect(test_image.copy(), 'medium')
        elapsed_opt = time.time() - start
        
        time_per_image_opt = elapsed_opt / num_iterations
        
        print(f"✅ Version OPTIMISÉE:")
        print(f"   {num_iterations} images en {elapsed_opt:.2f}s")
        print(f"   Temps par image: {time_per_image_opt:.3f}s")
        print(f"   Vitesse: {1/time_per_image_opt:.1f} images/sec")
        
    except Exception as e:
        print(f"❌ Erreur version optimisée: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n2️⃣  Test de la version ORIGINALE...")
    print("-" * 60)
    
    try:
        from core.holographic_augmenter import HolographicAugmenter
        
        augmenter_old = HolographicAugmenter()
        
        # Benchmark (moins d'itérations car plus lent)
        start = time.time()
        num_iterations_old = 3
        for i in range(num_iterations_old):
            result = augmenter_old.apply_holographic_effect(test_image.copy(), 'medium')
        elapsed_old = time.time() - start
        
        time_per_image_old = elapsed_old / num_iterations_old
        
        print(f"✅ Version ORIGINALE:")
        print(f"   {num_iterations_old} images en {elapsed_old:.2f}s")
        print(f"   Temps par image: {time_per_image_old:.3f}s")
        print(f"   Vitesse: {1/time_per_image_old:.1f} images/sec")
        
    except Exception as e:
        print(f"❌ Erreur version originale: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("📊 RÉSULTATS")
    print("="*60)
    
    speedup = time_per_image_old / time_per_image_opt
    
    print(f"\n🚀 ACCÉLÉRATION: {speedup:.1f}x plus rapide!")
    print(f"\n💾 ESTIMATION pour 252 images × 3 variations:")
    print(f"   Ancienne version: {(252*3*time_per_image_old)/60:.1f} minutes")
    print(f"   Version optimisée: {(252*3*time_per_image_opt)/60:.1f} minutes")
    print(f"   Gain de temps: {((252*3*time_per_image_old) - (252*3*time_per_image_opt))/60:.1f} minutes économisées!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_performance()
