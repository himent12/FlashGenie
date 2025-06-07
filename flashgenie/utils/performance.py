"""
Performance monitoring and optimization utilities for FlashGenie.

This module provides tools for monitoring performance, profiling,
and optimizing resource usage.
"""

import time
import functools
import threading
import psutil
import gc
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    memory_usage: int
    cpu_usage: float
    timestamp: datetime
    function_name: str
    args_count: int
    result_size: Optional[int] = None


class PerformanceMonitor:
    """Monitors and tracks performance metrics."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        self.logger = logging.getLogger(__name__)
        self.metrics: List[PerformanceMetrics] = []
        self.enabled = True
        self._lock = threading.Lock()
        
        # Performance thresholds
        self.thresholds = {
            'execution_time': 1.0,  # seconds
            'memory_usage': 100 * 1024 * 1024,  # 100MB
            'cpu_usage': 80.0,  # percent
        }
    
    def record_metrics(self, metrics: PerformanceMetrics) -> None:
        """Record performance metrics."""
        if not self.enabled:
            return
        
        with self._lock:
            self.metrics.append(metrics)
            
            # Keep only recent metrics (last 1000)
            if len(self.metrics) > 1000:
                self.metrics = self.metrics[-1000:]
        
        # Check thresholds and log warnings
        self._check_thresholds(metrics)
    
    def _check_thresholds(self, metrics: PerformanceMetrics) -> None:
        """Check if metrics exceed thresholds."""
        if metrics.execution_time > self.thresholds['execution_time']:
            self.logger.warning(
                f"Slow execution detected: {metrics.function_name} took "
                f"{metrics.execution_time:.2f}s"
            )
        
        if metrics.memory_usage > self.thresholds['memory_usage']:
            self.logger.warning(
                f"High memory usage detected: {metrics.function_name} used "
                f"{metrics.memory_usage / 1024 / 1024:.2f}MB"
            )
        
        if metrics.cpu_usage > self.thresholds['cpu_usage']:
            self.logger.warning(
                f"High CPU usage detected: {metrics.function_name} used "
                f"{metrics.cpu_usage:.1f}% CPU"
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {"message": "No performance data available"}
        
        with self._lock:
            metrics = self.metrics.copy()
        
        # Calculate statistics
        execution_times = [m.execution_time for m in metrics]
        memory_usages = [m.memory_usage for m in metrics]
        cpu_usages = [m.cpu_usage for m in metrics]
        
        return {
            "total_calls": len(metrics),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "max_execution_time": max(execution_times),
            "avg_memory_usage": sum(memory_usages) / len(memory_usages),
            "max_memory_usage": max(memory_usages),
            "avg_cpu_usage": sum(cpu_usages) / len(cpu_usages),
            "max_cpu_usage": max(cpu_usages),
            "slowest_functions": self._get_slowest_functions(metrics),
            "memory_intensive_functions": self._get_memory_intensive_functions(metrics)
        }
    
    def _get_slowest_functions(self, metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Get the slowest functions."""
        function_times = {}
        for metric in metrics:
            if metric.function_name not in function_times:
                function_times[metric.function_name] = []
            function_times[metric.function_name].append(metric.execution_time)
        
        # Calculate average times
        avg_times = {
            func: sum(times) / len(times)
            for func, times in function_times.items()
        }
        
        # Sort by average time
        sorted_functions = sorted(avg_times.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"function": func, "avg_time": avg_time}
            for func, avg_time in sorted_functions[:5]
        ]
    
    def _get_memory_intensive_functions(self, metrics: List[PerformanceMetrics]) -> List[Dict[str, Any]]:
        """Get the most memory-intensive functions."""
        function_memory = {}
        for metric in metrics:
            if metric.function_name not in function_memory:
                function_memory[metric.function_name] = []
            function_memory[metric.function_name].append(metric.memory_usage)
        
        # Calculate average memory usage
        avg_memory = {
            func: sum(usages) / len(usages)
            for func, usages in function_memory.items()
        }
        
        # Sort by average memory usage
        sorted_functions = sorted(avg_memory.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"function": func, "avg_memory": avg_mem / 1024 / 1024}  # Convert to MB
            for func, avg_mem in sorted_functions[:5]
        ]
    
    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        with self._lock:
            self.metrics.clear()
        self.logger.info("Performance metrics cleared")


# Global performance monitor
performance_monitor = PerformanceMonitor()


def monitor_performance(func: Callable) -> Callable:
    """
    Decorator to monitor function performance.
    
    Args:
        func: Function to monitor
        
    Returns:
        Wrapped function with performance monitoring
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not performance_monitor.enabled:
            return func(*args, **kwargs)
        
        # Get initial metrics
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Calculate metrics
            end_time = time.time()
            end_memory = process.memory_info().rss
            end_cpu = process.cpu_percent()
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = max(end_cpu - start_cpu, 0)  # Ensure non-negative
            
            # Calculate result size if possible
            result_size = None
            try:
                if hasattr(result, '__len__'):
                    result_size = len(result)
                elif hasattr(result, '__sizeof__'):
                    result_size = result.__sizeof__()
            except:
                pass
            
            # Record metrics
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                timestamp=datetime.now(),
                function_name=f"{func.__module__}.{func.__name__}",
                args_count=len(args) + len(kwargs),
                result_size=result_size
            )
            
            performance_monitor.record_metrics(metrics)
            
            return result
            
        except Exception as e:
            # Still record metrics for failed calls
            end_time = time.time()
            execution_time = end_time - start_time
            
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=0,
                cpu_usage=0,
                timestamp=datetime.now(),
                function_name=f"{func.__module__}.{func.__name__}",
                args_count=len(args) + len(kwargs)
            )
            
            performance_monitor.record_metrics(metrics)
            raise
    
    return wrapper


class MemoryOptimizer:
    """Provides memory optimization utilities."""
    
    def __init__(self):
        """Initialize the memory optimizer."""
        self.logger = logging.getLogger(__name__)
    
    def optimize_memory(self) -> Dict[str, Any]:
        """
        Perform memory optimization.
        
        Returns:
            Dictionary with optimization results
        """
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_freed = initial_memory - final_memory
        
        result = {
            "initial_memory_mb": initial_memory / 1024 / 1024,
            "final_memory_mb": final_memory / 1024 / 1024,
            "memory_freed_mb": memory_freed / 1024 / 1024,
            "objects_collected": collected
        }
        
        self.logger.info(f"Memory optimization completed: freed {memory_freed / 1024 / 1024:.2f}MB")
        return result
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage information."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }
    
    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure."""
        memory = psutil.virtual_memory()
        return memory.percent > 85  # Consider 85% as high memory usage


class CacheManager:
    """Manages application caches for performance optimization."""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the cache manager.
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self.caches: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def get_cache(self, cache_name: str) -> Dict[str, Any]:
        """Get or create a cache."""
        with self._lock:
            if cache_name not in self.caches:
                self.caches[cache_name] = {}
            return self.caches[cache_name]
    
    def set_cache_item(self, cache_name: str, key: str, value: Any) -> None:
        """Set an item in the cache."""
        cache = self.get_cache(cache_name)
        
        with self._lock:
            # Remove oldest items if cache is full
            if len(cache) >= self.max_size:
                # Remove 20% of oldest items
                items_to_remove = max(1, len(cache) // 5)
                for _ in range(items_to_remove):
                    cache.pop(next(iter(cache)), None)
            
            cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'access_count': 0
            }
    
    def get_cache_item(self, cache_name: str, key: str) -> Optional[Any]:
        """Get an item from the cache."""
        cache = self.get_cache(cache_name)
        
        with self._lock:
            if key in cache:
                cache[key]['access_count'] += 1
                return cache[key]['value']
            return None
    
    def clear_cache(self, cache_name: Optional[str] = None) -> None:
        """Clear cache(s)."""
        with self._lock:
            if cache_name:
                if cache_name in self.caches:
                    self.caches[cache_name].clear()
                    self.logger.info(f"Cache '{cache_name}' cleared")
            else:
                self.caches.clear()
                self.logger.info("All caches cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            stats = {}
            for cache_name, cache in self.caches.items():
                total_access = sum(item['access_count'] for item in cache.values())
                stats[cache_name] = {
                    'size': len(cache),
                    'total_accesses': total_access,
                    'avg_accesses': total_access / len(cache) if cache else 0
                }
            return stats


# Global instances
memory_optimizer = MemoryOptimizer()
cache_manager = CacheManager()


def cached(cache_name: str, ttl: int = 3600):
    """
    Decorator to cache function results.
    
    Args:
        cache_name: Name of the cache to use
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get_cache_item(cache_name, key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set_cache_item(cache_name, key, result)
            
            return result
        
        return wrapper
    return decorator
