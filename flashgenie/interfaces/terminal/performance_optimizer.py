"""
Performance Optimization System for FlashGenie v1.8.4.

This module provides comprehensive performance monitoring, optimization,
and resource management for the Rich Terminal UI.
"""

import asyncio
import threading
import time
import gc
import sys
import psutil
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import weakref
import functools

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, TaskID
from rich.live import Live


@dataclass
class PerformanceThresholds:
    """Performance threshold configuration."""
    max_memory_mb: float = 500.0
    max_cpu_percent: float = 80.0
    max_execution_time: float = 1.0
    max_render_time: float = 0.1
    gc_threshold_objects: int = 10000
    cache_max_size: int = 1000
    background_task_limit: int = 5


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""
    timestamp: datetime
    memory_usage_mb: float
    cpu_percent: float
    execution_time: float
    render_time: float
    active_objects: int
    cache_hit_ratio: float
    background_tasks: int


class AsyncTaskManager:
    """Manages asynchronous operations with progress feedback."""
    
    def __init__(self, console: Console, max_concurrent: int = 5):
        """
        Initialize async task manager.
        
        Args:
            console: Rich console instance
            max_concurrent: Maximum concurrent tasks
        """
        self.console = console
        self.max_concurrent = max_concurrent
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_progress: Dict[str, float] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.progress_display: Optional[Live] = None
    
    async def run_with_progress(
        self, 
        task_func: Callable,
        task_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Run async task with progress feedback.
        
        Args:
            task_func: Async function to run
            task_name: Human-readable task name
            *args: Task function arguments
            **kwargs: Task function keyword arguments
            
        Returns:
            Task result
        """
        async with self.semaphore:
            task_id = f"{task_name}_{int(time.time())}"
            self.task_progress[task_id] = 0.0
            
            try:
                # Create progress callback
                def update_progress(progress: float):
                    self.task_progress[task_id] = min(100.0, max(0.0, progress))
                
                # Add progress callback to kwargs if task supports it
                if 'progress_callback' in task_func.__code__.co_varnames:
                    kwargs['progress_callback'] = update_progress
                
                # Run the task
                result = await task_func(*args, **kwargs)
                self.task_progress[task_id] = 100.0
                
                return result
                
            finally:
                # Clean up
                self.task_progress.pop(task_id, None)
    
    def start_progress_display(self) -> None:
        """Start live progress display."""
        if self.progress_display:
            return
        
        def create_progress_layout():
            if not self.task_progress:
                return Panel(Text("No active tasks", style="dim"), title="📊 Task Progress")
            
            progress_content = []
            for task_id, progress in self.task_progress.items():
                task_name = task_id.split('_')[0]
                progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
                
                progress_text = Text()
                progress_text.append(f"{task_name}: ", style="bright_white")
                progress_text.append(progress_bar, style="bright_blue")
                progress_text.append(f" {progress:.1f}%", style="bright_cyan")
                
                progress_content.append(progress_text)
            
            return Panel(
                Group(*progress_content),
                title="📊 Task Progress",
                border_style="bright_blue"
            )
        
        self.progress_display = Live(create_progress_layout(), refresh_per_second=4)
        self.progress_display.start()
    
    def stop_progress_display(self) -> None:
        """Stop live progress display."""
        if self.progress_display:
            self.progress_display.stop()
            self.progress_display = None


class IntelligentCache:
    """Intelligent caching system with automatic optimization."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize intelligent cache.
        
        Args:
            max_size: Maximum cache size
            ttl_seconds: Time to live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key not in self.cache:
                self.miss_count += 1
                return None
            
            entry = self.cache[key]
            
            # Check TTL
            if datetime.now() - entry['timestamp'] > timedelta(seconds=self.ttl_seconds):
                del self.cache[key]
                del self.access_times[key]
                self.miss_count += 1
                return None
            
            # Update access time
            self.access_times[key] = datetime.now()
            self.hit_count += 1
            
            return entry['value']
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        with self._lock:
            # Clean up if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = {
                'value': value,
                'timestamp': datetime.now(),
                'size': sys.getsizeof(value)
            }
            self.access_times[key] = datetime.now()
    
    def _evict_lru(self) -> None:
        """Evict least recently used items."""
        if not self.access_times:
            return
        
        # Remove 20% of least recently used items
        items_to_remove = max(1, len(self.access_times) // 5)
        
        # Sort by access time
        sorted_items = sorted(self.access_times.items(), key=lambda x: x[1])
        
        for key, _ in sorted_items[:items_to_remove]:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_ratio = self.hit_count / total_requests if total_requests > 0 else 0
        
        total_size = sum(entry['size'] for entry in self.cache.values())
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_ratio': hit_ratio,
            'total_size_bytes': total_size,
            'avg_size_bytes': total_size / len(self.cache) if self.cache else 0
        }
    
    def clear(self) -> None:
        """Clear cache."""
        with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0


class ResourceMonitor:
    """Monitors system resources and triggers optimizations."""
    
    def __init__(self, thresholds: PerformanceThresholds):
        """
        Initialize resource monitor.
        
        Args:
            thresholds: Performance threshold configuration
        """
        self.thresholds = thresholds
        self.metrics_history: deque = deque(maxlen=1000)
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.optimization_callbacks: List[Callable] = []
        
        # System info
        self.process = psutil.Process()
        self.system_memory = psutil.virtual_memory().total / 1024 / 1024  # MB
    
    def start_monitoring(self) -> None:
        """Start resource monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect metrics
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                cpu_percent = self.process.cpu_percent()
                
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    memory_usage_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    execution_time=0.0,  # Will be updated by profiled functions
                    render_time=0.0,     # Will be updated by render operations
                    active_objects=len(gc.get_objects()),
                    cache_hit_ratio=0.0,  # Will be updated by cache
                    background_tasks=threading.active_count() - 1  # Exclude main thread
                )
                
                self.metrics_history.append(metrics)
                
                # Check thresholds and trigger optimizations
                self._check_thresholds(metrics)
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception:
                # Continue monitoring even if there are errors
                time.sleep(1.0)
    
    def _check_thresholds(self, metrics: PerformanceMetrics) -> None:
        """Check if metrics exceed thresholds and trigger optimizations."""
        optimizations_needed = []
        
        if metrics.memory_usage_mb > self.thresholds.max_memory_mb:
            optimizations_needed.append("memory")
        
        if metrics.cpu_percent > self.thresholds.max_cpu_percent:
            optimizations_needed.append("cpu")
        
        if metrics.active_objects > self.thresholds.gc_threshold_objects:
            optimizations_needed.append("garbage_collection")
        
        # Trigger optimizations
        for optimization in optimizations_needed:
            self._trigger_optimization(optimization, metrics)
    
    def _trigger_optimization(self, optimization_type: str, metrics: PerformanceMetrics) -> None:
        """Trigger specific optimization."""
        for callback in self.optimization_callbacks:
            try:
                callback(optimization_type, metrics)
            except Exception:
                # Don't let callback errors stop monitoring
                pass
    
    def add_optimization_callback(self, callback: Callable) -> None:
        """Add optimization callback."""
        self.optimization_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        recent_metrics = list(self.metrics_history)[-60:]  # Last minute
        
        return {
            "current_memory_mb": recent_metrics[-1].memory_usage_mb,
            "avg_memory_mb": sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics),
            "max_memory_mb": max(m.memory_usage_mb for m in recent_metrics),
            "current_cpu_percent": recent_metrics[-1].cpu_percent,
            "avg_cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            "active_objects": recent_metrics[-1].active_objects,
            "background_tasks": recent_metrics[-1].background_tasks,
            "memory_threshold_exceeded": recent_metrics[-1].memory_usage_mb > self.thresholds.max_memory_mb,
            "cpu_threshold_exceeded": recent_metrics[-1].cpu_percent > self.thresholds.max_cpu_percent
        }


class PerformanceOptimizer:
    """
    Main performance optimization coordinator.
    
    Manages all performance optimization features including async operations,
    caching, resource monitoring, and automatic optimizations.
    """
    
    def __init__(self, console: Console):
        """
        Initialize performance optimizer.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.thresholds = PerformanceThresholds()
        self.cache = IntelligentCache()
        self.resource_monitor = ResourceMonitor(self.thresholds)
        self.async_manager = AsyncTaskManager(console)
        
        # Register optimization callbacks
        self.resource_monitor.add_optimization_callback(self._handle_optimization)
        
        # Start monitoring
        self.resource_monitor.start_monitoring()
    
    def _handle_optimization(self, optimization_type: str, metrics: PerformanceMetrics) -> None:
        """Handle optimization triggers."""
        if optimization_type == "memory":
            self.optimize_memory()
        elif optimization_type == "cpu":
            self.optimize_cpu_usage()
        elif optimization_type == "garbage_collection":
            self.force_garbage_collection()
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        initial_memory = self.resource_monitor.process.memory_info().rss / 1024 / 1024
        
        # Clear caches
        cache_size_before = self.cache.get_stats()['size']
        self.cache.clear()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get final memory
        final_memory = self.resource_monitor.process.memory_info().rss / 1024 / 1024
        memory_freed = initial_memory - final_memory
        
        result = {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_freed_mb": memory_freed,
            "cache_entries_cleared": cache_size_before,
            "objects_collected": collected
        }
        
        return result
    
    def optimize_cpu_usage(self) -> None:
        """Optimize CPU usage by reducing background tasks."""
        # This could involve pausing non-essential background operations
        pass
    
    def force_garbage_collection(self) -> int:
        """Force garbage collection and return number of objects collected."""
        return gc.collect()
    
    def cached_operation(self, cache_key: str, ttl: int = 3600):
        """Decorator for caching operation results."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Try cache first
                result = self.cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                self.cache.set(cache_key, result)
                
                return result
            return wrapper
        return decorator
    
    async def run_async_with_progress(self, task_func: Callable, task_name: str, *args, **kwargs) -> Any:
        """Run async operation with progress feedback."""
        return await self.async_manager.run_with_progress(task_func, task_name, *args, **kwargs)
    
    def get_performance_dashboard(self) -> Panel:
        """Get performance dashboard panel."""
        metrics_summary = self.resource_monitor.get_metrics_summary()
        cache_stats = self.cache.get_stats()
        
        dashboard_content = []
        
        # Memory section
        memory_text = Text()
        memory_text.append("Memory: ", style="bright_white")
        memory_text.append(f"{metrics_summary.get('current_memory_mb', 0):.1f} MB", style="bright_cyan")
        if metrics_summary.get('memory_threshold_exceeded', False):
            memory_text.append(" ⚠️", style="bright_red")
        dashboard_content.append(memory_text)
        
        # CPU section
        cpu_text = Text()
        cpu_text.append("CPU: ", style="bright_white")
        cpu_text.append(f"{metrics_summary.get('current_cpu_percent', 0):.1f}%", style="bright_cyan")
        if metrics_summary.get('cpu_threshold_exceeded', False):
            cpu_text.append(" ⚠️", style="bright_red")
        dashboard_content.append(cpu_text)
        
        # Cache section
        cache_text = Text()
        cache_text.append("Cache: ", style="bright_white")
        cache_text.append(f"{cache_stats['size']}/{cache_stats['max_size']} ", style="bright_cyan")
        cache_text.append(f"({cache_stats['hit_ratio']:.1%} hit rate)", style="bright_green")
        dashboard_content.append(cache_text)
        
        # Objects section
        objects_text = Text()
        objects_text.append("Objects: ", style="bright_white")
        objects_text.append(f"{metrics_summary.get('active_objects', 0):,}", style="bright_cyan")
        dashboard_content.append(objects_text)
        
        return Panel(
            Group(*dashboard_content),
            title="⚡ Performance Dashboard",
            border_style="bright_green",
            padding=(1, 2)
        )
    
    def cleanup(self) -> None:
        """Clean up performance optimizer."""
        self.resource_monitor.stop_monitoring()
        self.async_manager.stop_progress_display()
