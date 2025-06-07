"""
Data models for achievement system.

This module contains all the data classes and enums used by the achievement system.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class AchievementType(Enum):
    """Types of achievements."""
    MILESTONE = "milestone"
    STREAK = "streak"
    MASTERY = "mastery"
    SPEED = "speed"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    SPECIAL = "special"


class AchievementRarity(Enum):
    """Rarity levels for achievements."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BadgeCategory(Enum):
    """Categories for badges."""
    LEARNING = "learning"
    PERFORMANCE = "performance"
    DEDICATION = "dedication"
    EXPLORATION = "exploration"
    MASTERY = "mastery"
    SOCIAL = "social"
    SPECIAL = "special"


@dataclass
class Achievement:
    """An achievement that can be earned by users."""
    id: str
    name: str
    description: str
    achievement_type: AchievementType
    rarity: AchievementRarity
    
    # Requirements
    requirements: Dict[str, Any] = field(default_factory=dict)
    prerequisite_achievements: List[str] = field(default_factory=list)
    
    # Rewards
    points: int = 0
    badge_id: Optional[str] = None
    title: Optional[str] = None
    
    # Metadata
    category: BadgeCategory = BadgeCategory.LEARNING
    icon: str = "🏆"
    color: str = "#FFD700"
    
    # Tracking
    is_hidden: bool = False
    is_repeatable: bool = False
    max_completions: int = 1
    
    # Progress tracking
    progress_tracking: bool = True
    progress_description: str = ""
    
    def __post_init__(self):
        """Set default values based on achievement type."""
        if not self.progress_description:
            self.progress_description = f"Progress towards {self.name}"


@dataclass
class UserAchievement:
    """An achievement earned by a user."""
    achievement_id: str
    user_id: str
    earned_at: datetime
    
    # Progress data
    progress_data: Dict[str, Any] = field(default_factory=dict)
    completion_count: int = 1
    
    # Context
    trigger_event: str = ""
    session_id: Optional[str] = None
    
    # Notification
    notified: bool = False
    notification_sent_at: Optional[datetime] = None


@dataclass
class AchievementProgress:
    """Progress towards an achievement."""
    achievement_id: str
    user_id: str
    
    # Progress tracking
    current_progress: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: float = 0.0
    
    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Milestones
    milestones_reached: List[str] = field(default_factory=list)
    
    def update_progress(self, new_data: Dict[str, Any]) -> None:
        """Update progress data."""
        self.current_progress.update(new_data)
        self.last_updated = datetime.now()


@dataclass
class Badge:
    """A badge that can be displayed on user profiles."""
    id: str
    name: str
    description: str
    category: BadgeCategory
    
    # Visual properties
    icon: str = "🏅"
    color: str = "#4CAF50"
    image_url: Optional[str] = None
    
    # Requirements
    required_achievements: List[str] = field(default_factory=list)
    
    # Metadata
    rarity: AchievementRarity = AchievementRarity.COMMON
    is_special: bool = False


@dataclass
class UserBadge:
    """A badge earned by a user."""
    badge_id: str
    user_id: str
    earned_at: datetime
    
    # Display settings
    is_displayed: bool = True
    display_order: int = 0
    
    # Context
    earned_from_achievement: Optional[str] = None


@dataclass
class AchievementRule:
    """A rule for checking achievement completion."""
    achievement_id: str
    rule_name: str
    
    # Condition function
    condition_function: str  # Name of the function to call
    condition_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Thresholds
    target_value: Optional[float] = None
    comparison_operator: str = "gte"  # gte, lte, eq, gt, lt
    
    # Context requirements
    required_context: Dict[str, Any] = field(default_factory=dict)
    
    # Progress calculation
    progress_function: Optional[str] = None
    progress_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AchievementEvent:
    """An event that can trigger achievement checks."""
    event_type: str
    user_id: str
    timestamp: datetime
    
    # Event data
    event_data: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    
    # Context
    deck_id: Optional[str] = None
    card_id: Optional[str] = None
    
    # Metrics
    performance_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class AchievementNotification:
    """A notification for an earned achievement."""
    notification_id: str
    user_id: str
    achievement_id: str
    
    # Notification content
    title: str
    message: str
    
    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    # Status
    is_sent: bool = False
    is_read: bool = False
    
    # Delivery
    delivery_method: str = "in_app"  # in_app, email, push
    priority: str = "normal"  # low, normal, high


@dataclass
class AchievementStats:
    """Statistics about user achievements."""
    user_id: str
    
    # Counts
    total_achievements: int = 0
    achievements_by_type: Dict[str, int] = field(default_factory=dict)
    achievements_by_rarity: Dict[str, int] = field(default_factory=dict)
    
    # Points
    total_points: int = 0
    points_by_category: Dict[str, int] = field(default_factory=dict)
    
    # Badges
    total_badges: int = 0
    displayed_badges: int = 0
    
    # Progress
    achievements_in_progress: int = 0
    completion_rate: float = 0.0
    
    # Recent activity
    recent_achievements: List[str] = field(default_factory=list)
    last_achievement_date: Optional[datetime] = None
    
    # Streaks
    current_streak: int = 0
    longest_streak: int = 0


@dataclass
class AchievementLeaderboard:
    """Leaderboard for achievements."""
    leaderboard_id: str
    name: str
    description: str
    
    # Configuration
    metric_type: str  # total_points, total_achievements, specific_achievement
    time_period: str = "all_time"  # all_time, monthly, weekly, daily
    
    # Entries
    entries: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    last_updated: datetime = field(default_factory=datetime.now)
    participant_count: int = 0


@dataclass
class AchievementChallenge:
    """A time-limited achievement challenge."""
    challenge_id: str
    name: str
    description: str
    
    # Timing
    start_date: datetime
    end_date: datetime
    
    # Requirements
    target_achievements: List[str] = field(default_factory=list)
    target_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Rewards
    completion_rewards: Dict[str, Any] = field(default_factory=dict)
    
    # Participation
    participants: List[str] = field(default_factory=list)
    completions: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    is_public: bool = True


@dataclass
class AchievementMilestone:
    """A milestone within an achievement."""
    milestone_id: str
    achievement_id: str
    name: str
    description: str
    
    # Requirements
    threshold: float
    threshold_type: str  # percentage, absolute
    
    # Rewards
    points: int = 0
    notification_message: str = ""
    
    # Order
    order: int = 0


@dataclass
class UserProfile:
    """User profile with achievement data."""
    user_id: str
    
    # Display preferences
    display_name: str = ""
    show_achievements: bool = True
    show_badges: bool = True
    
    # Featured content
    featured_achievements: List[str] = field(default_factory=list)
    featured_badges: List[str] = field(default_factory=list)
    
    # Titles
    current_title: Optional[str] = None
    available_titles: List[str] = field(default_factory=list)
    
    # Statistics
    achievement_stats: Optional[AchievementStats] = None
    
    # Privacy
    profile_visibility: str = "public"  # public, friends, private
