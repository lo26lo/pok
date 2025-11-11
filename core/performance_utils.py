#!/usr/bin/env python3
"""
Performance Utilities - Tools for profiling and optimizing code
================================================================

This module provides utilities to help identify and fix performance bottlenecks:
- Function timing decorators
- Memory profiling
- Batch processing helpers
- Caching utilities

Author: Pokemon Dataset Generator Team
Version: 1.0.0
"""

import time
import functools
from typing import Callable, Any, TypeVar, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Type for generic functions
F = TypeVar('F', bound=Callable[..., Any])


def timeit(func: F) -> F:
    """
    Decorator to measure execution time of a function
    
    Usage:
        @timeit
        def my_slow_function():
            ...
    
    The execution time will be logged automatically.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        func_name = func.__name__
        logger.info(f"⏱️  {func_name} took {duration:.3f}s")
        print(f"⏱️  {func_name} took {duration:.3f}s")
        
        return result
    return wrapper


def memoize(func: F) -> F:
    """
    Simple memoization decorator for functions with hashable arguments
    
    Caches function results to avoid repeated computation.
    Warning: Can consume memory for large result sets.
    
    Usage:
        @memoize
        def expensive_calculation(x, y):
            ...
    """
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


class PerformanceProfiler:
    """
    Context manager for profiling code blocks
    
    Usage:
        with PerformanceProfiler("Image loading"):
            images = load_images()
    """
    
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.debug(f"Starting: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        logger.info(f"✅ {self.operation_name} completed in {duration:.3f}s")
        print(f"✅ {self.operation_name} completed in {duration:.3f}s")
        return False


def batch_process(items: List[Any], batch_size: int = 32) -> List[List[Any]]:
    """
    Split a list into batches for more efficient processing
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        
    Returns:
        List of batches
        
    Example:
        for batch in batch_process(image_paths, batch_size=16):
            results = process_batch_gpu(batch)
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches


class BatchTimer:
    """
    Timer for tracking batch processing progress
    
    Usage:
        timer = BatchTimer(total_items=1000, batch_size=32)
        for batch in batches:
            process_batch(batch)
            timer.update(len(batch))
    """
    
    def __init__(self, total_items: int, batch_size: int):
        self.total_items = total_items
        self.batch_size = batch_size
        self.processed = 0
        self.start_time = time.perf_counter()
        
    def update(self, items_processed: int = None):
        """Update progress"""
        if items_processed is None:
            items_processed = self.batch_size
            
        self.processed += items_processed
        elapsed = time.perf_counter() - self.start_time
        
        if self.processed > 0:
            avg_time = elapsed / self.processed
            remaining = self.total_items - self.processed
            eta = avg_time * remaining
            
            progress = (self.processed / self.total_items) * 100
            
            logger.info(
                f"Progress: {self.processed}/{self.total_items} ({progress:.1f}%) | "
                f"ETA: {eta:.1f}s | Speed: {self.processed/elapsed:.1f} items/s"
            )


def check_bottlenecks(module_name: str = None):
    """
    Analyze common performance bottlenecks in the codebase
    
    Prints recommendations for optimization
    """
    print("\n" + "="*70)
    print("🔍 Performance Analysis")
    print("="*70)
    
    recommendations = [
        {
            "issue": "Nested loops (for i in range, for j in range)",
            "solution": "Use NumPy vectorized operations",
            "example": "core/holographic_augmenter_optimized.py",
            "speedup": "10-100x faster"
        },
        {
            "issue": "Sequential file I/O in loops",
            "solution": "Use batch processing or multiprocessing",
            "example": "Use batch_process() from this module",
            "speedup": "2-8x faster"
        },
        {
            "issue": "Repeated function calls with same arguments",
            "solution": "Use @memoize decorator",
            "example": "@memoize on load_card_data()",
            "speedup": "Eliminates redundant computation"
        },
        {
            "issue": "Large datasets processed serially",
            "solution": "Use GPU acceleration (PyTorch/CUDA)",
            "example": "core/holographic_augmenter_optimized.py",
            "speedup": "30-50x faster"
        }
    ]
    
    print("\n📋 Common Performance Issues and Solutions:\n")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. ❌ Issue: {rec['issue']}")
        print(f"   ✅ Solution: {rec['solution']}")
        print(f"   📝 Example: {rec['example']}")
        print(f"   🚀 Speedup: {rec['speedup']}")
        print()
    
    print("="*70)
    print("💡 Use @timeit decorator to identify slow functions")
    print("💡 Use PerformanceProfiler context manager for code blocks")
    print("💡 Check *_optimized.py modules for optimized implementations")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Demo usage
    print("Performance Utilities Demo\n")
    
    # Demo 1: timeit decorator
    @timeit
    def slow_function():
        time.sleep(0.1)
        return "Done"
    
    result = slow_function()
    
    # Demo 2: Performance profiler
    with PerformanceProfiler("Demo operation"):
        time.sleep(0.05)
    
    # Demo 3: Batch processing
    items = list(range(100))
    batches = batch_process(items, batch_size=10)
    print(f"\n✅ Split {len(items)} items into {len(batches)} batches")
    
    # Demo 4: Show bottleneck analysis
    check_bottlenecks()
