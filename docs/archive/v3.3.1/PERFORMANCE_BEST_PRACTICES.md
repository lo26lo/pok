# 🚀 Performance Best Practices - Quick Reference

**Target Audience**: Developers working on Pokémon Dataset Generator  
**Last Updated**: 2025-11-11

---

## 🎯 Golden Rules

### Rule #1: Avoid Nested Loops on Images
```python
# ❌ BAD: O(height × width) - Very slow
for i in range(height):
    for j in range(width):
        image[i, j] = some_calculation(i, j)

# ✅ GOOD: O(1) - Vectorized
y, x = np.indices((height, width))
image = some_calculation_vectorized(y, x)
```

### Rule #2: Use NumPy Operations
```python
# ❌ BAD: Python loops
result = []
for x in data:
    result.append(x * 2 + 5)

# ✅ GOOD: NumPy vectorization
result = data * 2 + 5
```

### Rule #3: Create Coordinate Grids Once
```python
# ❌ BAD: Recreating grids
for effect in effects:
    y, x = np.indices((h, w))  # Wasteful recreation
    apply_effect(y, x)

# ✅ GOOD: Reuse grids
y, x = np.indices((h, w))  # Create once
for effect in effects:
    apply_effect(y, x)  # Reuse
```

### Rule #4: Use Parallel Processing for Independent Tasks
```python
# ❌ BAD: Sequential processing
results = []
for image_path in image_paths:
    result = process_image(image_path)
    results.append(result)

# ✅ GOOD: Parallel processing
from multiprocessing import Pool
with Pool() as pool:
    results = pool.map(process_image, image_paths)
```

---

## 🔥 Common Bottlenecks and Fixes

### Bottleneck 1: Pixel-by-Pixel Operations

**Symptom**: Code with nested loops over image dimensions

**Fix**: Use NumPy broadcasting and vectorization

```python
# Example: Apply gradient
# ❌ Slow
for i in range(h):
    for j in range(w):
        gradient[i, j] = i / h * intensity

# ✅ Fast
i = np.arange(h).reshape(-1, 1)
gradient = i / h * intensity
```

### Bottleneck 2: Repeated Distance Calculations

**Symptom**: `np.sqrt((x - cx)**2 + (y - cy)**2)` in loops

**Fix**: Use meshgrid for vectorized distance calculation

```python
# ✅ Fast distance calculation
y, x = np.indices((h, w))
dist = np.sqrt((x - cx)**2 + (y - cy)**2)
mask = dist < radius
```

### Bottleneck 3: Repeated Image Loading

**Symptom**: Same image loaded multiple times

**Fix**: Implement caching or load once

```python
# ✅ Load once, use many times
images = {path: cv2.imread(path) for path in image_paths}
for processing_step in steps:
    for path in image_paths:
        process(images[path])  # No reload
```

### Bottleneck 4: Sequential Independent Operations

**Symptom**: Processing items one at a time when order doesn't matter

**Fix**: Use multiprocessing

```python
from multiprocessing import Pool

def process_item(item):
    # Processing logic
    return result

# ✅ Parallel processing
with Pool() as pool:
    results = pool.map(process_item, items)
```

---

## 📊 Performance Patterns

### Pattern 1: Coordinate-Based Operations

**Use Case**: Applying effects based on pixel position

```python
# Create coordinate grids
y, x = np.indices((height, width))

# Use in calculations
radial_distance = np.sqrt(x**2 + y**2)
angular_position = np.arctan2(y, x)
gradient = x / width
```

### Pattern 2: Conditional Image Operations

**Use Case**: Apply different values based on conditions

```python
# Use np.where for conditional assignment
mask = distance < radius
image = np.where(mask, bright_value, dark_value)

# Or for more complex conditions
result = np.select(
    [cond1, cond2, cond3],
    [value1, value2, value3],
    default=default_value
)
```

### Pattern 3: Color Channel Operations

**Use Case**: Process RGB channels efficiently

```python
# ❌ Slow: Loop over channels
for c in range(3):
    for i in range(h):
        for j in range(w):
            image[i, j, c] = process(image[i, j, c])

# ✅ Fast: Vectorized
image = process_vectorized(image)
```

### Pattern 4: Batch Image Processing

**Use Case**: Process multiple images with same pipeline

```python
def process_batch_parallel(image_paths, processor, num_workers=None):
    """
    Process multiple images in parallel.
    
    Args:
        image_paths: List of image file paths
        processor: Function that takes image and returns processed image
        num_workers: Number of parallel workers (default: CPU count)
    
    Returns:
        List of processed images
    """
    from multiprocessing import Pool, cpu_count
    
    num_workers = num_workers or max(1, cpu_count() - 1)
    
    def load_and_process(path):
        img = cv2.imread(str(path))
        return processor(img) if img is not None else None
    
    with Pool(num_workers) as pool:
        return pool.map(load_and_process, image_paths)
```

---

## 🧪 Benchmarking Template

Use this template to measure optimization impact:

```python
import time
import numpy as np

def benchmark_function(func, *args, iterations=10, warmup=2):
    """
    Benchmark a function.
    
    Args:
        func: Function to benchmark
        *args: Arguments to pass to function
        iterations: Number of test iterations
        warmup: Number of warmup iterations (excluded from timing)
    
    Returns:
        (mean_time, std_time, result)
    """
    # Warmup
    for _ in range(warmup):
        result = func(*args)
    
    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return np.mean(times), np.std(times), result

# Example usage
def original_function(data):
    # Original implementation
    pass

def optimized_function(data):
    # Optimized implementation
    pass

test_data = np.random.rand(1000, 1000)

time_orig, std_orig, result_orig = benchmark_function(original_function, test_data)
time_opt, std_opt, result_opt = benchmark_function(optimized_function, test_data)

print(f"Original: {time_orig:.4f}s ± {std_orig:.4f}s")
print(f"Optimized: {time_opt:.4f}s ± {std_opt:.4f}s")
print(f"Speedup: {time_orig / time_opt:.1f}x")

# Verify correctness
assert np.allclose(result_orig, result_opt, atol=1e-6), "Results differ!"
```

---

## 🔍 Profiling Tools

### Quick Profiling

```python
# Time a code block
import time
start = time.perf_counter()
# ... code to profile ...
elapsed = time.perf_counter() - start
print(f"Elapsed: {elapsed:.4f}s")
```

### Detailed Profiling

```python
import cProfile
import pstats

# Profile a function
profiler = cProfile.Profile()
profiler.enable()

your_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

### Line Profiling (Install: `pip install line_profiler`)

```python
# Add @profile decorator to function
@profile
def your_function():
    # ... code ...
    pass

# Run with: kernprof -l -v your_script.py
```

---

## ✅ Pre-Commit Checklist

Before committing performance-related changes:

- [ ] Benchmark shows measurable improvement (at least 1.5x)
- [ ] Output correctness verified (visual inspection or unit test)
- [ ] No regression in other tests
- [ ] Added/updated performance test
- [ ] Documented optimization in code comments
- [ ] Updated CHANGELOG with performance note

---

## 📚 Additional Resources

### NumPy Performance
- [NumPy Performance Tips](https://numpy.org/doc/stable/user/c-info.python-as-glue.html)
- [Broadcasting Rules](https://numpy.org/doc/stable/user/basics.broadcasting.html)

### OpenCV Performance
- [OpenCV Optimization](https://docs.opencv.org/4.x/dc/d71/tutorial_py_optimization.html)

### Python Multiprocessing
- [Multiprocessing Guide](https://docs.python.org/3/library/multiprocessing.html)
- [When to Use Threading vs Multiprocessing](https://docs.python.org/3/library/concurrent.futures.html)

### Profiling
- [Python Profilers](https://docs.python.org/3/library/profile.html)
- [line_profiler](https://github.com/pyutils/line_profiler)

---

## 🎓 Example: Complete Optimization

Here's a complete example showing before/after optimization:

```python
# BEFORE: Slow implementation
def apply_radial_gradient_slow(image, center, max_radius, intensity):
    """Slow radial gradient with nested loops"""
    h, w = image.shape[:2]
    gradient = np.zeros((h, w), dtype=np.float32)
    
    cx, cy = center
    for i in range(h):
        for j in range(w):
            dist = np.sqrt((j - cx)**2 + (i - cy)**2)
            if dist < max_radius:
                gradient[i, j] = (1 - dist / max_radius) * intensity
    
    gradient_3ch = cv2.cvtColor((gradient * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    return cv2.addWeighted(image, 1.0, gradient_3ch, 0.5, 0)

# AFTER: Fast vectorized implementation
def apply_radial_gradient_fast(image, center, max_radius, intensity):
    """Fast radial gradient with vectorization"""
    h, w = image.shape[:2]
    cx, cy = center
    
    # Vectorized distance calculation
    y, x = np.indices((h, w))
    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    
    # Vectorized gradient calculation
    gradient = np.where(
        dist < max_radius,
        (1 - dist / max_radius) * intensity,
        0
    ).astype(np.float32)
    
    gradient_3ch = cv2.merge([gradient] * 3) * 255
    return cv2.addWeighted(image, 1.0, gradient_3ch.astype(np.uint8), 0.5, 0)

# Benchmark
test_image = np.random.randint(0, 255, (500, 350, 3), dtype=np.uint8)
center = (175, 250)
max_radius = 150
intensity = 0.8

time_slow, _, result_slow = benchmark_function(
    apply_radial_gradient_slow, test_image, center, max_radius, intensity
)
time_fast, _, result_fast = benchmark_function(
    apply_radial_gradient_fast, test_image, center, max_radius, intensity
)

print(f"Slow: {time_slow:.4f}s")
print(f"Fast: {time_fast:.4f}s")
print(f"Speedup: {time_slow / time_fast:.1f}x")

# Verify correctness
assert np.allclose(result_slow, result_fast, atol=1), "Results differ!"
print("✅ Results match!")
```

---

**Remember**: Premature optimization is the root of all evil. Profile first, optimize what matters!

---

**Questions?** Check:
- `docs/PERFORMANCE_ANALYSIS.md` - Detailed analysis
- `docs/OPTIMIZATION_RECOMMENDATIONS.md` - Complete recommendations
- `tests/test_holographic_performance.py` - Performance test examples
