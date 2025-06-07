"""
Achievement engine for processing and awarding achievements.

This module provides the core logic for checking and awarding achievements.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json
from pathlib import Path

from .models import (
    Achievement, UserAchievement, AchievementProgress, AchievementEvent,
    AchievementRule, AchievementType, AchievementRarity, AchievementStats
)


class AchievementEngine:
    """Core engine for processing achievements."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the achievement engine.
        
        Args:
            data_path: Optional path for storing achievement data
        """
        self.data_path = Path(data_path or "data/achievements")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Achievement definitions
        self.achievements: Dict[str, Achievement] = {}
        self.achievement_rules: Dict[str, List[AchievementRule]] = {}
        
        # User data
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self.user_progress: Dict[str, Dict[str, AchievementProgress]] = {}
        
        # Condition functions
        self.condition_functions: Dict[str, Callable] = {}
        
        # Load default achievements
        self._load_default_achievements()
        self._register_default_conditions()
    
    def register_achievement(self, achievement: Achievement) -> None:
        """
        Register a new achievement.
        
        Args:
            achievement: Achievement to register
        """
        self.achievements[achievement.id] = achievement
        
        # Create default rules if none exist
        if achievement.id not in self.achievement_rules:
            self.achievement_rules[achievement.id] = []
    
    def register_condition_function(self, name: str, function: Callable) -> None:
        """
        Register a condition function for achievement checking.
        
        Args:
            name: Name of the function
            function: Function to register
        """
        self.condition_functions[name] = function
    
    def process_event(self, event: AchievementEvent) -> List[UserAchievement]:
        """
        Process an event and check for achievement completions.
        
        Args:
            event: Event to process
            
        Returns:
            List of newly earned achievements
        """
        newly_earned = []
        
        # Check all achievements for this user
        for achievement_id, achievement in self.achievements.items():
            if self._should_check_achievement(achievement, event):
                if self._check_achievement_completion(achievement, event):
                    user_achievement = self._award_achievement(achievement, event)
                    if user_achievement:
                        newly_earned.append(user_achievement)
        
        return newly_earned
    
    def check_achievement_progress(self, user_id: str, achievement_id: str) -> Optional[AchievementProgress]:
        """
        Check progress towards a specific achievement.
        
        Args:
            user_id: User identifier
            achievement_id: Achievement identifier
            
        Returns:
            Achievement progress or None if not found
        """
        if user_id not in self.user_progress:
            return None
        
        return self.user_progress[user_id].get(achievement_id)
    
    def get_user_achievements(self, user_id: str) -> List[UserAchievement]:
        """
        Get all achievements for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user achievements
        """
        return self.user_achievements.get(user_id, [])
    
    def calculate_achievement_stats(self, user_id: str) -> AchievementStats:
        """
        Calculate achievement statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Achievement statistics
        """
        user_achievements = self.get_user_achievements(user_id)
        
        stats = AchievementStats(user_id=user_id)
        
        # Count achievements
        stats.total_achievements = len(user_achievements)
        
        # Count by type and rarity
        for user_achievement in user_achievements:
            achievement = self.achievements.get(user_achievement.achievement_id)
            if achievement:
                # By type
                type_name = achievement.achievement_type.value
                stats.achievements_by_type[type_name] = stats.achievements_by_type.get(type_name, 0) + 1
                
                # By rarity
                rarity_name = achievement.rarity.value
                stats.achievements_by_rarity[rarity_name] = stats.achievements_by_rarity.get(rarity_name, 0) + 1
                
                # Points
                stats.total_points += achievement.points
                
                # By category
                category_name = achievement.category.value
                stats.points_by_category[category_name] = stats.points_by_category.get(category_name, 0) + achievement.points
        
        # Progress tracking
        if user_id in self.user_progress:
            stats.achievements_in_progress = len(self.user_progress[user_id])
        
        # Completion rate
        total_available = len([a for a in self.achievements.values() if not a.is_hidden])
        if total_available > 0:
            stats.completion_rate = stats.total_achievements / total_available
        
        # Recent achievements
        recent_achievements = sorted(user_achievements, key=lambda x: x.earned_at, reverse=True)[:5]
        stats.recent_achievements = [ua.achievement_id for ua in recent_achievements]
        
        if user_achievements:
            stats.last_achievement_date = max(ua.earned_at for ua in user_achievements)
        
        return stats
    
    def _should_check_achievement(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Check if an achievement should be evaluated for an event."""
        # Skip if user already has non-repeatable achievement
        if not achievement.is_repeatable:
            user_achievements = self.get_user_achievements(event.user_id)
            if any(ua.achievement_id == achievement.id for ua in user_achievements):
                return False
        
        # Check if user has completed max times
        if achievement.max_completions > 1:
            user_achievements = self.get_user_achievements(event.user_id)
            completion_count = sum(1 for ua in user_achievements if ua.achievement_id == achievement.id)
            if completion_count >= achievement.max_completions:
                return False
        
        # Check prerequisites
        if achievement.prerequisite_achievements:
            user_achievements = self.get_user_achievements(event.user_id)
            user_achievement_ids = {ua.achievement_id for ua in user_achievements}
            
            for prereq in achievement.prerequisite_achievements:
                if prereq not in user_achievement_ids:
                    return False
        
        return True
    
    def _check_achievement_completion(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Check if an achievement is completed by an event."""
        rules = self.achievement_rules.get(achievement.id, [])
        
        if not rules:
            # No specific rules, use default checking
            return self._default_achievement_check(achievement, event)
        
        # Check all rules
        for rule in rules:
            if not self._evaluate_rule(rule, event):
                return False
        
        return True
    
    def _evaluate_rule(self, rule: AchievementRule, event: AchievementEvent) -> bool:
        """Evaluate a single achievement rule."""
        # Get condition function
        condition_func = self.condition_functions.get(rule.condition_function)
        if not condition_func:
            return False
        
        # Prepare parameters
        params = rule.condition_parameters.copy()
        params.update({
            'event': event,
            'rule': rule
        })
        
        try:
            result = condition_func(**params)
            
            # Apply comparison if target value is specified
            if rule.target_value is not None:
                if rule.comparison_operator == "gte":
                    return result >= rule.target_value
                elif rule.comparison_operator == "lte":
                    return result <= rule.target_value
                elif rule.comparison_operator == "eq":
                    return result == rule.target_value
                elif rule.comparison_operator == "gt":
                    return result > rule.target_value
                elif rule.comparison_operator == "lt":
                    return result < rule.target_value
            
            return bool(result)
            
        except Exception as e:
            print(f"Error evaluating rule {rule.rule_name}: {e}")
            return False
    
    def _default_achievement_check(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Default achievement checking logic."""
        # Simple checks based on achievement type
        if achievement.achievement_type == AchievementType.MILESTONE:
            # Check if milestone requirements are met
            return self._check_milestone_requirements(achievement, event)
        
        elif achievement.achievement_type == AchievementType.STREAK:
            # Check streak requirements
            return self._check_streak_requirements(achievement, event)
        
        elif achievement.achievement_type == AchievementType.ACCURACY:
            # Check accuracy requirements
            return self._check_accuracy_requirements(achievement, event)
        
        # Default to false for unknown types
        return False
    
    def _check_milestone_requirements(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Check milestone-based achievement requirements."""
        requirements = achievement.requirements
        
        # Check cards studied milestone
        if "cards_studied" in requirements:
            target = requirements["cards_studied"]
            current = event.event_data.get("total_cards_studied", 0)
            return current >= target
        
        # Check sessions completed milestone
        if "sessions_completed" in requirements:
            target = requirements["sessions_completed"]
            current = event.event_data.get("total_sessions", 0)
            return current >= target
        
        return False
    
    def _check_streak_requirements(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Check streak-based achievement requirements."""
        requirements = achievement.requirements
        
        if "streak_days" in requirements:
            target = requirements["streak_days"]
            current = event.event_data.get("current_streak", 0)
            return current >= target
        
        return False
    
    def _check_accuracy_requirements(self, achievement: Achievement, event: AchievementEvent) -> bool:
        """Check accuracy-based achievement requirements."""
        requirements = achievement.requirements
        
        if "accuracy_threshold" in requirements:
            target = requirements["accuracy_threshold"]
            current = event.performance_metrics.get("accuracy", 0.0)
            return current >= target
        
        return False
    
    def _award_achievement(self, achievement: Achievement, event: AchievementEvent) -> Optional[UserAchievement]:
        """Award an achievement to a user."""
        user_id = event.user_id
        
        # Create user achievement
        user_achievement = UserAchievement(
            achievement_id=achievement.id,
            user_id=user_id,
            earned_at=datetime.now(),
            trigger_event=event.event_type,
            session_id=event.session_id
        )
        
        # Add to user achievements
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
        
        self.user_achievements[user_id].append(user_achievement)
        
        # Remove from progress tracking
        if user_id in self.user_progress and achievement.id in self.user_progress[user_id]:
            del self.user_progress[user_id][achievement.id]
        
        # Save data
        self._save_user_data(user_id)
        
        return user_achievement
    
    def _load_default_achievements(self) -> None:
        """Load default achievements."""
        default_achievements = [
            Achievement(
                id="first_session",
                name="Getting Started",
                description="Complete your first study session",
                achievement_type=AchievementType.MILESTONE,
                rarity=AchievementRarity.COMMON,
                requirements={"sessions_completed": 1},
                points=10,
                icon="🎯"
            ),
            Achievement(
                id="cards_100",
                name="Century Mark",
                description="Study 100 flashcards",
                achievement_type=AchievementType.MILESTONE,
                rarity=AchievementRarity.COMMON,
                requirements={"cards_studied": 100},
                points=50,
                icon="💯"
            ),
            Achievement(
                id="streak_7",
                name="Week Warrior",
                description="Maintain a 7-day study streak",
                achievement_type=AchievementType.STREAK,
                rarity=AchievementRarity.UNCOMMON,
                requirements={"streak_days": 7},
                points=100,
                icon="🔥"
            ),
            Achievement(
                id="accuracy_90",
                name="Precision Master",
                description="Achieve 90% accuracy in a session",
                achievement_type=AchievementType.ACCURACY,
                rarity=AchievementRarity.RARE,
                requirements={"accuracy_threshold": 0.9},
                points=75,
                icon="🎯"
            ),
            Achievement(
                id="speed_demon",
                name="Speed Demon",
                description="Answer 50 cards in under 10 minutes",
                achievement_type=AchievementType.SPEED,
                rarity=AchievementRarity.RARE,
                requirements={"cards_per_minute": 5.0},
                points=100,
                icon="⚡"
            )
        ]
        
        for achievement in default_achievements:
            self.register_achievement(achievement)
    
    def _register_default_conditions(self) -> None:
        """Register default condition functions."""
        self.register_condition_function("cards_studied_total", self._condition_cards_studied_total)
        self.register_condition_function("sessions_completed_total", self._condition_sessions_completed_total)
        self.register_condition_function("current_streak", self._condition_current_streak)
        self.register_condition_function("session_accuracy", self._condition_session_accuracy)
        self.register_condition_function("session_speed", self._condition_session_speed)
    
    def _condition_cards_studied_total(self, event: AchievementEvent, **kwargs) -> int:
        """Condition function for total cards studied."""
        return event.event_data.get("total_cards_studied", 0)
    
    def _condition_sessions_completed_total(self, event: AchievementEvent, **kwargs) -> int:
        """Condition function for total sessions completed."""
        return event.event_data.get("total_sessions", 0)
    
    def _condition_current_streak(self, event: AchievementEvent, **kwargs) -> int:
        """Condition function for current streak."""
        return event.event_data.get("current_streak", 0)
    
    def _condition_session_accuracy(self, event: AchievementEvent, **kwargs) -> float:
        """Condition function for session accuracy."""
        return event.performance_metrics.get("accuracy", 0.0)
    
    def _condition_session_speed(self, event: AchievementEvent, **kwargs) -> float:
        """Condition function for session speed (cards per minute)."""
        return event.performance_metrics.get("cards_per_minute", 0.0)
    
    def _save_user_data(self, user_id: str) -> None:
        """Save user achievement data to disk."""
        try:
            user_file = self.data_path / f"user_{user_id}.json"
            
            # Prepare data for serialization
            user_data = {
                "achievements": [
                    {
                        "achievement_id": ua.achievement_id,
                        "earned_at": ua.earned_at.isoformat(),
                        "trigger_event": ua.trigger_event,
                        "session_id": ua.session_id,
                        "completion_count": ua.completion_count
                    }
                    for ua in self.user_achievements.get(user_id, [])
                ],
                "progress": {
                    achievement_id: {
                        "current_progress": progress.current_progress,
                        "progress_percentage": progress.progress_percentage,
                        "started_at": progress.started_at.isoformat(),
                        "last_updated": progress.last_updated.isoformat(),
                        "milestones_reached": progress.milestones_reached
                    }
                    for achievement_id, progress in self.user_progress.get(user_id, {}).items()
                }
            }
            
            with open(user_file, 'w') as f:
                json.dump(user_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving user achievement data: {e}")
    
    def _load_user_data(self, user_id: str) -> None:
        """Load user achievement data from disk."""
        try:
            user_file = self.data_path / f"user_{user_id}.json"
            
            if not user_file.exists():
                return
            
            with open(user_file, 'r') as f:
                user_data = json.load(f)
            
            # Load achievements
            achievements = []
            for ua_data in user_data.get("achievements", []):
                user_achievement = UserAchievement(
                    achievement_id=ua_data["achievement_id"],
                    user_id=user_id,
                    earned_at=datetime.fromisoformat(ua_data["earned_at"]),
                    trigger_event=ua_data.get("trigger_event", ""),
                    session_id=ua_data.get("session_id"),
                    completion_count=ua_data.get("completion_count", 1)
                )
                achievements.append(user_achievement)
            
            self.user_achievements[user_id] = achievements
            
            # Load progress
            progress_data = {}
            for achievement_id, progress_info in user_data.get("progress", {}).items():
                progress = AchievementProgress(
                    achievement_id=achievement_id,
                    user_id=user_id,
                    current_progress=progress_info["current_progress"],
                    progress_percentage=progress_info["progress_percentage"],
                    started_at=datetime.fromisoformat(progress_info["started_at"]),
                    last_updated=datetime.fromisoformat(progress_info["last_updated"]),
                    milestones_reached=progress_info.get("milestones_reached", [])
                )
                progress_data[achievement_id] = progress
            
            if progress_data:
                self.user_progress[user_id] = progress_data
                
        except Exception as e:
            print(f"Error loading user achievement data: {e}")
