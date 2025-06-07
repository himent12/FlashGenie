#!/usr/bin/env python3
"""
FlashGenie v1.8.3 Phase 3 Demo - Accessibility & Performance Optimizations

This script demonstrates the Phase 3 enhancements including accessibility features,
performance optimizations, async operations, and intelligent caching.
"""

import sys
import time
import asyncio
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from flashgenie.interfaces.terminal import RichTerminalUI, AccessibilityManager, PerformanceOptimizer
    print("✅ FlashGenie Phase 3 components loaded successfully!")
except ImportError as e:
    print(f"❌ Could not load FlashGenie Phase 3 components: {e}")
    print("Please install dependencies: pip install rich textual prompt-toolkit psutil")
    sys.exit(1)


def demo_accessibility_features():
    """Demo accessibility features and screen reader support."""
    print("\n♿ Demo: Accessibility Features")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Show accessibility status
    ui.show_accessibility_menu()
    
    # Demo different accessibility modes
    accessibility_modes = [
        ("high_contrast", "High Contrast Mode"),
        ("large_text", "Large Text Mode"),
        ("audio", "Audio Feedback Mode")
    ]
    
    for mode, description in accessibility_modes:
        ui.show_info(f"Demonstrating {description}...", "Accessibility Demo")
        ui.enable_accessibility_mode(mode)
        time.sleep(1)
        
        # Show sample content in accessibility mode
        sample_content = f"This is how content appears in {description}"
        accessible_panel = ui.create_accessible_panel(
            sample_content,
            f"{description} Sample",
            "info"
        )
        ui.console.print(accessible_panel)
        time.sleep(2)
        
        ui.disable_accessibility_mode(mode)
    
    # Demo screen reader announcements
    ui.show_info("Demonstrating screen reader announcements...", "Accessibility Demo")
    ui.announce("Welcome to FlashGenie accessibility features")
    ui.announce("Navigation: Use Tab to move between elements")
    ui.announce("Press Enter to activate buttons and links")
    
    ui.show_success("Accessibility features demonstration complete!", "Accessibility Demo")


def demo_performance_optimization():
    """Demo performance monitoring and optimization."""
    print("\n⚡ Demo: Performance Optimization")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Show initial performance dashboard
    ui.show_info("Displaying performance dashboard...", "Performance Demo")
    ui.show_performance_dashboard()
    time.sleep(2)
    
    # Demo memory optimization
    ui.show_info("Running memory optimization...", "Performance Demo")
    
    # Create some objects to optimize
    test_data = []
    for i in range(1000):
        test_data.append({"id": i, "data": f"test_data_{i}" * 10})
    
    ui.watch_object("test_data", test_data)
    
    # Show performance before optimization
    ui.show_performance_dashboard()
    time.sleep(1)
    
    # Run optimization
    optimization_result = ui.optimize_performance()
    
    # Show performance after optimization
    ui.show_performance_dashboard()
    
    # Clean up test data
    del test_data


def demo_intelligent_caching():
    """Demo intelligent caching system."""
    print("\n🧠 Demo: Intelligent Caching")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    # Demo cached operations
    @ui.cached_operation("expensive_calculation", ttl=60)
    def expensive_calculation(n: int) -> int:
        """Simulate an expensive calculation."""
        time.sleep(0.1)  # Simulate work
        return sum(range(n))
    
    ui.show_info("Running expensive calculation (first time - not cached)...", "Caching Demo")
    start_time = time.time()
    result1 = expensive_calculation(1000)
    first_time = time.time() - start_time
    
    ui.show_success(f"Result: {result1}, Time: {first_time:.3f}s", "First Calculation")
    
    ui.show_info("Running same calculation (second time - cached)...", "Caching Demo")
    start_time = time.time()
    result2 = expensive_calculation(1000)
    second_time = time.time() - start_time
    
    ui.show_success(f"Result: {result2}, Time: {second_time:.3f}s", "Cached Calculation")
    
    speedup = first_time / second_time if second_time > 0 else float('inf')
    ui.show_success(f"Cache speedup: {speedup:.1f}x faster!", "Cache Performance")


async def demo_async_operations():
    """Demo async operations with progress feedback."""
    print("\n🔄 Demo: Async Operations")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    async def simulate_data_processing(progress_callback=None):
        """Simulate async data processing with progress updates."""
        total_steps = 10
        for i in range(total_steps):
            await asyncio.sleep(0.2)  # Simulate work
            if progress_callback:
                progress_callback((i + 1) / total_steps * 100)
        return f"Processed {total_steps} items"
    
    async def simulate_file_download(progress_callback=None):
        """Simulate async file download with progress updates."""
        total_chunks = 20
        for i in range(total_chunks):
            await asyncio.sleep(0.1)  # Simulate download
            if progress_callback:
                progress_callback((i + 1) / total_chunks * 100)
        return f"Downloaded {total_chunks} chunks"
    
    ui.show_info("Starting async operations with progress feedback...", "Async Demo")
    
    # Start progress display
    ui.performance.async_manager.start_progress_display()
    
    try:
        # Run multiple async tasks concurrently
        tasks = [
            ui.run_async_task(simulate_data_processing, "Data Processing"),
            ui.run_async_task(simulate_file_download, "File Download")
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, result in enumerate(results):
            ui.show_success(f"Task {i+1} completed: {result}", "Async Result")
    
    finally:
        # Stop progress display
        ui.performance.async_manager.stop_progress_display()


def demo_resource_monitoring():
    """Demo real-time resource monitoring."""
    print("\n📊 Demo: Resource Monitoring")
    print("=" * 40)
    
    ui = RichTerminalUI()
    
    ui.show_info("Monitoring system resources for 10 seconds...", "Resource Monitor")
    
    # Monitor for a short period
    start_time = time.time()
    while time.time() - start_time < 10:
        ui.show_performance_dashboard()
        time.sleep(2)
        
        # Create some load to show monitoring
        if time.time() - start_time > 5:
            # Create memory pressure
            temp_data = [i * "x" * 1000 for i in range(100)]
            time.sleep(0.5)
            del temp_data
    
    ui.show_success("Resource monitoring demonstration complete!", "Resource Monitor")


def interactive_phase3_demo():
    """Run an interactive demo of Phase 3 features."""
    print("\n🎮 Interactive Phase 3 Demo")
    print("=" * 50)
    
    ui = RichTerminalUI()
    
    while True:
        try:
            options = [
                "Accessibility Features Demo",
                "Performance Optimization Demo",
                "Intelligent Caching Demo",
                "Async Operations Demo",
                "Resource Monitoring Demo",
                "Exit Demo"
            ]
            
            print("\n📋 Phase 3 Feature Demo Menu")
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                demo_accessibility_features()
            elif choice == "2":
                demo_performance_optimization()
            elif choice == "3":
                demo_intelligent_caching()
            elif choice == "4":
                print("Running async demo...")
                asyncio.run(demo_async_operations())
            elif choice == "5":
                demo_resource_monitoring()
            elif choice == "6":
                ui.show_success("Thanks for exploring FlashGenie v1.8.3 Phase 3! 🎉", "Demo Complete")
                break
            else:
                ui.show_warning("Invalid choice. Please select 1-6.", "Invalid Input")
                
        except KeyboardInterrupt:
            ui.show_info("Demo interrupted. Goodbye! 👋", "Interrupted")
            break
        except Exception as e:
            ui.show_error(f"Demo error: {e}", "Error")


def main():
    """Main demo function."""
    print("🚀 FlashGenie v1.8.3 Phase 3 Demo")
    print("=" * 50)
    print("Phase 3: Accessibility & Performance Optimizations")
    print("\nThis demo showcases the advanced features added in Phase 3:")
    print("• Comprehensive accessibility features")
    print("• Performance monitoring and optimization")
    print("• Intelligent caching system")
    print("• Async operations with progress feedback")
    print("• Real-time resource monitoring")
    
    try:
        demo_choice = input("\n🎮 Would you like to run the interactive demo? (y/n): ").strip().lower()
        if demo_choice in ['y', 'yes']:
            interactive_phase3_demo()
        else:
            print("\n🎬 Running automatic demo sequence...")
            demo_accessibility_features()
            demo_performance_optimization()
            demo_intelligent_caching()
            print("\n🔄 Running async operations demo...")
            asyncio.run(demo_async_operations())
            demo_resource_monitoring()
            
            print("\n✅ Phase 3 demo completed successfully!")
            print("🎉 FlashGenie v1.8.3 Phase 3 is ready to provide world-class accessibility and performance!")
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")


if __name__ == "__main__":
    main()
