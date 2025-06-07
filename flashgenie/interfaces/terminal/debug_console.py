"""
Developer Tools and Debug Console for FlashGenie v1.8.3.

This module provides interactive debugging tools, performance monitoring,
and development utilities for the Rich Terminal UI.
"""

import sys
import time
import traceback
import threading
import psutil
import gc
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import deque

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.tree import Tree
from rich.syntax import Syntax
from rich.traceback import Traceback


@dataclass
class PerformanceMetric:
    """Performance metric data point."""
    timestamp: datetime
    cpu_percent: float
    memory_mb: float
    function_name: str
    execution_time: float


@dataclass
class LogEntry:
    """Log entry for the debug console."""
    timestamp: datetime
    level: str
    message: str
    module: str
    function: str
    line_number: int


class DebugConsole:
    """
    Interactive debugging console for FlashGenie developers.
    
    Provides real-time performance monitoring, log streaming,
    object inspection, and debugging utilities.
    """
    
    def __init__(self, console: Console):
        """
        Initialize the debug console.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.enabled = False
        self.performance_metrics: deque = deque(maxlen=1000)
        self.log_entries: deque = deque(maxlen=500)
        self.watched_objects: Dict[str, Any] = {}
        self.breakpoints: List[str] = []
        
        # Performance monitoring
        self.process = psutil.Process()
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_active = False
        
        # Profiling
        self.profiling_enabled = False
        self.function_timings: Dict[str, List[float]] = {}
    
    def enable(self) -> None:
        """Enable debug mode and start monitoring."""
        self.enabled = True
        self.start_performance_monitoring()
        self.show_debug_panel()
    
    def disable(self) -> None:
        """Disable debug mode and stop monitoring."""
        self.enabled = False
        self.stop_performance_monitoring()
    
    def start_performance_monitoring(self) -> None:
        """Start background performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitoring_thread.start()
    
    def stop_performance_monitoring(self) -> None:
        """Stop background performance monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
    
    def _monitor_performance(self) -> None:
        """Background thread for performance monitoring."""
        while self.monitoring_active:
            try:
                # Collect metrics
                cpu_percent = self.process.cpu_percent()
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                metric = PerformanceMetric(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    function_name="system",
                    execution_time=0.0
                )
                
                self.performance_metrics.append(metric)
                
                time.sleep(1.0)  # Update every second
                
            except Exception:
                # Ignore errors in monitoring thread
                pass
    
    def show_debug_panel(self) -> None:
        """Display the main debug panel."""
        layout = self.create_debug_layout()
        
        debug_panel = Panel(
            layout,
            title="🐛 Debug Console - FlashGenie v1.8.3",
            border_style="bright_magenta",
            padding=(1, 2)
        )
        
        self.console.print(debug_panel)
    
    def create_debug_layout(self) -> Layout:
        """Create the debug console layout."""
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="performance", size=8),
            Layout(name="logs", size=10),
            Layout(name="objects")
        )
        
        # Performance section
        perf_content = self.get_performance_summary()
        layout["performance"].update(Panel(
            perf_content,
            title="📊 Performance Metrics",
            border_style="bright_green"
        ))
        
        # Logs section
        log_content = self.get_recent_logs()
        layout["logs"].update(Panel(
            log_content,
            title="📝 Recent Logs",
            border_style="bright_blue"
        ))
        
        # Objects section
        obj_content = self.get_watched_objects()
        layout["objects"].update(Panel(
            obj_content,
            title="🔍 Watched Objects",
            border_style="bright_yellow"
        ))
        
        return layout
    
    def get_performance_summary(self) -> Group:
        """Get performance metrics summary."""
        if not self.performance_metrics:
            return Group(Text("No performance data available", style="dim"))
        
        # Get recent metrics
        recent_metrics = list(self.performance_metrics)[-10:]
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        current_memory = recent_metrics[-1].memory_mb if recent_metrics else 0
        
        # Memory trend
        if len(recent_metrics) >= 2:
            memory_trend = recent_metrics[-1].memory_mb - recent_metrics[0].memory_mb
            trend_indicator = "↑" if memory_trend > 0 else "↓" if memory_trend < 0 else "→"
            trend_style = "bright_red" if memory_trend > 10 else "bright_green" if memory_trend < -5 else "bright_yellow"
        else:
            trend_indicator = "→"
            trend_style = "bright_yellow"
        
        content = []
        
        # Current stats
        content.append(Text(f"CPU Usage: {avg_cpu:.1f}%", style="bright_cyan"))
        content.append(Text(f"Memory: {current_memory:.1f} MB {trend_indicator}", style=f"bright_white {trend_style}"))
        content.append(Text(f"Average Memory: {avg_memory:.1f} MB", style="dim"))
        
        # Function timings
        if self.function_timings:
            content.append(Text(""))
            content.append(Text("Slowest Functions:", style="bright_yellow"))
            
            # Sort by average time
            sorted_functions = sorted(
                self.function_timings.items(),
                key=lambda x: sum(x[1]) / len(x[1]),
                reverse=True
            )
            
            for func_name, timings in sorted_functions[:3]:
                avg_time = sum(timings) / len(timings)
                content.append(Text(f"  {func_name}: {avg_time:.3f}s", style="dim"))
        
        return Group(*content)
    
    def get_recent_logs(self) -> Group:
        """Get recent log entries."""
        if not self.log_entries:
            return Group(Text("No log entries available", style="dim"))
        
        content = []
        recent_logs = list(self.log_entries)[-8:]  # Show last 8 logs
        
        for log in recent_logs:
            timestamp = log.timestamp.strftime("%H:%M:%S")
            
            # Color by log level
            level_style = {
                "DEBUG": "dim",
                "INFO": "bright_blue",
                "WARNING": "bright_yellow",
                "ERROR": "bright_red",
                "CRITICAL": "bold bright_red"
            }.get(log.level, "white")
            
            log_text = Text()
            log_text.append(f"[{timestamp}] ", style="dim")
            log_text.append(f"{log.level:8}", style=level_style)
            log_text.append(f" {log.message}", style="white")
            
            content.append(log_text)
        
        return Group(*content)
    
    def get_watched_objects(self) -> Group:
        """Get information about watched objects."""
        if not self.watched_objects:
            return Group(Text("No objects being watched", style="dim"))
        
        content = []
        
        for name, obj in self.watched_objects.items():
            obj_text = Text()
            obj_text.append(f"{name}: ", style="bright_white")
            obj_text.append(f"{type(obj).__name__}", style="bright_cyan")
            
            # Add object details
            if hasattr(obj, '__len__'):
                obj_text.append(f" (length: {len(obj)})", style="dim")
            
            content.append(obj_text)
        
        return Group(*content)
    
    def add_log_entry(self, level: str, message: str, module: str = "", function: str = "", line_number: int = 0) -> None:
        """Add a log entry to the debug console."""
        if not self.enabled:
            return
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            module=module,
            function=function,
            line_number=line_number
        )
        
        self.log_entries.append(entry)
    
    def watch_object(self, name: str, obj: Any) -> None:
        """Add an object to the watch list."""
        self.watched_objects[name] = obj
    
    def unwatch_object(self, name: str) -> None:
        """Remove an object from the watch list."""
        self.watched_objects.pop(name, None)
    
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile function execution time."""
        def wrapper(*args, **kwargs):
            if not self.profiling_enabled:
                return func(*args, **kwargs)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                func_name = f"{func.__module__}.{func.__name__}"
                
                # Store timing
                if func_name not in self.function_timings:
                    self.function_timings[func_name] = []
                self.function_timings[func_name].append(execution_time)
                
                # Keep only recent timings
                if len(self.function_timings[func_name]) > 100:
                    self.function_timings[func_name] = self.function_timings[func_name][-100:]
                
                # Add performance metric
                if self.enabled:
                    metric = PerformanceMetric(
                        timestamp=datetime.now(),
                        cpu_percent=0.0,  # Will be updated by monitoring thread
                        memory_mb=0.0,    # Will be updated by monitoring thread
                        function_name=func_name,
                        execution_time=execution_time
                    )
                    self.performance_metrics.append(metric)
        
        return wrapper
    
    def inspect_object(self, obj: Any, name: str = "object") -> None:
        """Inspect an object and display its properties."""
        inspection_content = []
        
        # Basic info
        inspection_content.append(Text(f"Object: {name}", style="bold bright_white"))
        inspection_content.append(Text(f"Type: {type(obj).__name__}", style="bright_cyan"))
        inspection_content.append(Text(f"Module: {type(obj).__module__}", style="dim"))
        
        # Size info
        if hasattr(obj, '__len__'):
            inspection_content.append(Text(f"Length: {len(obj)}", style="bright_yellow"))
        
        if hasattr(obj, '__sizeof__'):
            size_bytes = obj.__sizeof__()
            inspection_content.append(Text(f"Size: {size_bytes} bytes", style="bright_yellow"))
        
        # Attributes
        inspection_content.append(Text(""))
        inspection_content.append(Text("Attributes:", style="bright_green"))
        
        attrs = [attr for attr in dir(obj) if not attr.startswith('_')][:10]  # Show first 10
        for attr in attrs:
            try:
                value = getattr(obj, attr)
                attr_text = Text()
                attr_text.append(f"  {attr}: ", style="bright_white")
                attr_text.append(f"{type(value).__name__}", style="bright_cyan")
                inspection_content.append(attr_text)
            except Exception:
                inspection_content.append(Text(f"  {attr}: <error accessing>", style="dim"))
        
        if len(dir(obj)) > 10:
            inspection_content.append(Text(f"  ... and {len(dir(obj)) - 10} more", style="dim"))
        
        # Display inspection panel
        inspection_panel = Panel(
            Group(*inspection_content),
            title=f"🔍 Object Inspector: {name}",
            border_style="bright_magenta",
            padding=(1, 2)
        )
        
        self.console.print(inspection_panel)
    
    def show_traceback(self, exc: Exception) -> None:
        """Show a rich traceback for an exception."""
        tb = Traceback.from_exception(type(exc), exc, exc.__traceback__)
        
        traceback_panel = Panel(
            tb,
            title="🚨 Exception Traceback",
            border_style="bright_red",
            padding=(1, 2)
        )
        
        self.console.print(traceback_panel)
    
    def memory_profile(self) -> Dict[str, Any]:
        """Get detailed memory profiling information."""
        # Force garbage collection
        collected = gc.collect()
        
        # Get memory info
        memory_info = self.process.memory_info()
        
        # Get object counts
        object_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
        
        # Sort by count
        top_objects = sorted(object_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "objects_collected": collected,
            "total_objects": len(gc.get_objects()),
            "top_object_types": top_objects
        }
    
    def enable_profiling(self) -> None:
        """Enable function profiling."""
        self.profiling_enabled = True
        self.add_log_entry("INFO", "Function profiling enabled", "debug_console")
    
    def disable_profiling(self) -> None:
        """Disable function profiling."""
        self.profiling_enabled = False
        self.add_log_entry("INFO", "Function profiling disabled", "debug_console")
