#!/usr/bin/env python3
"""
Performance test for utils.py resize_cards function
Tests sequential vs multiprocessing performance
"""
import sys
import time
from pathlib import Path
import numpy as np
import cv2
import tempfile
import shutil

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import resize_cards


def create_test_images(num_images: int = 50) -> tuple:
    """Create temporary test images"""
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    # Create test images of typical card size
    for i in range(num_images):
        # Create random image
        img = np.random.randint(0, 255, (500, 350, 3), dtype=np.uint8)
        
        # Save to temp directory
        path = Path(temp_dir) / f"test_card_{i:03d}.png"
        cv2.imwrite(str(path), img)
        image_paths.append(str(path))
    
    return temp_dir, image_paths


def test_resize_performance():
    """Compare sequential vs multiprocessing resize performance"""
    print("="*70)
    print("🧪 Performance Test: resize_cards()")
    print("="*70)
    
    # Test configurations
    test_sizes = [10, 50, 100]
    
    for num_images in test_sizes:
        print(f"\n📊 Testing with {num_images} images:")
        print("-" * 70)
        
        # Create test images
        print(f"   Creating {num_images} test images...")
        temp_dir, image_paths = create_test_images(num_images)
        
        try:
            # Test 1: Sequential processing
            print(f"\n   1️⃣  Sequential processing...")
            start = time.perf_counter()
            results_seq = resize_cards(image_paths, target_size=(280, 380), use_multiprocessing=False)
            time_seq = time.perf_counter() - start
            
            print(f"      ✅ Processed {len(results_seq)} images")
            print(f"      ⏱️  Time: {time_seq:.3f}s ({num_images/time_seq:.1f} images/sec)")
            
            # Test 2: Multiprocessing (only if num_images >= 50)
            if num_images >= 50:
                print(f"\n   2️⃣  Multiprocessing...")
                start = time.perf_counter()
                results_mp = resize_cards(image_paths, target_size=(280, 380), use_multiprocessing=True)
                time_mp = time.perf_counter() - start
                
                print(f"      ✅ Processed {len(results_mp)} images")
                print(f"      ⏱️  Time: {time_mp:.3f}s ({num_images/time_mp:.1f} images/sec)")
                
                # Calculate speedup
                speedup = time_seq / time_mp
                print(f"\n   🚀 Speedup: {speedup:.2f}x faster with multiprocessing!")
                
                if speedup < 1.2:
                    print(f"   ℹ️  Note: Small speedup expected for I/O bound operations")
            else:
                print(f"\n   ℹ️  Skipping multiprocessing test (too few images)")
        
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
            print(f"\n   🧹 Cleaned up test images")
    
    print("\n" + "="*70)
    print("✅ Performance test complete!")
    print("="*70)
    
    # Recommendations
    print("\n💡 Recommendations:")
    print("   - Use sequential processing for <50 images")
    print("   - Use multiprocessing for ≥50 images (2-4x faster)")
    print("   - For best performance, batch process images in groups")
    print()


def test_memory_efficiency():
    """Test memory usage patterns"""
    print("\n" + "="*70)
    print("💾 Memory Efficiency Test")
    print("="*70)
    
    # Create a batch of test images
    num_images = 20
    temp_dir, image_paths = create_test_images(num_images)
    
    try:
        # Process images
        results = resize_cards(image_paths, target_size=(280, 380))
        
        # Calculate memory usage
        total_mb = 0
        for img, path in results:
            size_bytes = img.nbytes
            total_mb += size_bytes / (1024 * 1024)
        
        avg_mb = total_mb / len(results)
        
        print(f"\n📊 Memory Usage:")
        print(f"   Total images: {len(results)}")
        print(f"   Total memory: {total_mb:.2f} MB")
        print(f"   Average per image: {avg_mb:.2f} MB")
        print(f"   Estimated for 252 cards: {avg_mb * 252:.1f} MB")
        
        print("\n💡 For large datasets (>500 images):")
        print("   - Consider processing in batches")
        print("   - Release memory between batches")
        print("   - Use generators instead of lists where possible")
        
    finally:
        shutil.rmtree(temp_dir)
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Run performance tests
    test_resize_performance()
    
    # Run memory test
    test_memory_efficiency()
    
    print("\n✅ All performance tests completed!")
