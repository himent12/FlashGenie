"""
Study Reminders Plugin for FlashGenie

Provides intelligent study reminder system with spaced repetition scheduling,
motivational messages, and smart timing optimization.
"""

import json
import random
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import schedule

from flashgenie.core.plugin_system import BasePlugin
from flashgenie.data.storage import DataStorage


class StudyRemindersPlugin(BasePlugin):
    """Study reminders plugin with intelligent scheduling."""
    
    def initialize(self) -> None:
        """Initialize the study reminders plugin."""
        self.require_permission(self.manifest.permissions[0])  # user_data
        self.require_permission(self.manifest.permissions[1])  # system_integration
        
        self.logger.info("Study reminders plugin initialized")
        
        # Motivational messages
        self.motivational_messages = [
            "🧠 Time to boost your brainpower! Your flashcards are waiting.",
            "🎯 Consistency is key to mastery. Ready for today's session?",
            "⚡ Quick study session = Big learning gains!",
            "🌟 Every card you review brings you closer to mastery!",
            "🚀 Your future self will thank you for studying today!",
            "💪 Strong minds are built one flashcard at a time.",
            "🎓 Knowledge is power - time to power up!",
            "🔥 Keep your learning streak alive!",
            "📚 Great learners study a little every day.",
            "✨ Transform your potential into knowledge!"
        ]
        
        # Achievement-based messages
        self.achievement_messages = [
            "🏆 You're on a roll! Keep that streak going!",
            "🎖️ Your dedication is paying off - time for more progress!",
            "👑 Champions study consistently. Be a champion today!",
            "🌟 Your achievements show your commitment. Let's add to them!",
            "💎 Precious knowledge awaits in your flashcards!"
        ]
        
        # Initialize scheduler
        self.scheduler_thread = None
        self.running = False
        
        # Start reminder system if enabled
        if self.get_setting("enabled", True):
            self.start_reminders()
    
    def cleanup(self) -> None:
        """Cleanup reminder resources."""
        self.stop_reminders()
        self.logger.info("Study reminders plugin cleaned up")
    
    def start_reminders(self) -> None:
        """Start the reminder scheduling system."""
        if self.running:
            return
        
        self.running = True
        
        # Clear any existing schedules
        schedule.clear()
        
        # Schedule daily reminders
        reminder_times = self.get_setting("reminder_times", ["09:00", "18:00"])
        for time_str in reminder_times:
            schedule.every().day.at(time_str).do(self._send_daily_reminder)
        
        # Schedule smart reminders if enabled
        if self.get_setting("smart_scheduling", True):
            # Check every hour for smart reminder opportunities
            schedule.every().hour.do(self._check_smart_reminders)
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Study reminder system started")
    
    def stop_reminders(self) -> None:
        """Stop the reminder scheduling system."""
        self.running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=1)
        
        self.logger.info("Study reminder system stopped")
    
    def _run_scheduler(self) -> None:
        """Run the scheduler in background thread."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)
    
    def _send_daily_reminder(self) -> None:
        """Send daily study reminder."""
        try:
            # Check if reminders are enabled
            if not self.get_setting("enabled", True):
                return
            
            # Check weekend setting
            if not self.get_setting("weekend_reminders", False):
                if datetime.now().weekday() >= 5:  # Saturday = 5, Sunday = 6
                    return
            
            # Get due cards count
            due_cards_info = self._get_due_cards_info()
            total_due = sum(info['due_count'] for info in due_cards_info.values())
            
            # Check minimum threshold
            min_cards = self.get_setting("min_cards_due", 5)
            if total_due < min_cards:
                return
            
            # Generate reminder message
            message = self._generate_reminder_message(due_cards_info, total_due)
            
            # Send notification
            self._send_notification("FlashGenie Study Reminder", message)
            
            self.logger.info(f"Sent daily reminder: {total_due} cards due")
            
        except Exception as e:
            self.logger.error(f"Failed to send daily reminder: {e}")
    
    def _check_smart_reminders(self) -> None:
        """Check for smart reminder opportunities."""
        try:
            if not self.get_setting("smart_scheduling", True):
                return
            
            # Get user's study patterns
            study_patterns = self._analyze_study_patterns()
            
            # Check if it's a good time to remind
            current_hour = datetime.now().hour
            if current_hour in study_patterns.get('preferred_hours', []):
                
                # Check if user hasn't studied recently
                last_study = self._get_last_study_time()
                if last_study and (datetime.now() - last_study).hours >= 4:
                    
                    due_cards_info = self._get_due_cards_info()
                    total_due = sum(info['due_count'] for info in due_cards_info.values())
                    
                    if total_due >= self.get_setting("min_cards_due", 5):
                        message = self._generate_smart_reminder_message(due_cards_info, total_due)
                        self._send_notification("FlashGenie Smart Reminder", message)
                        self.logger.info(f"Sent smart reminder: {total_due} cards due")
        
        except Exception as e:
            self.logger.error(f"Smart reminder check failed: {e}")
    
    def _get_due_cards_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about due cards across all decks."""
        storage = DataStorage()
        due_info = {}
        
        try:
            # Get all deck files
            data_dir = Path("data/decks")
            if not data_dir.exists():
                return due_info
            
            for deck_file in data_dir.glob("*.json"):
                try:
                    deck = storage.load_deck(deck_file.stem)
                    if deck:
                        due_cards = deck.get_due_cards()
                        if due_cards:
                            due_info[deck.name] = {
                                'due_count': len(due_cards),
                                'total_cards': len(deck.flashcards),
                                'deck_name': deck.name
                            }
                except Exception as e:
                    self.logger.warning(f"Error loading deck {deck_file}: {e}")
        
        except Exception as e:
            self.logger.error(f"Error getting due cards info: {e}")
        
        return due_info
    
    def _generate_reminder_message(self, due_cards_info: Dict[str, Dict[str, Any]], total_due: int) -> str:
        """Generate reminder message."""
        # Base message
        if len(due_cards_info) == 1:
            deck_name = list(due_cards_info.keys())[0]
            message = f"You have {total_due} cards due in '{deck_name}'"
        else:
            message = f"You have {total_due} cards due across {len(due_cards_info)} decks"
        
        # Add motivational message if enabled
        if self.get_setting("motivational_messages", True):
            motivational = random.choice(self.motivational_messages)
            message = f"{motivational}\n\n{message}"
        
        # Add deck breakdown for multiple decks
        if len(due_cards_info) > 1:
            message += ":\n"
            for deck_info in due_cards_info.values():
                message += f"• {deck_info['deck_name']}: {deck_info['due_count']} cards\n"
        
        message += f"\n💡 Tip: Even 10 minutes of study makes a difference!"
        
        return message
    
    def _generate_smart_reminder_message(self, due_cards_info: Dict[str, Dict[str, Any]], total_due: int) -> str:
        """Generate smart reminder message."""
        base_message = self._generate_reminder_message(due_cards_info, total_due)
        
        # Add smart context
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 11:
            context = "Perfect time for a morning brain boost!"
        elif 13 <= current_hour <= 15:
            context = "Great afternoon learning opportunity!"
        elif 18 <= current_hour <= 20:
            context = "Ideal evening study time!"
        else:
            context = "Quick study session opportunity!"
        
        return f"🤖 Smart Reminder: {context}\n\n{base_message}"
    
    def _analyze_study_patterns(self) -> Dict[str, Any]:
        """Analyze user's study patterns for smart scheduling."""
        # This would analyze historical study data
        # For now, return common productive hours
        return {
            'preferred_hours': [9, 10, 14, 15, 19, 20],
            'most_productive_hour': 10,
            'average_session_length': 20,
            'preferred_days': [0, 1, 2, 3, 4]  # Monday to Friday
        }
    
    def _get_last_study_time(self) -> Optional[datetime]:
        """Get the time of last study session."""
        # This would check session logs
        # For now, return a placeholder
        try:
            # Check if there are any recent session files
            sessions_dir = Path("data/sessions")
            if sessions_dir.exists():
                session_files = list(sessions_dir.glob("*.csv"))
                if session_files:
                    # Get most recent session file
                    latest_session = max(session_files, key=lambda f: f.stat().st_mtime)
                    return datetime.fromtimestamp(latest_session.stat().st_mtime)
        except Exception:
            pass
        
        return None
    
    def _send_notification(self, title: str, message: str) -> None:
        """Send system notification."""
        try:
            import platform
            system = platform.system()
            
            if system == "Windows":
                self._send_windows_notification(title, message)
            elif system == "Darwin":  # macOS
                self._send_macos_notification(title, message)
            elif system == "Linux":
                self._send_linux_notification(title, message)
            else:
                # Fallback: print to console
                print(f"\n🔔 {title}\n{message}\n")
        
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            # Fallback: print to console
            print(f"\n🔔 {title}\n{message}\n")
    
    def _send_windows_notification(self, title: str, message: str) -> None:
        """Send Windows notification."""
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=10, icon_path=None)
        except ImportError:
            # Fallback to console
            print(f"\n🔔 {title}\n{message}\n")
    
    def _send_macos_notification(self, title: str, message: str) -> None:
        """Send macOS notification."""
        try:
            import subprocess
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
        except Exception:
            # Fallback to console
            print(f"\n🔔 {title}\n{message}\n")
    
    def _send_linux_notification(self, title: str, message: str) -> None:
        """Send Linux notification."""
        try:
            import subprocess
            subprocess.run(["notify-send", title, message], check=True)
        except Exception:
            # Fallback to console
            print(f"\n🔔 {title}\n{message}\n")
    
    def get_reminder_status(self) -> Dict[str, Any]:
        """Get current reminder system status."""
        return {
            'enabled': self.get_setting("enabled", True),
            'running': self.running,
            'reminder_times': self.get_setting("reminder_times", ["09:00", "18:00"]),
            'smart_scheduling': self.get_setting("smart_scheduling", True),
            'weekend_reminders': self.get_setting("weekend_reminders", False),
            'min_cards_due': self.get_setting("min_cards_due", 5),
            'next_scheduled': self._get_next_scheduled_reminder()
        }
    
    def _get_next_scheduled_reminder(self) -> Optional[str]:
        """Get next scheduled reminder time."""
        try:
            if schedule.jobs:
                next_run = min(job.next_run for job in schedule.jobs)
                return next_run.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
        return None
    
    def send_test_reminder(self) -> None:
        """Send a test reminder for configuration testing."""
        message = "🧪 This is a test reminder from FlashGenie!\n\nIf you can see this, your reminder system is working correctly."
        self._send_notification("FlashGenie Test Reminder", message)
        self.logger.info("Test reminder sent")
