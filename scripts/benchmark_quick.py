#!/usr/bin/env python3
"""
Quick Performance Benchmark - Compare key operations
====================================================

Runs quick benchmarks on common operations to help identify
if your system is performing optimally.

Usage:
    python scripts/benchmark_quick.py
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def benchmark_numpy_operations():
    """Benchmark NumPy array operations"""
    print("\n📊 NumPy Operations Benchmark")
    print("-" * 70)
    
    # Test 1: Array creation and manipulation
    size = 1000
    iterations = 100
    
    start = time.perf_counter()
    for _ in range(iterations):
        arr = np.random.rand(size, size)
        result = arr * 2 + 1
        _ = result.sum()
    duration = time.perf_counter() - start
    
    print(f"✅ {iterations} iterations of {size}x{size} array ops: {duration:.3f}s")
    print(f"   Average: {duration/iterations*1000:.2f}ms per iteration")
    
    if duration < 1.0:
        print("   🚀 Excellent! NumPy is fast")
    elif duration < 2.0:
        print("   ✅ Good NumPy performance")
    else:
        print("   ⚠️  NumPy seems slow - check installation")
    
    return duration


def benchmark_image_operations():
    """Benchmark image processing operations"""
    print("\n🖼️  Image Processing Benchmark")
    print("-" * 70)
    
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV not installed, skipping")
        return None
    
    # Create test image
    img = np.random.randint(0, 255, (500, 350, 3), dtype=np.uint8)
    
    # Test resize operations
    iterations = 50
    start = time.perf_counter()
    for _ in range(iterations):
        resized = cv2.resize(img, (280, 380), interpolation=cv2.INTER_AREA)
    duration = time.perf_counter() - start
    
    print(f"✅ {iterations} image resizes (500x350 → 280x380): {duration:.3f}s")
    print(f"   Average: {duration/iterations*1000:.2f}ms per resize")
    
    speed = iterations / duration
    print(f"   Speed: {speed:.1f} resizes/second")
    
    if speed > 300:
        print("   🚀 Excellent! Image processing is fast")
    elif speed > 150:
        print("   ✅ Good image processing performance")
    else:
        print("   ⚠️  Image processing seems slow")
    
    return duration


def benchmark_file_io():
    """Benchmark file I/O operations"""
    print("\n💾 File I/O Benchmark")
    print("-" * 70)
    
    import tempfile
    import shutil
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test writing small files
        num_files = 100
        data = b"x" * 1024  # 1KB per file
        
        start = time.perf_counter()
        for i in range(num_files):
            with open(f"{temp_dir}/file_{i}.dat", 'wb') as f:
                f.write(data)
        write_duration = time.perf_counter() - start
        
        print(f"✅ Write {num_files} files (1KB each): {write_duration:.3f}s")
        print(f"   Speed: {num_files/write_duration:.1f} files/second")
        
        # Test reading files
        start = time.perf_counter()
        for i in range(num_files):
            with open(f"{temp_dir}/file_{i}.dat", 'rb') as f:
                _ = f.read()
        read_duration = time.perf_counter() - start
        
        print(f"✅ Read {num_files} files: {read_duration:.3f}s")
        print(f"   Speed: {num_files/read_duration:.1f} files/second")
        
        if read_duration < 0.1:
            print("   🚀 Excellent! Fast disk I/O")
        elif read_duration < 0.5:
            print("   ✅ Good disk I/O performance")
        else:
            print("   ⚠️  Disk I/O seems slow - check disk/SSD")
    
    finally:
        shutil.rmtree(temp_dir)
    
    return write_duration, read_duration


def benchmark_gpu_availability():
    """Check GPU availability"""
    print("\n🎮 GPU Detection")
    print("-" * 70)
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            
            print(f"✅ GPU Available: {device_name}")
            print(f"   Device count: {device_count}")
            
            # Simple GPU benchmark
            if device_count > 0:
                size = 1000
                iterations = 10
                
                # CPU benchmark
                x_cpu = torch.rand(size, size)
                y_cpu = torch.rand(size, size)
                start = time.perf_counter()
                for _ in range(iterations):
                    z_cpu = torch.matmul(x_cpu, y_cpu)
                cpu_time = time.perf_counter() - start
                
                # GPU benchmark
                x_gpu = torch.rand(size, size).cuda()
                y_gpu = torch.rand(size, size).cuda()
                torch.cuda.synchronize()
                start = time.perf_counter()
                for _ in range(iterations):
                    z_gpu = torch.matmul(x_gpu, y_gpu)
                    torch.cuda.synchronize()
                gpu_time = time.perf_counter() - start
                
                speedup = cpu_time / gpu_time
                
                print(f"\n   Matrix multiplication ({size}x{size}, {iterations} iterations):")
                print(f"   CPU time: {cpu_time:.3f}s")
                print(f"   GPU time: {gpu_time:.3f}s")
                print(f"   🚀 GPU Speedup: {speedup:.1f}x faster")
                
                if speedup > 5:
                    print("   🎉 Excellent GPU acceleration!")
                elif speedup > 2:
                    print("   ✅ Good GPU performance")
                else:
                    print("   ⚠️  Limited GPU acceleration (driver issue?)")
        else:
            print("❌ No GPU available")
            print("   Consider using optimized CPU modules (*_optimized.py)")
    
    except ImportError:
        print("❌ PyTorch not installed")
        print("   Install with: pip install torch torchvision")
    except Exception as e:
        print(f"❌ Error testing GPU: {e}")


def print_system_info():
    """Print system information"""
    print("\n💻 System Information")
    print("-" * 70)
    
    import platform
    import multiprocessing
    
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"CPU cores: {multiprocessing.cpu_count()}")
    
    try:
        import numpy as np
        print(f"NumPy: {np.__version__}")
    except:
        pass
    
    try:
        import cv2
        print(f"OpenCV: {cv2.__version__}")
    except:
        pass
    
    try:
        import torch
        print(f"PyTorch: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
    except:
        pass


def main():
    """Run all benchmarks"""
    print("\n" + "="*70)
    print("🚀 QUICK PERFORMANCE BENCHMARK")
    print("="*70)
    
    print_system_info()
    
    # Run benchmarks
    numpy_time = benchmark_numpy_operations()
    image_time = benchmark_image_operations()
    io_times = benchmark_file_io()
    benchmark_gpu_availability()
    
    # Summary
    print("\n" + "="*70)
    print("📊 BENCHMARK SUMMARY")
    print("="*70)
    
    print("\nYour system performance:")
    
    if numpy_time and numpy_time < 2.0:
        print("  ✅ NumPy: Fast")
    else:
        print("  ⚠️  NumPy: Could be faster")
    
    if image_time and image_time < 0.5:
        print("  ✅ Image Processing: Fast")
    else:
        print("  ⚠️  Image Processing: Could be faster")
    
    print("\n💡 Recommendations:")
    print("  • For large datasets (>100 images), use *_optimized.py modules")
    print("  • Enable multiprocessing for batch operations")
    print("  • Use GPU acceleration when available")
    print("  • See docs/PERFORMANCE_GUIDE.md for optimization tips")
    
    print("\n" + "="*70)
    print("✅ Benchmark complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
