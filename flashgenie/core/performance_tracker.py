"""
Performance tracking and analytics for FlashGenie.

This module tracks user performance over time, generates statistics,
and provides insights for learning progress.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import csv
from pathlib import Path

from flashgenie.core.quiz_engine import QuizSession
from flashgenie.core.deck import Deck
from flashgenie.config import SESSIONS_DIR


@dataclass
class PerformanceMetrics:
    """
    Performance metrics for a specific time period.
    
    Attributes:
        total_sessions: Number of quiz sessions
        total_questions: Total questions answered
        correct_answers: Number of correct answers
        accuracy: Overall accuracy percentage
        average_response_time: Average response time in seconds
        total_study_time: Total time spent studying
        cards_learned: Number of cards mastered
        improvement_rate: Rate of improvement over time
    """
    total_sessions: int = 0
    total_questions: int = 0
    correct_answers: int = 0
    accuracy: float = 0.0
    average_response_time: float = 0.0
    total_study_time: timedelta = timedelta()
    cards_learned: int = 0
    improvement_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_sessions": self.total_sessions,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "accuracy": self.accuracy,
            "average_response_time": self.average_response_time,
            "total_study_time": str(self.total_study_time),
            "cards_learned": self.cards_learned,
            "improvement_rate": self.improvement_rate,
        }


class PerformanceTracker:
    """
    Tracks and analyzes user performance across quiz sessions.
    """
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.sessions_file = SESSIONS_DIR / "sessions.csv"
        self.ensure_sessions_file()
    
    def ensure_sessions_file(self) -> None:
        """Ensure the sessions CSV file exists with proper headers."""
        if not self.sessions_file.exists():
            self.sessions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sessions_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'session_id', 'deck_id', 'deck_name', 'mode', 'start_time',
                    'end_time', 'total_questions', 'correct_answers', 'accuracy',
                    'average_response_time', 'session_duration'
                ])
    
    def log_session(self, session: QuizSession) -> None:
        """
        Log a completed quiz session.
        
        Args:
            session: The completed quiz session
        """
        if not session.completed:
            return
        
        # Save detailed session data as JSON
        session_file = SESSIONS_DIR / f"session_{session.session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Log summary to CSV
        with open(self.sessions_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                session.session_id,
                session.deck.deck_id if session.deck else '',
                session.deck.name if session.deck else '',
                session.mode.value,
                session.start_time.isoformat(),
                session.end_time.isoformat() if session.end_time else '',
                session.total_questions,
                session.correct_answers,
                session.accuracy,
                session.average_response_time,
                str(session.session_duration)
            ])
    
    def get_performance_metrics(self, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               deck_id: Optional[str] = None) -> PerformanceMetrics:
        """
        Calculate performance metrics for a given time period.
        
        Args:
            start_date: Start date for analysis (None for all time)
            end_date: End date for analysis (None for now)
            deck_id: Specific deck ID to analyze (None for all decks)
            
        Returns:
            Performance metrics
        """
        sessions = self._load_sessions(start_date, end_date, deck_id)
        
        if not sessions:
            return PerformanceMetrics()
        
        # Calculate metrics
        total_sessions = len(sessions)
        total_questions = sum(s['total_questions'] for s in sessions)
        correct_answers = sum(s['correct_answers'] for s in sessions)
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
        
        # Average response time
        response_times = [s['average_response_time'] for s in sessions if s['average_response_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Total study time
        total_study_time = timedelta()
        for session in sessions:
            if session['session_duration']:
                # Parse duration string (format: "H:MM:SS" or similar)
                duration_str = session['session_duration']
                try:
                    # Simple parsing for "H:MM:SS.microseconds" format
                    parts = duration_str.split(':')
                    if len(parts) >= 3:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = float(parts[2])
                        total_study_time += timedelta(hours=hours, minutes=minutes, seconds=seconds)
                except (ValueError, IndexError):
                    continue
        
        # TODO: Implement cards_learned and improvement_rate calculations
        cards_learned = 0  # Placeholder
        improvement_rate = 0.0  # Placeholder
        
        return PerformanceMetrics(
            total_sessions=total_sessions,
            total_questions=total_questions,
            correct_answers=correct_answers,
            accuracy=accuracy,
            average_response_time=avg_response_time,
            total_study_time=total_study_time,
            cards_learned=cards_learned,
            improvement_rate=improvement_rate
        )
    
    def _load_sessions(self, 
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      deck_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load sessions from CSV with optional filtering."""
        if not self.sessions_file.exists():
            return []
        
        sessions = []
        with open(self.sessions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse start time
                try:
                    session_start = datetime.fromisoformat(row['start_time'])
                except (ValueError, KeyError):
                    continue
                
                # Apply filters
                if start_date and session_start < start_date:
                    continue
                if end_date and session_start > end_date:
                    continue
                if deck_id and row.get('deck_id') != deck_id:
                    continue
                
                # Convert numeric fields
                try:
                    row['total_questions'] = int(row['total_questions'])
                    row['correct_answers'] = int(row['correct_answers'])
                    row['accuracy'] = float(row['accuracy'])
                    row['average_response_time'] = float(row['average_response_time'])
                except (ValueError, KeyError):
                    continue
                
                sessions.append(row)
        
        return sessions
    
    def get_daily_stats(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily statistics for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of daily statistics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        sessions = self._load_sessions(start_date, end_date)
        
        # Group sessions by date
        daily_stats = {}
        for session in sessions:
            session_date = datetime.fromisoformat(session['start_time']).date()
            date_str = session_date.isoformat()
            
            if date_str not in daily_stats:
                daily_stats[date_str] = {
                    'date': date_str,
                    'sessions': 0,
                    'questions': 0,
                    'correct': 0,
                    'accuracy': 0.0
                }
            
            daily_stats[date_str]['sessions'] += 1
            daily_stats[date_str]['questions'] += session['total_questions']
            daily_stats[date_str]['correct'] += session['correct_answers']
        
        # Calculate accuracy for each day
        for stats in daily_stats.values():
            if stats['questions'] > 0:
                stats['accuracy'] = (stats['correct'] / stats['questions']) * 100
        
        # Sort by date
        return sorted(daily_stats.values(), key=lambda x: x['date'])
    
    def get_deck_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance statistics for each deck.
        
        Returns:
            List of deck performance statistics
        """
        sessions = self._load_sessions()
        
        # Group by deck
        deck_stats = {}
        for session in sessions:
            deck_id = session.get('deck_id', '')
            deck_name = session.get('deck_name', 'Unknown')
            
            if deck_id not in deck_stats:
                deck_stats[deck_id] = {
                    'deck_id': deck_id,
                    'deck_name': deck_name,
                    'sessions': 0,
                    'questions': 0,
                    'correct': 0,
                    'accuracy': 0.0,
                    'total_time': timedelta()
                }
            
            deck_stats[deck_id]['sessions'] += 1
            deck_stats[deck_id]['questions'] += session['total_questions']
            deck_stats[deck_id]['correct'] += session['correct_answers']
            
            # Parse session duration
            duration_str = session.get('session_duration', '')
            try:
                parts = duration_str.split(':')
                if len(parts) >= 3:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    seconds = float(parts[2])
                    deck_stats[deck_id]['total_time'] += timedelta(
                        hours=hours, minutes=minutes, seconds=seconds
                    )
            except (ValueError, IndexError):
                pass
        
        # Calculate accuracy and convert timedelta to string
        for stats in deck_stats.values():
            if stats['questions'] > 0:
                stats['accuracy'] = (stats['correct'] / stats['questions']) * 100
            stats['total_time'] = str(stats['total_time'])
        
        return list(deck_stats.values())
    
    def get_learning_streak(self) -> int:
        """
        Calculate the current learning streak (consecutive days with sessions).
        
        Returns:
            Number of consecutive days with study sessions
        """
        sessions = self._load_sessions()
        if not sessions:
            return 0
        
        # Get unique study dates
        study_dates = set()
        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session['start_time']).date()
                study_dates.add(session_date)
            except ValueError:
                continue
        
        if not study_dates:
            return 0
        
        # Sort dates in descending order
        sorted_dates = sorted(study_dates, reverse=True)
        
        # Count consecutive days from today
        today = datetime.now().date()
        streak = 0
        
        for i, date in enumerate(sorted_dates):
            expected_date = today - timedelta(days=i)
            if date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def export_performance_data(self, file_path: Path) -> None:
        """
        Export all performance data to a JSON file.
        
        Args:
            file_path: Path where to save the export
        """
        data = {
            'export_date': datetime.now().isoformat(),
            'overall_metrics': self.get_performance_metrics().to_dict(),
            'daily_stats': self.get_daily_stats(90),  # Last 90 days
            'deck_performance': self.get_deck_performance(),
            'learning_streak': self.get_learning_streak(),
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def clear_old_sessions(self, days_to_keep: int = 365) -> int:
        """
        Clear old session data to save space.
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Number of sessions removed
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        sessions = self._load_sessions()
        
        # Filter sessions to keep
        sessions_to_keep = []
        removed_count = 0
        
        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session['start_time'])
                if session_date >= cutoff_date:
                    sessions_to_keep.append(session)
                else:
                    removed_count += 1
                    # Remove detailed session file
                    session_file = SESSIONS_DIR / f"session_{session['session_id']}.json"
                    if session_file.exists():
                        session_file.unlink()
            except ValueError:
                continue
        
        # Rewrite CSV with remaining sessions
        with open(self.sessions_file, 'w', newline='', encoding='utf-8') as f:
            if sessions_to_keep:
                writer = csv.DictWriter(f, fieldnames=sessions_to_keep[0].keys())
                writer.writeheader()
                writer.writerows(sessions_to_keep)
        
        return removed_count
