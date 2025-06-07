"""
Gamification & Achievement System for FlashGenie v1.5

This module implements a comprehensive gamification system with achievements,
streaks, challenges, and social features to increase motivation and engagement.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck


class AchievementType(Enum):
    """Types of achievements."""
    STREAK = "streak"  # Study streaks
    ACCURACY = "accuracy"  # Accuracy milestones
    VOLUME = "volume"  # Volume-based achievements
    DIFFICULTY = "difficulty"  # Difficulty progression
    SPEED = "speed"  # Response time achievements
    CONSISTENCY = "consistency"  # Regular study habits
    MASTERY = "mastery"  # Mastery achievements
    SPECIAL = "special"  # Special event achievements


class AchievementRarity(Enum):
    """Rarity levels for achievements."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class StreakType(Enum):
    """Types of study streaks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    ACCURACY = "accuracy"
    PERFECT = "perfect"
    DIFFICULTY = "difficulty"


@dataclass
class AchievementCriteria:
    """Criteria for earning an achievement."""
    metric: str  # The metric to track
    threshold: float  # The threshold value
    comparison: str = "gte"  # gte, lte, eq
    timeframe: Optional[int] = None  # Days to look back (None = all time)
    additional_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def check(self, value: float, **kwargs) -> bool:
        """Check if the criteria is met."""
        if self.comparison == "gte":
            return value >= self.threshold
        elif self.comparison == "lte":
            return value <= self.threshold
        elif self.comparison == "eq":
            return abs(value - self.threshold) < 0.001
        return False


@dataclass
class Achievement:
    """An achievement that can be earned."""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    rarity: AchievementRarity
    criteria: AchievementCriteria
    
    # Rewards
    points: int = 0
    badge_icon: str = "🏆"
    unlock_message: str = ""
    
    # Metadata
    hidden: bool = False  # Hidden until unlocked
    repeatable: bool = False
    prerequisite_achievements: List[str] = field(default_factory=list)
    
    # Progress tracking
    progress_description: str = ""
    max_progress: float = 1.0
    
    def calculate_progress(self, current_value: float) -> float:
        """Calculate progress towards this achievement (0.0 to 1.0)."""
        if self.criteria.comparison == "gte":
            return min(1.0, current_value / self.criteria.threshold)
        elif self.criteria.comparison == "lte":
            return min(1.0, self.criteria.threshold / max(current_value, 0.001))
        return 1.0 if self.criteria.check(current_value) else 0.0


@dataclass
class UserAchievement:
    """An achievement earned by a user."""
    achievement_id: str
    earned_at: datetime
    progress_when_earned: float = 1.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StudyStreak:
    """A study streak record."""
    streak_type: StreakType
    current_count: int
    best_count: int
    start_date: datetime
    last_activity_date: datetime
    is_active: bool = True
    
    def update(self, activity_date: datetime, success: bool = True) -> bool:
        """
        Update the streak with new activity.
        
        Args:
            activity_date: Date of the activity
            success: Whether the activity was successful
            
        Returns:
            True if streak was extended, False if broken
        """
        if not success:
            self._break_streak()
            return False
        
        # Check if this continues the streak
        if self.streak_type == StreakType.DAILY:
            expected_date = self.last_activity_date + timedelta(days=1)
            if activity_date.date() == expected_date.date():
                self.current_count += 1
                self.last_activity_date = activity_date
                self.best_count = max(self.best_count, self.current_count)
                return True
            elif activity_date.date() > expected_date.date():
                self._break_streak()
                self._start_new_streak(activity_date)
                return False
        
        return True
    
    def _break_streak(self) -> None:
        """Break the current streak."""
        self.is_active = False
    
    def _start_new_streak(self, start_date: datetime) -> None:
        """Start a new streak."""
        self.current_count = 1
        self.start_date = start_date
        self.last_activity_date = start_date
        self.is_active = True


@dataclass
class Challenge:
    """A time-limited challenge."""
    id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    criteria: AchievementCriteria
    rewards: Dict[str, Any]
    participants: Set[str] = field(default_factory=set)
    leaderboard: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_active(self) -> bool:
        """Check if the challenge is currently active."""
        now = datetime.now()
        return self.start_date <= now <= self.end_date
    
    def time_remaining(self) -> timedelta:
        """Get time remaining in the challenge."""
        if not self.is_active():
            return timedelta(0)
        return self.end_date - datetime.now()


class AchievementEngine:
    """
    Comprehensive achievement and gamification system.
    
    Features:
    - Achievement tracking and unlocking
    - Study streak monitoring
    - Challenge system
    - Progress visualization
    - Social features (leaderboards, sharing)
    """
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path or "data/achievements")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Achievement system
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: List[UserAchievement] = []
        
        # Streak system
        self.streaks: Dict[StreakType, StudyStreak] = {}
        
        # Challenge system
        self.challenges: Dict[str, Challenge] = {}
        
        # User stats
        self.user_stats: Dict[str, Any] = {}
        
        # Initialize system
        self._initialize_achievements()
        self._load_user_data()
    
    def check_achievements(self, user_stats: Dict[str, Any]) -> List[Achievement]:
        """
        Check for newly earned achievements.
        
        Args:
            user_stats: Current user statistics
            
        Returns:
            List of newly earned achievements
        """
        newly_earned = []
        
        for achievement in self.achievements.values():
            # Skip if already earned (and not repeatable)
            if not achievement.repeatable and self._is_achievement_earned(achievement.id):
                continue
            
            # Check prerequisites
            if not self._check_prerequisites(achievement):
                continue
            
            # Check criteria
            metric_value = user_stats.get(achievement.criteria.metric, 0)
            
            # Apply timeframe filter if specified
            if achievement.criteria.timeframe:
                metric_value = self._get_metric_in_timeframe(
                    achievement.criteria.metric, 
                    achievement.criteria.timeframe,
                    user_stats
                )
            
            # Check additional conditions
            if not self._check_additional_conditions(achievement.criteria, user_stats):
                continue
            
            # Check if criteria is met
            if achievement.criteria.check(metric_value):
                self._award_achievement(achievement, user_stats)
                newly_earned.append(achievement)
        
        return newly_earned
    
    def update_streaks(self, session_stats: Dict[str, Any]) -> Dict[StreakType, bool]:
        """
        Update study streaks based on session performance.
        
        Args:
            session_stats: Statistics from the study session
            
        Returns:
            Dictionary of streak types and whether they were extended
        """
        streak_updates = {}
        session_date = datetime.now()
        
        # Daily study streak
        daily_streak = self.streaks.get(StreakType.DAILY)
        if not daily_streak:
            daily_streak = StudyStreak(
                streak_type=StreakType.DAILY,
                current_count=1,
                best_count=1,
                start_date=session_date,
                last_activity_date=session_date
            )
            self.streaks[StreakType.DAILY] = daily_streak
            streak_updates[StreakType.DAILY] = True
        else:
            streak_updates[StreakType.DAILY] = daily_streak.update(session_date, True)
        
        # Accuracy streak
        accuracy = session_stats.get('accuracy_rate', 0.0)
        if accuracy >= 0.8:  # 80% accuracy threshold
            accuracy_streak = self.streaks.get(StreakType.ACCURACY)
            if not accuracy_streak:
                accuracy_streak = StudyStreak(
                    streak_type=StreakType.ACCURACY,
                    current_count=1,
                    best_count=1,
                    start_date=session_date,
                    last_activity_date=session_date
                )
                self.streaks[StreakType.ACCURACY] = accuracy_streak
                streak_updates[StreakType.ACCURACY] = True
            else:
                streak_updates[StreakType.ACCURACY] = accuracy_streak.update(session_date, True)
        else:
            # Break accuracy streak
            if StreakType.ACCURACY in self.streaks:
                self.streaks[StreakType.ACCURACY]._break_streak()
                streak_updates[StreakType.ACCURACY] = False
        
        # Perfect streak (100% accuracy)
        if accuracy >= 1.0:
            perfect_streak = self.streaks.get(StreakType.PERFECT)
            if not perfect_streak:
                perfect_streak = StudyStreak(
                    streak_type=StreakType.PERFECT,
                    current_count=1,
                    best_count=1,
                    start_date=session_date,
                    last_activity_date=session_date
                )
                self.streaks[StreakType.PERFECT] = perfect_streak
                streak_updates[StreakType.PERFECT] = True
            else:
                streak_updates[StreakType.PERFECT] = perfect_streak.update(session_date, True)
        else:
            # Break perfect streak
            if StreakType.PERFECT in self.streaks:
                self.streaks[StreakType.PERFECT]._break_streak()
                streak_updates[StreakType.PERFECT] = False
        
        # Save updated streaks
        self._save_user_data()
        
        return streak_updates
    
    def get_achievement_progress(self, user_stats: Dict[str, Any]) -> Dict[str, float]:
        """
        Get progress towards all achievements.
        
        Args:
            user_stats: Current user statistics
            
        Returns:
            Dictionary mapping achievement IDs to progress (0.0 to 1.0)
        """
        progress = {}
        
        for achievement in self.achievements.values():
            # Skip hidden achievements that haven't been unlocked
            if achievement.hidden and not self._is_achievement_earned(achievement.id):
                continue
            
            metric_value = user_stats.get(achievement.criteria.metric, 0)
            
            # Apply timeframe filter if specified
            if achievement.criteria.timeframe:
                metric_value = self._get_metric_in_timeframe(
                    achievement.criteria.metric,
                    achievement.criteria.timeframe,
                    user_stats
                )
            
            progress[achievement.id] = achievement.calculate_progress(metric_value)
        
        return progress
    
    def get_user_level_and_points(self) -> Tuple[int, int, int]:
        """
        Calculate user level and points.
        
        Returns:
            Tuple of (level, current_points, points_to_next_level)
        """
        total_points = sum(
            self.achievements[ua.achievement_id].points
            for ua in self.user_achievements
            if ua.achievement_id in self.achievements
        )
        
        # Calculate level (every 1000 points = 1 level)
        level = total_points // 1000 + 1
        points_in_level = total_points % 1000
        points_to_next = 1000 - points_in_level
        
        return level, points_in_level, points_to_next
    
    def get_leaderboard_stats(self) -> Dict[str, Any]:
        """Get stats for leaderboard display."""
        level, current_points, points_to_next = self.get_user_level_and_points()
        
        return {
            'level': level,
            'total_points': current_points + (level - 1) * 1000,
            'achievements_earned': len(self.user_achievements),
            'total_achievements': len(self.achievements),
            'current_streaks': {
                streak_type.value: streak.current_count
                for streak_type, streak in self.streaks.items()
                if streak.is_active
            },
            'best_streaks': {
                streak_type.value: streak.best_count
                for streak_type, streak in self.streaks.items()
            }
        }
    
    def _initialize_achievements(self) -> None:
        """Initialize the achievement system with predefined achievements."""
        # Study streak achievements
        self.achievements["first_day"] = Achievement(
            id="first_day",
            name="First Steps",
            description="Complete your first study session",
            achievement_type=AchievementType.STREAK,
            rarity=AchievementRarity.COMMON,
            criteria=AchievementCriteria("sessions_completed", 1),
            points=50,
            badge_icon="🎯",
            unlock_message="Welcome to FlashGenie! You've taken your first step on the learning journey."
        )
        
        self.achievements["week_warrior"] = Achievement(
            id="week_warrior",
            name="Week Warrior",
            description="Study for 7 consecutive days",
            achievement_type=AchievementType.STREAK,
            rarity=AchievementRarity.UNCOMMON,
            criteria=AchievementCriteria("daily_streak", 7),
            points=200,
            badge_icon="🔥",
            unlock_message="Incredible dedication! You've built a solid study habit."
        )
        
        self.achievements["month_master"] = Achievement(
            id="month_master",
            name="Month Master",
            description="Study for 30 consecutive days",
            achievement_type=AchievementType.STREAK,
            rarity=AchievementRarity.RARE,
            criteria=AchievementCriteria("daily_streak", 30),
            points=1000,
            badge_icon="👑",
            unlock_message="Outstanding! You've mastered the art of consistent learning."
        )
        
        # Accuracy achievements
        self.achievements["perfectionist"] = Achievement(
            id="perfectionist",
            name="Perfectionist",
            description="Achieve 100% accuracy in a session",
            achievement_type=AchievementType.ACCURACY,
            rarity=AchievementRarity.UNCOMMON,
            criteria=AchievementCriteria("session_accuracy", 1.0),
            points=150,
            badge_icon="💯",
            unlock_message="Perfect! Your attention to detail is impressive."
        )
        
        self.achievements["accuracy_ace"] = Achievement(
            id="accuracy_ace",
            name="Accuracy Ace",
            description="Maintain 90%+ accuracy over 100 cards",
            achievement_type=AchievementType.ACCURACY,
            rarity=AchievementRarity.RARE,
            criteria=AchievementCriteria("accuracy_rate", 0.9, additional_conditions={"min_cards": 100}),
            points=500,
            badge_icon="🎯",
            unlock_message="Exceptional accuracy! Your precision is remarkable."
        )
        
        # Volume achievements
        self.achievements["century_club"] = Achievement(
            id="century_club",
            name="Century Club",
            description="Review 100 cards",
            achievement_type=AchievementType.VOLUME,
            rarity=AchievementRarity.COMMON,
            criteria=AchievementCriteria("total_cards_reviewed", 100),
            points=100,
            badge_icon="💪",
            unlock_message="Great progress! You're building momentum."
        )
        
        self.achievements["thousand_master"] = Achievement(
            id="thousand_master",
            name="Thousand Master",
            description="Review 1000 cards",
            achievement_type=AchievementType.VOLUME,
            rarity=AchievementRarity.EPIC,
            criteria=AchievementCriteria("total_cards_reviewed", 1000),
            points=2000,
            badge_icon="🏆",
            unlock_message="Incredible dedication! You've reviewed a thousand cards."
        )
        
        # Speed achievements
        self.achievements["lightning_fast"] = Achievement(
            id="lightning_fast",
            name="Lightning Fast",
            description="Average response time under 2 seconds",
            achievement_type=AchievementType.SPEED,
            rarity=AchievementRarity.UNCOMMON,
            criteria=AchievementCriteria("avg_response_time", 2.0, "lte"),
            points=300,
            badge_icon="⚡",
            unlock_message="Lightning fast! Your quick thinking is impressive."
        )
        
        # Difficulty achievements
        self.achievements["challenge_seeker"] = Achievement(
            id="challenge_seeker",
            name="Challenge Seeker",
            description="Complete 50 hard cards (difficulty > 0.7)",
            achievement_type=AchievementType.DIFFICULTY,
            rarity=AchievementRarity.RARE,
            criteria=AchievementCriteria("hard_cards_completed", 50),
            points=750,
            badge_icon="🎖️",
            unlock_message="Fearless! You embrace challenges and grow stronger."
        )
        
        # Mastery achievements
        self.achievements["deck_master"] = Achievement(
            id="deck_master",
            name="Deck Master",
            description="Achieve 90% mastery on a deck",
            achievement_type=AchievementType.MASTERY,
            rarity=AchievementRarity.EPIC,
            criteria=AchievementCriteria("deck_mastery_rate", 0.9),
            points=1500,
            badge_icon="🎓",
            unlock_message="Mastery achieved! You've conquered this knowledge domain."
        )
    
    def _is_achievement_earned(self, achievement_id: str) -> bool:
        """Check if an achievement has been earned."""
        return any(ua.achievement_id == achievement_id for ua in self.user_achievements)
    
    def _check_prerequisites(self, achievement: Achievement) -> bool:
        """Check if achievement prerequisites are met."""
        for prereq_id in achievement.prerequisite_achievements:
            if not self._is_achievement_earned(prereq_id):
                return False
        return True
    
    def _check_additional_conditions(self, criteria: AchievementCriteria, user_stats: Dict[str, Any]) -> bool:
        """Check additional conditions for achievement criteria."""
        for condition, value in criteria.additional_conditions.items():
            if condition == "min_cards":
                if user_stats.get("total_cards_reviewed", 0) < value:
                    return False
        return True
    
    def _get_metric_in_timeframe(self, metric: str, days: int, user_stats: Dict[str, Any]) -> float:
        """Get metric value within a specific timeframe."""
        # Simplified implementation - would need session history for accurate calculation
        return user_stats.get(metric, 0)
    
    def _award_achievement(self, achievement: Achievement, user_stats: Dict[str, Any]) -> None:
        """Award an achievement to the user."""
        user_achievement = UserAchievement(
            achievement_id=achievement.id,
            earned_at=datetime.now(),
            context={"stats_when_earned": user_stats.copy()}
        )
        self.user_achievements.append(user_achievement)
        self._save_user_data()
    
    def _load_user_data(self) -> None:
        """Load user achievement data from storage."""
        # Load achievements
        achievements_file = self.data_path / "user_achievements.json"
        if achievements_file.exists():
            try:
                with open(achievements_file, 'r') as f:
                    data = json.load(f)
                    self.user_achievements = [
                        UserAchievement(
                            achievement_id=item["achievement_id"],
                            earned_at=datetime.fromisoformat(item["earned_at"]),
                            progress_when_earned=item.get("progress_when_earned", 1.0),
                            context=item.get("context", {})
                        )
                        for item in data
                    ]
            except Exception:
                pass
        
        # Load streaks
        streaks_file = self.data_path / "streaks.json"
        if streaks_file.exists():
            try:
                with open(streaks_file, 'r') as f:
                    data = json.load(f)
                    for streak_type_str, streak_data in data.items():
                        streak_type = StreakType(streak_type_str)
                        self.streaks[streak_type] = StudyStreak(
                            streak_type=streak_type,
                            current_count=streak_data["current_count"],
                            best_count=streak_data["best_count"],
                            start_date=datetime.fromisoformat(streak_data["start_date"]),
                            last_activity_date=datetime.fromisoformat(streak_data["last_activity_date"]),
                            is_active=streak_data.get("is_active", True)
                        )
            except Exception:
                pass
    
    def _save_user_data(self) -> None:
        """Save user achievement data to storage."""
        # Save achievements
        achievements_file = self.data_path / "user_achievements.json"
        try:
            with open(achievements_file, 'w') as f:
                json.dump([
                    {
                        "achievement_id": ua.achievement_id,
                        "earned_at": ua.earned_at.isoformat(),
                        "progress_when_earned": ua.progress_when_earned,
                        "context": ua.context
                    }
                    for ua in self.user_achievements
                ], f, indent=2)
        except Exception:
            pass
        
        # Save streaks
        streaks_file = self.data_path / "streaks.json"
        try:
            with open(streaks_file, 'w') as f:
                json.dump({
                    streak_type.value: {
                        "current_count": streak.current_count,
                        "best_count": streak.best_count,
                        "start_date": streak.start_date.isoformat(),
                        "last_activity_date": streak.last_activity_date.isoformat(),
                        "is_active": streak.is_active
                    }
                    for streak_type, streak in self.streaks.items()
                }, f, indent=2)
        except Exception:
            pass
