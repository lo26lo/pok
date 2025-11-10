#!/usr/bin/env python3
"""
Script de test de performance: Comparaison mosaic.py vs mosaic_optimized.py
Compare la vitesse de génération de mosaïques sur un petit échantillon
"""
import os
import sys
import time
import subprocess
from glob import glob

def safe_print(msg):
    """Print UTF-8 safe"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('utf-8', errors='ignore').decode('utf-8'))

def count_images_in_directory(directory):
    """Compte les images dans un répertoire"""
    patterns = ["*.jpg", "*.png", "*.jpeg"]
    count = 0
    for pattern in patterns:
        count += len(glob(os.path.join(directory, pattern)))
    return count

def test_mosaic_version(script_name, layout_mode, background_mode, transform_mode, max_groups=5):
    """
    Test une version de mosaic avec un nombre limité de groupes
    Retourne le temps d'exécution en secondes
    """
    safe_print(f"\n{'='*60}")
    safe_print(f"🧪 Test: {script_name}")
    safe_print(f"   Layout: {layout_mode}, Background: {background_mode}, Transform: {transform_mode}")
    safe_print(f"   Max groupes: {max_groups}")
    safe_print(f"{'='*60}")
    
    # Nettoyer les sorties précédentes
    output_dir = os.path.join("output", "yolov8", "images")
    if os.path.exists(output_dir):
        for f in glob(os.path.join(output_dir, "*")):
            try:
                os.remove(f)
            except:
                pass
    
    # Lancer le script (format différent selon la version)
    if "optimized" in script_name:
        # Version optimisée utilise argparse moderne
        cmd = [
            sys.executable,
            os.path.join("core", script_name),
            str(layout_mode),
            str(background_mode),
            str(transform_mode),
            "--max-groups", str(max_groups)
        ]
    else:
        # Version originale utilise sys.argv[1-4]
        cmd = [
            sys.executable,
            os.path.join("core", script_name),
            str(layout_mode),
            str(background_mode),
            str(transform_mode),
            str(max_groups)  # Pas de --max-groups
        ]
    
    safe_print(f"\n▶️  Commande: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            safe_print(f"\n✅ Succès!")
            safe_print(f"📊 Temps d'exécution: {elapsed:.2f} secondes")
            
            # Compter les images générées
            num_images = count_images_in_directory(output_dir)
            safe_print(f"🖼️  Images générées: {num_images}")
            
            if num_images > 0:
                speed = num_images / elapsed
                safe_print(f"⚡ Vitesse: {speed:.2f} mosaïques/seconde")
            
            return elapsed
        else:
            safe_print(f"\n❌ Erreur lors de l'exécution:")
            safe_print(result.stderr)
            return None
    except subprocess.TimeoutExpired:
        safe_print(f"\n⏱️  Timeout après 5 minutes!")
        return None
    except Exception as e:
        safe_print(f"\n❌ Exception: {e}")
        return None

def main():
    """Fonction principale de benchmark"""
    safe_print("="*60)
    safe_print("🚀 BENCHMARK: Mosaic Original vs Optimisé")
    safe_print("="*60)
    
    # Vérifier que les images d'entrée existent
    input_dir = os.path.join("output", "augmented", "images")
    if not os.path.exists(input_dir):
        safe_print(f"❌ Erreur: Répertoire d'entrée introuvable: {input_dir}")
        safe_print("   Veuillez d'abord générer des images augmentées.")
        return
    
    num_input_images = count_images_in_directory(input_dir)
    safe_print(f"\n📂 Images d'entrée: {num_input_images}")
    
    if num_input_images == 0:
        safe_print("❌ Aucune image d'entrée trouvée!")
        return
    
    # Calcul du nombre de groupes (8 cartes par groupe)
    max_groups = min(10, (num_input_images // 8) or 1)
    safe_print(f"🎯 Nombre de groupes à tester: {max_groups}")
    
    # Paramètres de test
    layout_mode = 1
    background_mode = 0
    transform_mode = 0
    
    # Test 1: Version ORIGINALE
    safe_print("\n\n" + "🔵"*30)
    safe_print("TEST 1: Version ORIGINALE (mosaic.py)")
    safe_print("🔵"*30)
    time_original = test_mosaic_version("mosaic.py", layout_mode, background_mode, transform_mode, max_groups)
    
    # Pause entre les tests
    safe_print("\n⏸️  Pause de 2 secondes...")
    time.sleep(2)
    
    # Test 2: Version OPTIMISÉE
    safe_print("\n\n" + "🟢"*30)
    safe_print("TEST 2: Version OPTIMISÉE (mosaic_optimized.py)")
    safe_print("🟢"*30)
    time_optimized = test_mosaic_version("mosaic_optimized.py", layout_mode, background_mode, transform_mode, max_groups)
    
    # Résumé des résultats
    safe_print("\n\n" + "="*60)
    safe_print("📊 RÉSULTATS DU BENCHMARK")
    safe_print("="*60)
    
    if time_original and time_optimized:
        speedup = time_original / time_optimized
        time_saved = time_original - time_optimized
        
        safe_print(f"\n⏱️  Temps version ORIGINALE:  {time_original:.2f} secondes")
        safe_print(f"⏱️  Temps version OPTIMISÉE:  {time_optimized:.2f} secondes")
        safe_print(f"\n🚀 ACCÉLÉRATION: {speedup:.1f}x plus rapide!")
        safe_print(f"💾 TEMPS GAGNÉ:  {time_saved:.2f} secondes ({time_saved/60:.1f} minutes)")
        
        # Projection pour un dataset complet
        if num_input_images > max_groups * 8:
            total_groups = num_input_images // 8
            projected_original = (time_original / max_groups) * total_groups
            projected_optimized = (time_optimized / max_groups) * total_groups
            projected_saved = projected_original - projected_optimized
            
            safe_print(f"\n📈 PROJECTION pour {total_groups} groupes ({num_input_images} images):")
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
    
    safe_print("\n" + "="*60)
    safe_print("✅ Benchmark terminé!")
    safe_print("="*60)

if __name__ == "__main__":
    main()
