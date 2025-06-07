"""
Achievement manager for handling badges, notifications, and user interactions.

This module provides high-level management of the achievement system.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from .models import (
    Badge, UserBadge, AchievementNotification, AchievementLeaderboard,
    AchievementChallenge, UserProfile, BadgeCategory, AchievementRarity
)
from .engine import AchievementEngine


class AchievementManager:
    """High-level manager for the achievement system."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the achievement manager.
        
        Args:
            data_path: Optional path for storing achievement data
        """
        self.engine = AchievementEngine(data_path)
        
        # Badge system
        self.badges: Dict[str, Badge] = {}
        self.user_badges: Dict[str, List[UserBadge]] = {}
        
        # Notification system
        self.notifications: Dict[str, List[AchievementNotification]] = {}
        
        # Leaderboards
        self.leaderboards: Dict[str, AchievementLeaderboard] = {}
        
        # User profiles
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Challenges
        self.active_challenges: Dict[str, AchievementChallenge] = {}
        
        # Initialize default content
        self._initialize_default_badges()
        self._initialize_default_leaderboards()
    
    def award_badge(self, user_id: str, badge_id: str, achievement_id: Optional[str] = None) -> Optional[UserBadge]:
        """
        Award a badge to a user.
        
        Args:
            user_id: User identifier
            badge_id: Badge identifier
            achievement_id: Optional achievement that triggered the badge
            
        Returns:
            Awarded user badge or None if already owned
        """
        # Check if user already has this badge
        user_badges = self.user_badges.get(user_id, [])
        if any(ub.badge_id == badge_id for ub in user_badges):
            return None
        
        # Create user badge
        user_badge = UserBadge(
            badge_id=badge_id,
            user_id=user_id,
            earned_at=datetime.now(),
            earned_from_achievement=achievement_id
        )
        
        # Add to user badges
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        self.user_badges[user_id].append(user_badge)
        
        return user_badge
    
    def create_notification(
        self, 
        user_id: str, 
        achievement_id: str, 
        title: str, 
        message: str
    ) -> AchievementNotification:
        """
        Create an achievement notification.
        
        Args:
            user_id: User identifier
            achievement_id: Achievement identifier
            title: Notification title
            message: Notification message
            
        Returns:
            Created notification
        """
        notification = AchievementNotification(
            notification_id=str(uuid.uuid4()),
            user_id=user_id,
            achievement_id=achievement_id,
            title=title,
            message=message
        )
        
        # Add to user notifications
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        
        self.notifications[user_id].append(notification)
        
        return notification
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """
        Get or create user profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile
        """
        if user_id not in self.user_profiles:
            # Create new profile
            profile = UserProfile(user_id=user_id)
            profile.achievement_stats = self.engine.calculate_achievement_stats(user_id)
            self.user_profiles[user_id] = profile
        
        return self.user_profiles[user_id]
    
    def update_leaderboard(self, leaderboard_id: str) -> None:
        """
        Update a leaderboard with current data.
        
        Args:
            leaderboard_id: Leaderboard identifier
        """
        leaderboard = self.leaderboards.get(leaderboard_id)
        if not leaderboard:
            return
        
        # Collect user data based on metric type
        user_scores = []
        
        for user_id in self.engine.user_achievements.keys():
            stats = self.engine.calculate_achievement_stats(user_id)
            
            if leaderboard.metric_type == "total_points":
                score = stats.total_points
            elif leaderboard.metric_type == "total_achievements":
                score = stats.total_achievements
            else:
                score = 0
            
            user_scores.append({
                "user_id": user_id,
                "score": score,
                "rank": 0  # Will be calculated
            })
        
        # Sort and assign ranks
        user_scores.sort(key=lambda x: x["score"], reverse=True)
        for i, entry in enumerate(user_scores):
            entry["rank"] = i + 1
        
        # Update leaderboard
        leaderboard.entries = user_scores[:100]  # Top 100
        leaderboard.last_updated = datetime.now()
        leaderboard.participant_count = len(user_scores)
    
    def create_challenge(
        self, 
        name: str, 
        description: str, 
        duration_days: int,
        target_achievements: List[str] = None,
        target_metrics: Dict[str, float] = None
    ) -> AchievementChallenge:
        """
        Create a new achievement challenge.
        
        Args:
            name: Challenge name
            description: Challenge description
            duration_days: Duration in days
            target_achievements: List of target achievement IDs
            target_metrics: Target metrics to achieve
            
        Returns:
            Created challenge
        """
        challenge_id = str(uuid.uuid4())
        
        challenge = AchievementChallenge(
            challenge_id=challenge_id,
            name=name,
            description=description,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            target_achievements=target_achievements or [],
            target_metrics=target_metrics or {}
        )
        
        self.active_challenges[challenge_id] = challenge
        
        return challenge
    
    def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """
        Join a user to a challenge.
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            
        Returns:
            True if successfully joined
        """
        challenge = self.active_challenges.get(challenge_id)
        if not challenge or not challenge.is_active:
            return False
        
        if user_id not in challenge.participants:
            challenge.participants.append(user_id)
        
        return True
    
    def check_challenge_completion(self, user_id: str, challenge_id: str) -> bool:
        """
        Check if a user has completed a challenge.
        
        Args:
            user_id: User identifier
            challenge_id: Challenge identifier
            
        Returns:
            True if challenge is completed
        """
        challenge = self.active_challenges.get(challenge_id)
        if not challenge:
            return False
        
        # Check if user is participant
        if user_id not in challenge.participants:
            return False
        
        # Check target achievements
        if challenge.target_achievements:
            user_achievements = self.engine.get_user_achievements(user_id)
            user_achievement_ids = {ua.achievement_id for ua in user_achievements}
            
            for target_achievement in challenge.target_achievements:
                if target_achievement not in user_achievement_ids:
                    return False
        
        # Check target metrics
        if challenge.target_metrics:
            stats = self.engine.calculate_achievement_stats(user_id)
            
            for metric, target_value in challenge.target_metrics.items():
                if metric == "total_points" and stats.total_points < target_value:
                    return False
                elif metric == "total_achievements" and stats.total_achievements < target_value:
                    return False
        
        # Mark as completed if not already
        if user_id not in challenge.completions:
            challenge.completions.append(user_id)
        
        return True
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with dashboard data
        """
        profile = self.get_user_profile(user_id)
        stats = self.engine.calculate_achievement_stats(user_id)
        user_achievements = self.engine.get_user_achievements(user_id)
        user_badges = self.user_badges.get(user_id, [])
        notifications = self.notifications.get(user_id, [])
        
        # Recent achievements (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_achievements = [
            ua for ua in user_achievements 
            if ua.earned_at >= week_ago
        ]
        
        # Available achievements (not yet earned)
        earned_ids = {ua.achievement_id for ua in user_achievements}
        available_achievements = [
            achievement for achievement in self.engine.achievements.values()
            if achievement.id not in earned_ids and not achievement.is_hidden
        ]
        
        # Active challenges
        user_challenges = [
            challenge for challenge in self.active_challenges.values()
            if user_id in challenge.participants and challenge.is_active
        ]
        
        return {
            "profile": {
                "user_id": profile.user_id,
                "display_name": profile.display_name,
                "current_title": profile.current_title,
                "profile_visibility": profile.profile_visibility
            },
            "statistics": {
                "total_achievements": stats.total_achievements,
                "total_points": stats.total_points,
                "total_badges": len(user_badges),
                "completion_rate": stats.completion_rate,
                "achievements_by_type": stats.achievements_by_type,
                "achievements_by_rarity": stats.achievements_by_rarity
            },
            "recent_activity": {
                "recent_achievements": [
                    {
                        "achievement_id": ua.achievement_id,
                        "name": self.engine.achievements[ua.achievement_id].name,
                        "earned_at": ua.earned_at.isoformat(),
                        "points": self.engine.achievements[ua.achievement_id].points
                    }
                    for ua in recent_achievements[-5:]  # Last 5
                ],
                "unread_notifications": len([n for n in notifications if not n.is_read])
            },
            "progress": {
                "available_achievements": len(available_achievements),
                "next_achievements": [
                    {
                        "achievement_id": achievement.id,
                        "name": achievement.name,
                        "description": achievement.description,
                        "points": achievement.points,
                        "rarity": achievement.rarity.value
                    }
                    for achievement in available_achievements[:5]  # Next 5
                ]
            },
            "challenges": {
                "active_challenges": len(user_challenges),
                "challenge_details": [
                    {
                        "challenge_id": challenge.challenge_id,
                        "name": challenge.name,
                        "description": challenge.description,
                        "end_date": challenge.end_date.isoformat(),
                        "completed": user_id in challenge.completions
                    }
                    for challenge in user_challenges
                ]
            }
        }
    
    def get_achievement_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get achievement recommendations for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recommended achievements
        """
        user_achievements = self.engine.get_user_achievements(user_id)
        earned_ids = {ua.achievement_id for ua in user_achievements}
        
        recommendations = []
        
        # Find achievements close to completion
        for achievement in self.engine.achievements.values():
            if achievement.id in earned_ids or achievement.is_hidden:
                continue
            
            # Check prerequisites
            if achievement.prerequisite_achievements:
                if not all(prereq in earned_ids for prereq in achievement.prerequisite_achievements):
                    continue
            
            # Estimate progress (simplified)
            progress_estimate = self._estimate_achievement_progress(user_id, achievement)
            
            if progress_estimate > 0.3:  # At least 30% progress
                recommendations.append({
                    "achievement_id": achievement.id,
                    "name": achievement.name,
                    "description": achievement.description,
                    "points": achievement.points,
                    "rarity": achievement.rarity.value,
                    "estimated_progress": progress_estimate,
                    "recommendation_reason": self._get_recommendation_reason(achievement, progress_estimate)
                })
        
        # Sort by progress and points
        recommendations.sort(key=lambda x: (x["estimated_progress"], x["points"]), reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _initialize_default_badges(self) -> None:
        """Initialize default badges."""
        default_badges = [
            Badge(
                id="newcomer",
                name="Newcomer",
                description="Welcome to FlashGenie!",
                category=BadgeCategory.LEARNING,
                icon="🌟",
                color="#4CAF50"
            ),
            Badge(
                id="dedicated_learner",
                name="Dedicated Learner",
                description="Consistent study habits",
                category=BadgeCategory.DEDICATION,
                icon="📚",
                color="#2196F3"
            ),
            Badge(
                id="speed_master",
                name="Speed Master",
                description="Lightning-fast learning",
                category=BadgeCategory.PERFORMANCE,
                icon="⚡",
                color="#FF9800"
            ),
            Badge(
                id="perfectionist",
                name="Perfectionist",
                description="Exceptional accuracy",
                category=BadgeCategory.PERFORMANCE,
                icon="🎯",
                color="#9C27B0"
            )
        ]
        
        for badge in default_badges:
            self.badges[badge.id] = badge
    
    def _initialize_default_leaderboards(self) -> None:
        """Initialize default leaderboards."""
        default_leaderboards = [
            AchievementLeaderboard(
                leaderboard_id="total_points",
                name="Top Achievers",
                description="Users with the most achievement points",
                metric_type="total_points"
            ),
            AchievementLeaderboard(
                leaderboard_id="total_achievements",
                name="Achievement Collectors",
                description="Users with the most achievements",
                metric_type="total_achievements"
            ),
            AchievementLeaderboard(
                leaderboard_id="monthly_points",
                name="Monthly Champions",
                description="Top point earners this month",
                metric_type="total_points",
                time_period="monthly"
            )
        ]
        
        for leaderboard in default_leaderboards:
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard
    
    def _estimate_achievement_progress(self, user_id: str, achievement) -> float:
        """Estimate progress towards an achievement."""
        # This is a simplified estimation
        # In a real implementation, this would analyze user data more thoroughly
        
        requirements = achievement.requirements
        
        if "cards_studied" in requirements:
            # Estimate based on current study patterns
            return min(1.0, 0.5)  # Placeholder
        
        if "sessions_completed" in requirements:
            return min(1.0, 0.3)  # Placeholder
        
        if "streak_days" in requirements:
            return min(1.0, 0.2)  # Placeholder
        
        return 0.1  # Default low progress
    
    def _get_recommendation_reason(self, achievement, progress: float) -> str:
        """Get reason for recommending an achievement."""
        if progress > 0.8:
            return "Almost complete! Just a little more effort."
        elif progress > 0.5:
            return "Good progress! Keep it up."
        elif achievement.rarity == AchievementRarity.COMMON:
            return "A great next step in your learning journey."
        else:
            return "Challenge yourself with this achievement."
