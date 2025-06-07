"""
Contextual Learning Engine for FlashGenie v1.5

This module implements dynamic learning modes that adapt to user context
(time available, location, device, energy level) for optimal learning experiences.
"""

from datetime import datetime, time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.quiz_engine import QuizEngine, QuizMode


class Environment(Enum):
    """Different environmental contexts for learning."""
    QUIET_HOME = "quiet_home"
    NOISY_PUBLIC = "noisy_public"
    COMMUTING = "commuting"
    OFFICE = "office"
    OUTDOORS = "outdoors"
    BED = "bed"


class DeviceType(Enum):
    """Different device types for learning."""
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"
    SMARTPHONE = "smartphone"


class AttentionLevel(Enum):
    """User's current attention/focus level."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


@dataclass
class LearningContext:
    """Complete context information for adaptive learning."""
    # Time context
    available_time: int  # minutes
    time_of_day: datetime
    is_weekend: bool = False
    
    # Environment context
    environment: Environment = Environment.QUIET_HOME
    noise_level: float = 0.0  # 0.0 = silent, 1.0 = very noisy
    interruption_likelihood: float = 0.1  # 0.0 = no interruptions, 1.0 = frequent
    
    # Device context
    device_type: DeviceType = DeviceType.DESKTOP
    screen_size: str = "large"  # small, medium, large
    input_method: str = "keyboard"  # keyboard, touch, voice
    
    # User context
    attention_level: AttentionLevel = AttentionLevel.MEDIUM
    energy_level: int = 3  # 1-5 scale
    stress_level: float = 0.3  # 0.0 = relaxed, 1.0 = very stressed
    
    # Learning context
    learning_goal: str = "general"  # general, quick_review, deep_study, test_prep
    preferred_difficulty: float = 0.5  # 0.0 = easy, 1.0 = hard
    multitasking: bool = False


@dataclass
class ContextualQuizConfig:
    """Configuration for contextually adapted quiz sessions."""
    # Question presentation
    question_display_time: float = 0.0  # 0 = unlimited
    answer_reveal_delay: float = 0.5  # seconds
    feedback_duration: float = 2.0  # seconds
    
    # Interaction style
    input_method: str = "typing"  # typing, multiple_choice, voice
    confirmation_required: bool = False
    auto_advance: bool = False
    
    # Difficulty adaptation
    difficulty_adjustment_rate: float = 1.0  # multiplier for normal rate
    confidence_weighting: float = 1.0  # importance of confidence ratings
    
    # Session structure
    max_consecutive_cards: int = 20
    break_frequency: int = 0  # 0 = no forced breaks
    session_timeout: int = 0  # 0 = no timeout
    
    # Content filtering
    card_types_enabled: List[str] = field(default_factory=lambda: ["all"])
    difficulty_range: Tuple[float, float] = (0.0, 1.0)
    tag_filters: List[str] = field(default_factory=list)


class ContextualLearningEngine:
    """
    Dynamic learning engine that adapts to user context for optimal experiences.
    
    This engine automatically adjusts:
    - Question presentation style
    - Interaction methods
    - Difficulty progression
    - Session structure
    - Content selection
    
    Based on environmental and user context factors.
    """
    
    def __init__(self, quiz_engine: QuizEngine, data_path: Optional[str] = None):
        self.quiz_engine = quiz_engine
        self.data_path = Path(data_path or "data/contextual_learning")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Load context patterns and preferences
        self.context_patterns = self._load_context_patterns()
        self.adaptation_rules = self._load_adaptation_rules()
        self.performance_by_context = self._load_performance_data()
    
    def detect_context(self, manual_context: Optional[LearningContext] = None) -> LearningContext:
        """
        Detect or infer the current learning context.
        
        Args:
            manual_context: Manually specified context (overrides detection)
            
        Returns:
            Detected or specified learning context
        """
        if manual_context:
            return manual_context
        
        # Auto-detect context based on available information
        now = datetime.now()
        
        # Time-based detection
        available_time = self._estimate_available_time(now)
        is_weekend = now.weekday() >= 5
        
        # Environment detection (simplified - could use sensors/APIs)
        environment = self._detect_environment(now)
        
        # Device detection (would use actual device info)
        device_type = DeviceType.DESKTOP  # Default
        
        # User state estimation
        attention_level = self._estimate_attention_level(now, environment)
        energy_level = self._estimate_energy_level(now)
        
        return LearningContext(
            available_time=available_time,
            time_of_day=now,
            is_weekend=is_weekend,
            environment=environment,
            device_type=device_type,
            attention_level=attention_level,
            energy_level=energy_level
        )
    
    def adapt_quiz_configuration(
        self, 
        context: LearningContext,
        deck: Deck
    ) -> ContextualQuizConfig:
        """
        Create an adapted quiz configuration based on context.
        
        Args:
            context: Current learning context
            deck: Deck to be studied
            
        Returns:
            Optimized quiz configuration
        """
        config = ContextualQuizConfig()
        
        # Adapt for time constraints
        if context.available_time < 10:
            config = self._adapt_for_short_session(config, context)
        elif context.available_time > 45:
            config = self._adapt_for_long_session(config, context)
        
        # Adapt for environment
        config = self._adapt_for_environment(config, context)
        
        # Adapt for device
        config = self._adapt_for_device(config, context)
        
        # Adapt for attention/energy
        config = self._adapt_for_user_state(config, context)
        
        # Adapt for learning goals
        config = self._adapt_for_goals(config, context)
        
        return config
    
    def select_optimal_cards(
        self, 
        deck: Deck, 
        context: LearningContext,
        target_count: Optional[int] = None
    ) -> List[Flashcard]:
        """
        Select optimal cards for the current context.
        
        Args:
            deck: Deck to select from
            context: Current learning context
            target_count: Target number of cards (auto-calculated if None)
            
        Returns:
            Optimally selected cards for the context
        """
        if target_count is None:
            target_count = self._calculate_optimal_card_count(context)
        
        # Get all available cards
        available_cards = deck.flashcards
        
        # Filter based on context
        filtered_cards = self._filter_cards_by_context(available_cards, context)
        
        # Score cards for current context
        scored_cards = self._score_cards_for_context(filtered_cards, context)
        
        # Select top cards
        selected_cards = scored_cards[:target_count]
        
        # Optimize sequence for context
        optimized_sequence = self._optimize_card_sequence(selected_cards, context)
        
        return optimized_sequence
    
    def get_context_recommendations(self, context: LearningContext) -> List[str]:
        """
        Get recommendations for optimizing the current context.
        
        Args:
            context: Current learning context
            
        Returns:
            List of recommendations for better learning
        """
        recommendations = []
        
        # Environment recommendations
        if context.noise_level > 0.7:
            recommendations.append("Consider using headphones or finding a quieter location")
        
        if context.interruption_likelihood > 0.5:
            recommendations.append("Try to minimize potential interruptions for better focus")
        
        # Time recommendations
        if context.available_time < 15:
            recommendations.append("Short sessions are great for quick reviews")
        elif context.available_time > 60:
            recommendations.append("Consider taking breaks every 20-30 minutes")
        
        # Energy/attention recommendations
        if context.attention_level.value < 3:
            recommendations.append("Consider easier cards or taking a break to refresh")
        elif context.attention_level.value > 4:
            recommendations.append("Great focus! This is perfect for challenging material")
        
        # Device recommendations
        if context.device_type == DeviceType.SMARTPHONE and context.available_time > 30:
            recommendations.append("For longer sessions, a larger screen might be more comfortable")
        
        return recommendations
    
    def track_context_performance(
        self, 
        context: LearningContext, 
        performance_metrics: Dict[str, float]
    ) -> None:
        """
        Track performance in different contexts to improve future adaptations.
        
        Args:
            context: The context during the session
            performance_metrics: Performance metrics from the session
        """
        context_key = self._generate_context_key(context)
        
        if context_key not in self.performance_by_context:
            self.performance_by_context[context_key] = []
        
        # Add performance data
        self.performance_by_context[context_key].append({
            'timestamp': datetime.now().isoformat(),
            'metrics': performance_metrics,
            'context': self._serialize_context(context)
        })
        
        # Keep only recent data (last 50 sessions per context)
        self.performance_by_context[context_key] = \
            self.performance_by_context[context_key][-50:]
        
        # Save to disk
        self._save_performance_data()
    
    def _adapt_for_short_session(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for short study sessions."""
        config.auto_advance = True
        config.feedback_duration = 1.0
        config.max_consecutive_cards = min(10, context.available_time // 2)
        config.break_frequency = 0  # No breaks for short sessions
        
        # Focus on due cards and reviews
        config.card_types_enabled = ["due", "review"]
        
        return config
    
    def _adapt_for_long_session(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for long study sessions."""
        config.break_frequency = 20  # Break every 20 cards
        config.max_consecutive_cards = 25
        config.feedback_duration = 3.0
        
        # Include all card types for comprehensive study
        config.card_types_enabled = ["all"]
        
        return config
    
    def _adapt_for_environment(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for environmental context."""
        if context.environment in [Environment.NOISY_PUBLIC, Environment.COMMUTING]:
            # Reduce audio feedback, increase visual feedback
            config.feedback_duration = 1.5
            config.confirmation_required = True
            
        elif context.environment == Environment.BED:
            # Gentle, relaxed mode
            config.feedback_duration = 2.5
            config.auto_advance = False
            config.difficulty_range = (0.0, 0.6)  # Easier cards
            
        elif context.interruption_likelihood > 0.5:
            # Quick, interruptible mode
            config.auto_advance = True
            config.session_timeout = context.available_time * 60  # Convert to seconds
            
        return config
    
    def _adapt_for_device(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for device type."""
        if context.device_type == DeviceType.SMARTPHONE:
            # Mobile-optimized settings
            config.input_method = "touch"
            config.auto_advance = True
            config.max_consecutive_cards = 15
            
        elif context.device_type == DeviceType.TABLET:
            # Tablet-optimized settings
            config.input_method = "touch"
            config.feedback_duration = 2.0
            
        else:  # Desktop/Laptop
            # Full-featured settings
            config.input_method = "typing"
            config.confirmation_required = False
            
        return config
    
    def _adapt_for_user_state(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for user's attention and energy state."""
        attention_factor = context.attention_level.value / 5.0
        energy_factor = context.energy_level / 5.0
        
        # Adjust difficulty based on attention/energy
        if attention_factor < 0.4 or energy_factor < 0.4:
            # Low attention/energy: easier cards, slower pace
            config.difficulty_range = (0.0, 0.5)
            config.difficulty_adjustment_rate = 0.5
            config.feedback_duration = 3.0
            config.auto_advance = False
            
        elif attention_factor > 0.8 and energy_factor > 0.8:
            # High attention/energy: challenging cards, faster pace
            config.difficulty_range = (0.3, 1.0)
            config.difficulty_adjustment_rate = 1.5
            config.feedback_duration = 1.5
            config.auto_advance = True
            
        # Adjust for stress
        if context.stress_level > 0.7:
            config.difficulty_range = (0.0, 0.6)  # Reduce stress with easier cards
            config.break_frequency = max(10, config.break_frequency or 20)
            
        return config
    
    def _adapt_for_goals(
        self, 
        config: ContextualQuizConfig, 
        context: LearningContext
    ) -> ContextualQuizConfig:
        """Adapt configuration for learning goals."""
        if context.learning_goal == "quick_review":
            config.auto_advance = True
            config.feedback_duration = 1.0
            config.card_types_enabled = ["review", "easy"]
            
        elif context.learning_goal == "deep_study":
            config.auto_advance = False
            config.feedback_duration = 4.0
            config.confirmation_required = True
            config.difficulty_range = (0.4, 1.0)
            
        elif context.learning_goal == "test_prep":
            config.input_method = "multiple_choice"
            config.confidence_weighting = 1.5
            config.difficulty_range = (0.5, 1.0)
            
        return config
    
    def _estimate_available_time(self, current_time: datetime) -> int:
        """Estimate available study time based on time of day."""
        hour = current_time.hour
        
        # Simple heuristic - can be personalized
        if 6 <= hour < 9:  # Morning
            return 20
        elif 9 <= hour < 12:  # Late morning
            return 30
        elif 12 <= hour < 14:  # Lunch
            return 15
        elif 14 <= hour < 17:  # Afternoon
            return 25
        elif 17 <= hour < 20:  # Evening
            return 35
        elif 20 <= hour < 23:  # Night
            return 40
        else:  # Late night/early morning
            return 10
    
    def _detect_environment(self, current_time: datetime) -> Environment:
        """Detect likely environment based on time and patterns."""
        hour = current_time.hour
        is_weekend = current_time.weekday() >= 5
        
        if is_weekend:
            if 6 <= hour < 10:
                return Environment.QUIET_HOME
            elif 10 <= hour < 18:
                return Environment.QUIET_HOME
            else:
                return Environment.QUIET_HOME
        else:  # Weekday
            if 7 <= hour < 9:
                return Environment.COMMUTING
            elif 9 <= hour < 17:
                return Environment.OFFICE
            elif 17 <= hour < 19:
                return Environment.COMMUTING
            else:
                return Environment.QUIET_HOME
    
    def _estimate_attention_level(self, current_time: datetime, environment: Environment) -> AttentionLevel:
        """Estimate attention level based on time and environment."""
        hour = current_time.hour
        
        # Base attention on time of day
        if 8 <= hour < 11:  # Morning peak
            base_attention = AttentionLevel.HIGH
        elif 14 <= hour < 16:  # Post-lunch dip
            base_attention = AttentionLevel.LOW
        elif 16 <= hour < 18:  # Afternoon peak
            base_attention = AttentionLevel.HIGH
        elif 20 <= hour < 22:  # Evening
            base_attention = AttentionLevel.MEDIUM
        else:
            base_attention = AttentionLevel.LOW
        
        # Adjust for environment
        if environment in [Environment.NOISY_PUBLIC, Environment.COMMUTING]:
            # Reduce attention in distracting environments
            attention_value = max(1, base_attention.value - 1)
            return AttentionLevel(attention_value)
        
        return base_attention
    
    def _estimate_energy_level(self, current_time: datetime) -> int:
        """Estimate energy level based on time of day."""
        hour = current_time.hour
        
        if 6 <= hour < 10:  # Morning
            return 4
        elif 10 <= hour < 14:  # Late morning
            return 5
        elif 14 <= hour < 16:  # Post-lunch
            return 3
        elif 16 <= hour < 19:  # Afternoon
            return 4
        elif 19 <= hour < 22:  # Evening
            return 3
        else:  # Night/early morning
            return 2
    
    def _calculate_optimal_card_count(self, context: LearningContext) -> int:
        """Calculate optimal number of cards for the context."""
        base_cards = context.available_time // 2  # Rough estimate: 2 minutes per card
        
        # Adjust for attention and energy
        attention_factor = context.attention_level.value / 5.0
        energy_factor = context.energy_level / 5.0
        
        adjusted_cards = int(base_cards * attention_factor * energy_factor)
        
        return max(5, min(50, adjusted_cards))
    
    def _filter_cards_by_context(self, cards: List[Flashcard], context: LearningContext) -> List[Flashcard]:
        """Filter cards based on context appropriateness."""
        filtered = []
        
        for card in cards:
            # Filter by difficulty range if specified
            if hasattr(context, 'preferred_difficulty'):
                difficulty_diff = abs(card.difficulty - context.preferred_difficulty)
                if difficulty_diff > 0.3:  # Skip cards too far from preference
                    continue
            
            # Filter by attention requirements
            if context.attention_level.value < 3 and card.difficulty > 0.7:
                continue  # Skip hard cards when attention is low
            
            filtered.append(card)
        
        return filtered
    
    def _score_cards_for_context(self, cards: List[Flashcard], context: LearningContext) -> List[Flashcard]:
        """Score and sort cards based on context appropriateness."""
        def context_score(card: Flashcard) -> float:
            score = 0.0
            
            # Due cards get priority
            if card.is_due_for_review():
                score += 10.0
            
            # Adjust for attention level
            attention_factor = context.attention_level.value / 5.0
            if card.difficulty <= attention_factor:
                score += 5.0
            
            # Adjust for available time
            if context.available_time < 15 and card.difficulty < 0.5:
                score += 3.0  # Prefer easier cards for short sessions
            
            # Adjust for environment
            if context.environment in [Environment.NOISY_PUBLIC, Environment.COMMUTING]:
                if card.difficulty < 0.6:  # Prefer easier cards in distracting environments
                    score += 2.0
            
            return score
        
        return sorted(cards, key=context_score, reverse=True)
    
    def _optimize_card_sequence(self, cards: List[Flashcard], context: LearningContext) -> List[Flashcard]:
        """Optimize the sequence of cards for the context."""
        if context.attention_level.value < 3:
            # Start with easier cards when attention is low
            return sorted(cards, key=lambda c: c.difficulty)
        else:
            # Mix difficulties for better engagement
            return cards  # Simple approach - can be enhanced
    
    def _generate_context_key(self, context: LearningContext) -> str:
        """Generate a key for context-based performance tracking."""
        return f"{context.environment.value}_{context.device_type.value}_{context.attention_level.value}"
    
    def _serialize_context(self, context: LearningContext) -> Dict[str, Any]:
        """Serialize context for storage."""
        return {
            'available_time': context.available_time,
            'environment': context.environment.value,
            'device_type': context.device_type.value,
            'attention_level': context.attention_level.value,
            'energy_level': context.energy_level
        }
    
    def _load_context_patterns(self) -> Dict[str, Any]:
        """Load learned context patterns."""
        patterns_file = self.data_path / "context_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _load_adaptation_rules(self) -> Dict[str, Any]:
        """Load adaptation rules."""
        rules_file = self.data_path / "adaptation_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _load_performance_data(self) -> Dict[str, List[Dict]]:
        """Load performance data by context."""
        perf_file = self.data_path / "performance_by_context.json"
        if perf_file.exists():
            try:
                with open(perf_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_performance_data(self) -> None:
        """Save performance data to disk."""
        perf_file = self.data_path / "performance_by_context.json"
        try:
            with open(perf_file, 'w') as f:
                json.dump(self.performance_by_context, f, indent=2)
        except Exception:
            pass
