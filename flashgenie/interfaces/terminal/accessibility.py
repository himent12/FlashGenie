"""
Accessibility System for FlashGenie v1.8.4.

This module provides comprehensive accessibility features including screen reader support,
keyboard navigation, audio feedback, and visual accessibility options.
"""

import os
import sys
import platform
import subprocess
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time

from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel


class AccessibilityMode(Enum):
    """Accessibility mode options."""
    NORMAL = "normal"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SCREEN_READER = "screen_reader"
    AUDIO_FEEDBACK = "audio_feedback"


@dataclass
class AccessibilitySettings:
    """Accessibility configuration settings."""
    screen_reader_enabled: bool = False
    high_contrast_mode: bool = False
    large_text_mode: bool = False
    audio_feedback_enabled: bool = False
    keyboard_navigation_only: bool = False
    reduced_motion: bool = False
    text_size_multiplier: float = 1.0
    announcement_delay: float = 0.5
    skip_animations: bool = False


class ScreenReaderDetector:
    """Detects and interfaces with screen readers."""
    
    def __init__(self):
        """Initialize screen reader detection."""
        self.detected_readers: List[str] = []
        self.active_reader: Optional[str] = None
        
    def detect_screen_readers(self) -> List[str]:
        """
        Detect available screen readers on the system.
        
        Returns:
            List of detected screen reader names
        """
        readers = []
        system = platform.system().lower()
        
        if system == "windows":
            readers.extend(self._detect_windows_readers())
        elif system == "darwin":  # macOS
            readers.extend(self._detect_macos_readers())
        elif system == "linux":
            readers.extend(self._detect_linux_readers())
        
        self.detected_readers = readers
        return readers
    
    def _detect_windows_readers(self) -> List[str]:
        """Detect Windows screen readers."""
        readers = []
        
        # Check for NVDA
        if self._check_process("nvda.exe"):
            readers.append("NVDA")
        
        # Check for JAWS
        if self._check_process("jfw.exe"):
            readers.append("JAWS")
        
        # Check for Narrator (built-in)
        if self._check_process("narrator.exe"):
            readers.append("Narrator")
        
        # Check environment variables
        if os.environ.get("NVDA_RUNNING"):
            readers.append("NVDA")
        
        return readers
    
    def _detect_macos_readers(self) -> List[str]:
        """Detect macOS screen readers."""
        readers = []
        
        # Check for VoiceOver
        try:
            result = subprocess.run(
                ["defaults", "read", "com.apple.universalaccess", "voiceOverOnOffKey"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                readers.append("VoiceOver")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return readers
    
    def _detect_linux_readers(self) -> List[str]:
        """Detect Linux screen readers."""
        readers = []
        
        # Check for Orca
        if self._check_process("orca"):
            readers.append("Orca")
        
        # Check for Speakup
        if os.path.exists("/proc/speakup"):
            readers.append("Speakup")
        
        # Check environment variables
        if os.environ.get("ORCA_RUNNING"):
            readers.append("Orca")
        
        return readers
    
    def _check_process(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                    capture_output=True, text=True, timeout=5
                )
                return process_name.lower() in result.stdout.lower()
            else:
                result = subprocess.run(
                    ["pgrep", "-f", process_name],
                    capture_output=True, text=True, timeout=5
                )
                return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def is_screen_reader_active(self) -> bool:
        """Check if any screen reader is currently active."""
        return len(self.detect_screen_readers()) > 0


class AudioFeedbackSystem:
    """Provides audio feedback for accessibility."""
    
    def __init__(self):
        """Initialize audio feedback system."""
        self.enabled = False
        self.volume = 0.5
        self.sound_library = None
        self._initialize_audio()
    
    def _initialize_audio(self) -> None:
        """Initialize audio system."""
        try:
            # Try to import audio libraries
            try:
                import pygame
                pygame.mixer.init()
                self.sound_library = "pygame"
            except ImportError:
                try:
                    import playsound
                    self.sound_library = "playsound"
                except ImportError:
                    # Fallback to system beep
                    self.sound_library = "system"
        except Exception:
            self.sound_library = None
    
    def play_sound(self, sound_type: str) -> None:
        """
        Play accessibility sound.
        
        Args:
            sound_type: Type of sound (success, error, warning, info, navigation)
        """
        if not self.enabled or not self.sound_library:
            return
        
        try:
            if self.sound_library == "system":
                self._play_system_beep(sound_type)
            else:
                # For now, use system beep as fallback
                self._play_system_beep(sound_type)
        except Exception:
            # Silently fail if audio doesn't work
            pass
    
    def _play_system_beep(self, sound_type: str) -> None:
        """Play system beep based on sound type."""
        if platform.system().lower() == "windows":
            import winsound
            frequencies = {
                "success": 800,
                "error": 300,
                "warning": 600,
                "info": 1000,
                "navigation": 1200
            }
            freq = frequencies.get(sound_type, 800)
            winsound.Beep(freq, 200)
        else:
            # Unix-like systems
            print("\a", end="", flush=True)  # Terminal bell
    
    def enable(self) -> None:
        """Enable audio feedback."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable audio feedback."""
        self.enabled = False


class KeyboardNavigationManager:
    """Manages keyboard-only navigation."""
    
    def __init__(self):
        """Initialize keyboard navigation manager."""
        self.navigation_mode = False
        self.current_focus = 0
        self.focusable_elements: List[str] = []
        self.shortcuts: Dict[str, Callable] = {}
    
    def enable_keyboard_navigation(self) -> None:
        """Enable keyboard-only navigation mode."""
        self.navigation_mode = True
    
    def disable_keyboard_navigation(self) -> None:
        """Disable keyboard-only navigation mode."""
        self.navigation_mode = False
    
    def register_focusable_element(self, element_id: str) -> None:
        """Register an element as focusable."""
        if element_id not in self.focusable_elements:
            self.focusable_elements.append(element_id)
    
    def navigate_next(self) -> str:
        """Navigate to next focusable element."""
        if not self.focusable_elements:
            return ""
        
        self.current_focus = (self.current_focus + 1) % len(self.focusable_elements)
        return self.focusable_elements[self.current_focus]
    
    def navigate_previous(self) -> str:
        """Navigate to previous focusable element."""
        if not self.focusable_elements:
            return ""
        
        self.current_focus = (self.current_focus - 1) % len(self.focusable_elements)
        return self.focusable_elements[self.current_focus]
    
    def get_current_focus(self) -> str:
        """Get currently focused element."""
        if not self.focusable_elements or self.current_focus >= len(self.focusable_elements):
            return ""
        return self.focusable_elements[self.current_focus]


class AccessibilityManager:
    """
    Main accessibility manager for FlashGenie.
    
    Coordinates all accessibility features and provides a unified interface
    for accessibility settings and functionality.
    """
    
    def __init__(self, console: Console):
        """
        Initialize accessibility manager.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.settings = AccessibilitySettings()
        self.screen_reader = ScreenReaderDetector()
        self.audio_feedback = AudioFeedbackSystem()
        self.keyboard_nav = KeyboardNavigationManager()
        
        # Auto-detect accessibility needs
        self._auto_detect_accessibility_needs()
    
    def _auto_detect_accessibility_needs(self) -> None:
        """Automatically detect and configure accessibility needs."""
        # Detect screen readers
        if self.screen_reader.is_screen_reader_active():
            self.enable_screen_reader_mode()
        
        # Check environment variables for accessibility preferences
        if os.environ.get("ACCESSIBILITY_HIGH_CONTRAST"):
            self.enable_high_contrast_mode()
        
        if os.environ.get("ACCESSIBILITY_LARGE_TEXT"):
            self.enable_large_text_mode()
        
        if os.environ.get("ACCESSIBILITY_AUDIO_FEEDBACK"):
            self.enable_audio_feedback()
    
    def enable_screen_reader_mode(self) -> None:
        """Enable screen reader compatibility mode."""
        self.settings.screen_reader_enabled = True
        self.settings.keyboard_navigation_only = True
        self.settings.reduced_motion = True
        self.settings.skip_animations = True
        self.keyboard_nav.enable_keyboard_navigation()
        
        # Announce mode change
        self._announce("Screen reader mode enabled")
    
    def disable_screen_reader_mode(self) -> None:
        """Disable screen reader compatibility mode."""
        self.settings.screen_reader_enabled = False
        self.settings.keyboard_navigation_only = False
        self.keyboard_nav.disable_keyboard_navigation()
        
        self._announce("Screen reader mode disabled")
    
    def enable_high_contrast_mode(self) -> None:
        """Enable high contrast visual mode."""
        self.settings.high_contrast_mode = True
        self._announce("High contrast mode enabled")
    
    def disable_high_contrast_mode(self) -> None:
        """Disable high contrast visual mode."""
        self.settings.high_contrast_mode = False
        self._announce("High contrast mode disabled")
    
    def enable_large_text_mode(self) -> None:
        """Enable large text mode."""
        self.settings.large_text_mode = True
        self.settings.text_size_multiplier = 1.5
        self._announce("Large text mode enabled")
    
    def disable_large_text_mode(self) -> None:
        """Disable large text mode."""
        self.settings.large_text_mode = False
        self.settings.text_size_multiplier = 1.0
        self._announce("Large text mode disabled")
    
    def enable_audio_feedback(self) -> None:
        """Enable audio feedback."""
        self.settings.audio_feedback_enabled = True
        self.audio_feedback.enable()
        self.audio_feedback.play_sound("success")
        self._announce("Audio feedback enabled")
    
    def disable_audio_feedback(self) -> None:
        """Disable audio feedback."""
        self.settings.audio_feedback_enabled = False
        self.audio_feedback.disable()
        self._announce("Audio feedback disabled")
    
    def _announce(self, message: str) -> None:
        """
        Announce message for screen readers.
        
        Args:
            message: Message to announce
        """
        if self.settings.screen_reader_enabled:
            # For screen readers, output to stderr with ARIA-like markup
            print(f"[ANNOUNCEMENT] {message}", file=sys.stderr, flush=True)
        
        # Also play audio feedback if enabled
        if self.settings.audio_feedback_enabled:
            self.audio_feedback.play_sound("info")
    
    def format_for_accessibility(self, content: str, element_type: str = "text") -> str:
        """
        Format content for accessibility.
        
        Args:
            content: Content to format
            element_type: Type of element (text, button, link, etc.)
            
        Returns:
            Formatted content with accessibility markup
        """
        if not self.settings.screen_reader_enabled:
            return content
        
        # Add semantic markup for screen readers
        if element_type == "button":
            return f"[BUTTON] {content}"
        elif element_type == "link":
            return f"[LINK] {content}"
        elif element_type == "heading":
            return f"[HEADING] {content}"
        elif element_type == "list_item":
            return f"[LIST ITEM] {content}"
        elif element_type == "menu_item":
            return f"[MENU ITEM] {content}"
        else:
            return content
    
    def create_accessible_panel(self, content: Any, title: str, panel_type: str = "info") -> Panel:
        """
        Create an accessible panel with proper markup.
        
        Args:
            content: Panel content
            title: Panel title
            panel_type: Type of panel (info, warning, error, success)
            
        Returns:
            Accessible Rich Panel
        """
        # Format title for accessibility
        accessible_title = self.format_for_accessibility(title, "heading")
        
        # Choose appropriate styling based on accessibility settings
        if self.settings.high_contrast_mode:
            border_style = "bright_white"
            title_style = "bold bright_white"
        else:
            style_map = {
                "info": "bright_blue",
                "warning": "bright_yellow",
                "error": "bright_red",
                "success": "bright_green"
            }
            border_style = style_map.get(panel_type, "bright_blue")
            title_style = f"bold {border_style}"
        
        # Announce panel creation
        self._announce(f"Panel opened: {title}")
        
        return Panel(
            content,
            title=accessible_title,
            border_style=border_style,
            title_style=title_style,
            padding=(1, 2)
        )
    
    def get_accessibility_status(self) -> Dict[str, Any]:
        """Get current accessibility status."""
        return {
            "screen_reader_enabled": self.settings.screen_reader_enabled,
            "high_contrast_mode": self.settings.high_contrast_mode,
            "large_text_mode": self.settings.large_text_mode,
            "audio_feedback_enabled": self.settings.audio_feedback_enabled,
            "keyboard_navigation_only": self.settings.keyboard_navigation_only,
            "detected_screen_readers": self.screen_reader.detected_readers,
            "text_size_multiplier": self.settings.text_size_multiplier
        }
    
    def show_accessibility_menu(self) -> None:
        """Show accessibility options menu."""
        status = self.get_accessibility_status()
        
        menu_content = []
        menu_content.append(Text("Accessibility Options", style="bold bright_blue"))
        menu_content.append(Text(""))
        
        # Current status
        menu_content.append(Text("Current Settings:", style="bright_yellow"))
        menu_content.append(Text(f"  Screen Reader: {'✅' if status['screen_reader_enabled'] else '❌'}"))
        menu_content.append(Text(f"  High Contrast: {'✅' if status['high_contrast_mode'] else '❌'}"))
        menu_content.append(Text(f"  Large Text: {'✅' if status['large_text_mode'] else '❌'}"))
        menu_content.append(Text(f"  Audio Feedback: {'✅' if status['audio_feedback_enabled'] else '❌'}"))
        menu_content.append(Text(f"  Text Size: {status['text_size_multiplier']:.1f}x"))
        
        if status['detected_screen_readers']:
            menu_content.append(Text(""))
            menu_content.append(Text("Detected Screen Readers:", style="bright_green"))
            for reader in status['detected_screen_readers']:
                menu_content.append(Text(f"  • {reader}"))
        
        panel = self.create_accessible_panel(
            Group(*menu_content),
            "Accessibility Settings",
            "info"
        )
        
        self.console.print(panel)
