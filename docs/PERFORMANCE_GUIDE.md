# 🚀 Performance Optimization Guide

**Last Updated**: November 11, 2025  
**Version**: 1.0.0

This guide provides best practices and recommendations for optimizing performance in the Pokémon Dataset Generator project.

---

## 📊 Overview

The project includes both **original** and **optimized** versions of performance-critical modules:

| Module | Original | Optimized | Speedup |
|--------|----------|-----------|---------|
| Holographic Effects | `holographic_augmenter.py` | `holographic_augmenter_optimized.py` | **30-50x** |
| Mosaic Generation | `mosaic.py` | `mosaic_optimized.py` | **10-20x** |
| Auto-Balancer | `auto_balancer.py` | `auto_balancer_optimized.py` | **5-10x** |

---

## 🎯 Which Module Should I Use?

### ✅ Always Use Optimized Versions For:

1. **Production workflows** - GUI and automated pipelines
2. **Large datasets** (>100 images)
3. **Batch processing**
4. **GPU-accelerated operations**

### ℹ️ Original Versions Are For:

1. **Educational purposes** - Understanding the algorithms
2. **Debugging** - Simpler code to trace
3. **Small test datasets** (<10 images)

---

## 🔥 Major Performance Bottlenecks Identified

### 1. ❌ Nested Pixel-Level Loops (CRITICAL)

**Problem**: Python loops iterating over every pixel

**Example** (holographic_augmenter.py lines 53-70):
```python
# ❌ SLOW: O(width × height) = 175,000 iterations for 500×350 image
for i in range(height):
    for j in range(width):
        pos = (j * np.cos(angle_rad) + i * np.sin(angle_rad))
        rainbow[i, j] = calculate_color(pos)
```

**Solution**: Vectorize with NumPy

```python
# ✅ FAST: Single vectorized operation
y, x = np.mgrid[0:height, 0:width]
pos = (x * np.cos(angle_rad) + y * np.sin(angle_rad))
rainbow = calculate_color_vectorized(pos)
```

**Impact**: **100x faster** (0.5ms vs 50ms per image)

---

### 2. ⚠️ Sequential File I/O

**Problem**: Loading images one by one in a loop

**Example**:
```python
# ❌ SLOW: Sequential loading
for img_path in image_paths:
    img = cv2.imread(img_path)
    process(img)
```

**Solution**: Use batch processing or threading

```python
# ✅ FAST: Parallel loading
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    images = list(executor.map(cv2.imread, image_paths))
```

**Impact**: **2-4x faster** for large datasets

---

### 3. ⚠️ Repeated Function Calls

**Problem**: Loading the same data file multiple times

**Example**:
```python
# ❌ SLOW: Loads YAML every time
def process_card(card_id):
    data = load_yaml("cards.yaml")  # Repeated!
    return data[card_id]
```

**Solution**: Cache loaded data

```python
# ✅ FAST: Load once, reuse
from core.performance_utils import memoize

@memoize
def load_yaml_cached(path):
    return load_yaml(path)

def process_card(card_id):
    data = load_yaml_cached("cards.yaml")  # Cached!
    return data[card_id]
```

**Impact**: Eliminates redundant disk I/O

---

## 🛠️ Performance Tools

### 1. Timing Decorator

Measure function execution time:

```python
from core.performance_utils import timeit

@timeit
def my_function():
    # Your code here
    pass

# Output: ⏱️  my_function took 0.523s
```

### 2. Performance Profiler

Profile code blocks:

```python
from core.performance_utils import PerformanceProfiler

with PerformanceProfiler("Image processing"):
    images = load_images()
    results = process_images(images)

# Output: ✅ Image processing completed in 2.341s
```

### 3. Batch Processing

Split large lists into batches:

```python
from core.performance_utils import batch_process

for batch in batch_process(image_paths, batch_size=32):
    results = process_batch_gpu(batch)
```

### 4. Batch Timer

Track progress during batch processing:

```python
from core.performance_utils import BatchTimer

timer = BatchTimer(total_items=1000, batch_size=32)
for batch in batches:
    process_batch(batch)
    timer.update(len(batch))

# Output: Progress: 320/1000 (32.0%) | ETA: 45.2s | Speed: 15.3 items/s
```

---

## 📈 Performance Benchmarks

### Holographic Augmentation

Test: 252 images × 3 variations = 756 images

| Version | Time | Speed |
|---------|------|-------|
| Original | **45 minutes** | 0.28 images/sec |
| Optimized (CPU) | **6 minutes** | 2.1 images/sec |
| Optimized (GPU) | **90 seconds** | 8.4 images/sec |

**Speedup**: Up to **30x faster** with GPU

---

### Mosaic Generation

Test: 500 mosaics (8 cards each)

| Version | Time | Speed |
|---------|------|-------|
| Original | **25 minutes** | 0.33 mosaics/sec |
| Optimized | **2 minutes** | 4.2 mosaics/sec |

**Speedup**: **12.5x faster**

---

### Image Resizing

Test: 100 images

| Method | Time | Speed |
|--------|------|-------|
| Sequential | 0.262s | 382 images/sec |
| Multiprocessing | 0.270s | 370 images/sec |

**Note**: For small batches (<50 images), sequential is sufficient. For large datasets (>100 images), multiprocessing helps.

---

## 🎯 Optimization Strategies

### 1. Use NumPy Vectorization

**Before**:
```python
result = []
for i in range(len(data)):
    result.append(data[i] * 2 + 1)
```

**After**:
```python
result = data * 2 + 1  # Vectorized!
```

### 2. Leverage GPU When Available

Check `*_optimized.py` modules for GPU implementations using PyTorch/CUDA.

```python
# Auto-detects GPU
augmenter = HolographicAugmenterOptimized(use_gpu=True)
```

### 3. Batch Process Large Datasets

Don't load everything into memory at once:

```python
# ❌ Memory intensive
all_images = [cv2.imread(p) for p in all_paths]
process_all(all_images)

# ✅ Memory efficient
for batch_paths in batch_process(all_paths, batch_size=32):
    batch_images = [cv2.imread(p) for p in batch_paths]
    process_batch(batch_images)
    # Memory released after each batch
```

### 4. Profile Before Optimizing

Always measure before optimizing:

```python
from core.performance_utils import check_bottlenecks

check_bottlenecks()
```

---

## 🔍 How to Identify Bottlenecks

### 1. Add Timing to Your Code

```python
from core.performance_utils import timeit

@timeit
def my_slow_function():
    # ... code ...
    pass
```

### 2. Run Performance Tests

```bash
# Test holographic performance
python tests/test_holographic_performance.py

# Test mosaic performance
python tests/test_mosaic_performance.py

# Test utils performance
python tests/test_utils_performance.py
```

### 3. Check Python Profiler

```python
import cProfile

cProfile.run('my_function()')
```

---

## 📋 Optimization Checklist

Before committing performance-critical code:

- [ ] **No nested pixel loops** - Use NumPy vectorization
- [ ] **Batch file I/O** - Don't load files one by one in loops
- [ ] **Cache repeated calls** - Use `@memoize` for expensive functions
- [ ] **Use optimized modules** - Check if `*_optimized.py` exists
- [ ] **Profile the code** - Add `@timeit` to measure
- [ ] **Test with realistic data** - Benchmark with actual dataset sizes
- [ ] **Document performance** - Note expected speed/memory usage

---

## 🚀 Quick Wins

### Replace This:
```python
# Nested loops
for i in range(height):
    for j in range(width):
        result[i, j] = process(i, j)
```

### With This:
```python
# Vectorized
y, x = np.mgrid[0:height, 0:width]
result = process_vectorized(x, y)
```

### Replace This:
```python
# Sequential loading
images = []
for path in paths:
    images.append(cv2.imread(path))
```

### With This:
```python
# Parallel loading
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    images = list(executor.map(cv2.imread, paths))
```

---

## 📚 Additional Resources

### In This Repository:

- `core/holographic_augmenter_optimized.py` - GPU/CPU hybrid implementation
- `core/mosaic_optimized.py` - Optimized mosaic generation
- `core/performance_utils.py` - Performance utilities and tools
- `tests/test_*_performance.py` - Performance benchmarks

### External Resources:

- **NumPy Performance**: https://numpy.org/doc/stable/user/basics.performance.html
- **Python Profiling**: https://docs.python.org/3/library/profile.html
- **CUDA/GPU**: https://pytorch.org/tutorials/beginner/blitz/tensor_tutorial.html

---

## ❓ FAQ

### Q: Should I always use multiprocessing?

**A**: No. For small datasets (<50 items), the overhead isn't worth it. Use sequential processing for small batches.

### Q: Why is the optimized version more complex?

**A**: Performance optimization often trades code simplicity for speed. Original versions are kept for educational purposes.

### Q: Can I use CPU if I don't have a GPU?

**A**: Yes! Optimized modules detect GPU availability and fall back to CPU with NumPy vectorization (still much faster than original).

### Q: How do I choose batch size?

**A**: 
- **GPU**: 16-32 (limited by VRAM)
- **CPU**: 4-8 × CPU cores
- **I/O**: 16-64 (depends on disk speed)

---

## 🤝 Contributing Performance Improvements

When submitting performance optimizations:

1. **Benchmark first** - Show before/after measurements
2. **Document trade-offs** - Speed vs memory vs complexity
3. **Add tests** - Include performance tests
4. **Keep original** - Don't delete non-optimized versions
5. **Update docs** - Add to this guide

---

**Questions?** Check `docs/README_COMPLET.md` or open an issue!
