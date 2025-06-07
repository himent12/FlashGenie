"""
Achievement System for FlashGenie.

This module provides the main AchievementSystem class that serves as the
public interface for achievement functionality.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .achievements.models import (
    Achievement, AchievementEvent, AchievementType, AchievementRarity
)
from .achievements.engine import AchievementEngine
from .achievements.manager import AchievementManager
from flashgenie.utils.exceptions import FlashGenieError


class AchievementSystem:
    """
    Main interface for achievement system functionality.
    
    This class provides a simplified interface to the achievement
    system while maintaining backward compatibility.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the achievement system.
        
        Args:
            data_path: Optional path for storing achievement data
        """
        self.engine = AchievementEngine(data_path)
        self.manager = AchievementManager(data_path)
    
    def record_study_session(
        self, 
        user_id: str, 
        session_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Record a study session and check for achievements.
        
        Args:
            user_id: User identifier
            session_data: Session performance data
            
        Returns:
            List of newly earned achievements
        """
        try:
            # Create achievement event
            event = AchievementEvent(
                event_type="study_session_completed",
                user_id=user_id,
                timestamp=datetime.now(),
                event_data=session_data,
                session_id=session_data.get("session_id"),
                deck_id=session_data.get("deck_id"),
                performance_metrics={
                    "accuracy": session_data.get("accuracy", 0.0),
                    "cards_per_minute": session_data.get("cards_per_minute", 0.0),
                    "session_duration": session_data.get("duration_minutes", 0)
                }
            )
            
            # Process event and get newly earned achievements
            user_achievements = self.engine.process_event(event)
            
            # Convert to dictionaries and create notifications
            earned_achievements = []
            for user_achievement in user_achievements:
                achievement = self.engine.achievements.get(user_achievement.achievement_id)
                if achievement:
                    # Create notification
                    self.manager.create_notification(
                        user_id=user_id,
                        achievement_id=achievement.id,
                        title=f"Achievement Unlocked: {achievement.name}",
                        message=achievement.description
                    )
                    
                    # Award badge if specified
                    if achievement.badge_id:
                        self.manager.award_badge(user_id, achievement.badge_id, achievement.id)
                    
                    earned_achievements.append({
                        "achievement_id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "points": achievement.points,
                        "rarity": achievement.rarity.value,
                        "icon": achievement.icon,
                        "earned_at": user_achievement.earned_at.isoformat()
                    })
            
            return earned_achievements
            
        except Exception as e:
            raise FlashGenieError(f"Failed to record study session: {e}")
    
    def get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all achievements for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user achievements
        """
        try:
            user_achievements = self.engine.get_user_achievements(user_id)
            
            achievements_data = []
            for user_achievement in user_achievements:
                achievement = self.engine.achievements.get(user_achievement.achievement_id)
                if achievement:
                    achievements_data.append({
                        "achievement_id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "type": achievement.achievement_type.value,
                        "rarity": achievement.rarity.value,
                        "points": achievement.points,
                        "icon": achievement.icon,
                        "color": achievement.color,
                        "earned_at": user_achievement.earned_at.isoformat(),
                        "trigger_event": user_achievement.trigger_event
                    })
            
            # Sort by earned date (most recent first)
            achievements_data.sort(key=lambda x: x["earned_at"], reverse=True)
            
            return achievements_data
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get user achievements: {e}")
    
    def get_achievement_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get achievement statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with achievement statistics
        """
        try:
            stats = self.engine.calculate_achievement_stats(user_id)
            
            return {
                "total_achievements": stats.total_achievements,
                "total_points": stats.total_points,
                "achievements_by_type": stats.achievements_by_type,
                "achievements_by_rarity": stats.achievements_by_rarity,
                "points_by_category": stats.points_by_category,
                "completion_rate": stats.completion_rate,
                "achievements_in_progress": stats.achievements_in_progress,
                "recent_achievements": stats.recent_achievements,
                "last_achievement_date": stats.last_achievement_date.isoformat() if stats.last_achievement_date else None,
                "current_streak": stats.current_streak,
                "longest_streak": stats.longest_streak
            }
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get achievement statistics: {e}")
    
    def get_available_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get achievements available to earn for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of available achievements
        """
        try:
            user_achievements = self.engine.get_user_achievements(user_id)
            earned_ids = {ua.achievement_id for ua in user_achievements}
            
            available_achievements = []
            for achievement in self.engine.achievements.values():
                if achievement.id not in earned_ids and not achievement.is_hidden:
                    # Check prerequisites
                    prerequisites_met = True
                    if achievement.prerequisite_achievements:
                        for prereq in achievement.prerequisite_achievements:
                            if prereq not in earned_ids:
                                prerequisites_met = False
                                break
                    
                    if prerequisites_met:
                        available_achievements.append({
                            "achievement_id": achievement.id,
                            "name": achievement.name,
                            "description": achievement.description,
                            "type": achievement.achievement_type.value,
                            "rarity": achievement.rarity.value,
                            "points": achievement.points,
                            "icon": achievement.icon,
                            "color": achievement.color,
                            "requirements": achievement.requirements,
                            "is_repeatable": achievement.is_repeatable
                        })
            
            # Sort by points (highest first)
            available_achievements.sort(key=lambda x: x["points"], reverse=True)
            
            return available_achievements
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get available achievements: {e}")
    
    def get_user_badges(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get badges earned by a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user badges
        """
        try:
            user_badges = self.manager.user_badges.get(user_id, [])
            
            badges_data = []
            for user_badge in user_badges:
                badge = self.manager.badges.get(user_badge.badge_id)
                if badge:
                    badges_data.append({
                        "badge_id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "category": badge.category.value,
                        "icon": badge.icon,
                        "color": badge.color,
                        "rarity": badge.rarity.value,
                        "earned_at": user_badge.earned_at.isoformat(),
                        "is_displayed": user_badge.is_displayed,
                        "earned_from_achievement": user_badge.earned_from_achievement
                    })
            
            # Sort by earned date (most recent first)
            badges_data.sort(key=lambda x: x["earned_at"], reverse=True)
            
            return badges_data
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get user badges: {e}")
    
    def get_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get achievement notifications for a user.
        
        Args:
            user_id: User identifier
            unread_only: Whether to return only unread notifications
            
        Returns:
            List of notifications
        """
        try:
            notifications = self.manager.notifications.get(user_id, [])
            
            if unread_only:
                notifications = [n for n in notifications if not n.is_read]
            
            notifications_data = []
            for notification in notifications:
                notifications_data.append({
                    "notification_id": notification.notification_id,
                    "achievement_id": notification.achievement_id,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                    "is_read": notification.is_read,
                    "priority": notification.priority
                })
            
            # Sort by creation date (most recent first)
            notifications_data.sort(key=lambda x: x["created_at"], reverse=True)
            
            return notifications_data
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get notifications: {e}")
    
    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            user_id: User identifier
            notification_id: Notification identifier
            
        Returns:
            True if successfully marked as read
        """
        try:
            notifications = self.manager.notifications.get(user_id, [])
            
            for notification in notifications:
                if notification.notification_id == notification_id:
                    notification.is_read = True
                    return True
            
            return False
            
        except Exception as e:
            raise FlashGenieError(f"Failed to mark notification as read: {e}")
    
    def get_leaderboard(self, leaderboard_id: str = "total_points") -> Dict[str, Any]:
        """
        Get leaderboard data.
        
        Args:
            leaderboard_id: Leaderboard identifier
            
        Returns:
            Dictionary with leaderboard data
        """
        try:
            # Update leaderboard with current data
            self.manager.update_leaderboard(leaderboard_id)
            
            leaderboard = self.manager.leaderboards.get(leaderboard_id)
            if not leaderboard:
                return {"error": f"Leaderboard '{leaderboard_id}' not found"}
            
            return {
                "leaderboard_id": leaderboard.leaderboard_id,
                "name": leaderboard.name,
                "description": leaderboard.description,
                "metric_type": leaderboard.metric_type,
                "time_period": leaderboard.time_period,
                "last_updated": leaderboard.last_updated.isoformat(),
                "participant_count": leaderboard.participant_count,
                "entries": leaderboard.entries[:50]  # Top 50
            }
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get leaderboard: {e}")
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with dashboard data
        """
        try:
            return self.manager.get_user_dashboard(user_id)
        except Exception as e:
            raise FlashGenieError(f"Failed to get user dashboard: {e}")
    
    def get_achievement_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get achievement recommendations for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recommended achievements
        """
        try:
            return self.manager.get_achievement_recommendations(user_id)
        except Exception as e:
            raise FlashGenieError(f"Failed to get achievement recommendations: {e}")
    
    def create_custom_achievement(
        self, 
        achievement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a custom achievement.
        
        Args:
            achievement_data: Achievement configuration
            
        Returns:
            Dictionary with created achievement data
        """
        try:
            achievement = Achievement(
                id=achievement_data["id"],
                name=achievement_data["name"],
                description=achievement_data["description"],
                achievement_type=AchievementType(achievement_data.get("type", "milestone")),
                rarity=AchievementRarity(achievement_data.get("rarity", "common")),
                requirements=achievement_data.get("requirements", {}),
                points=achievement_data.get("points", 10),
                icon=achievement_data.get("icon", "🏆"),
                color=achievement_data.get("color", "#FFD700")
            )
            
            self.engine.register_achievement(achievement)
            
            return {
                "achievement_id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "type": achievement.achievement_type.value,
                "rarity": achievement.rarity.value,
                "points": achievement.points,
                "created": True
            }
            
        except Exception as e:
            raise FlashGenieError(f"Failed to create custom achievement: {e}")
    
    def get_achievement_progress(self, user_id: str, achievement_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress towards a specific achievement.
        
        Args:
            user_id: User identifier
            achievement_id: Achievement identifier
            
        Returns:
            Dictionary with progress data or None if not found
        """
        try:
            progress = self.engine.check_achievement_progress(user_id, achievement_id)
            
            if not progress:
                return None
            
            return {
                "achievement_id": progress.achievement_id,
                "progress_percentage": progress.progress_percentage,
                "current_progress": progress.current_progress,
                "started_at": progress.started_at.isoformat(),
                "last_updated": progress.last_updated.isoformat(),
                "milestones_reached": progress.milestones_reached
            }
            
        except Exception as e:
            raise FlashGenieError(f"Failed to get achievement progress: {e}")
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all achievement data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with exported data
        """
        try:
            achievements = self.get_user_achievements(user_id)
            badges = self.get_user_badges(user_id)
            statistics = self.get_achievement_statistics(user_id)
            notifications = self.get_notifications(user_id)
            
            return {
                "user_id": user_id,
                "export_date": datetime.now().isoformat(),
                "achievements": achievements,
                "badges": badges,
                "statistics": statistics,
                "notifications": notifications,
                "total_achievements": len(achievements),
                "total_badges": len(badges),
                "total_points": statistics.get("total_points", 0)
            }
            
        except Exception as e:
            raise FlashGenieError(f"Failed to export user data: {e}")
