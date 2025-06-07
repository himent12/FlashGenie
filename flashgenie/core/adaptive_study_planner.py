"""
Adaptive Study Session Planner for FlashGenie v1.5

This module implements AI-powered study session planning that optimizes learning
based on available time, energy levels, learning goals, and historical performance.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import math
from pathlib import Path

from flashgenie.core.flashcard import Flashcard
from flashgenie.core.deck import Deck
from flashgenie.core.difficulty_analyzer import DifficultyAnalyzer
from flashgenie.core.smart_collections import SmartCollectionManager


class EnergyLevel(Enum):
    """User energy levels for study session optimization."""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5


class StudyGoal(Enum):
    """Different types of study goals."""
    MAINTENANCE = "maintenance"  # Maintain current knowledge
    ACQUISITION = "acquisition"  # Learn new material
    MASTERY = "mastery"  # Achieve deep understanding
    REVIEW = "review"  # Quick review of known material
    CHALLENGE = "challenge"  # Push difficulty boundaries


@dataclass
class StudyPreferences:
    """User preferences for study sessions."""
    preferred_session_length: int = 30  # minutes
    max_session_length: int = 60  # minutes
    break_frequency: int = 15  # minutes between breaks
    break_duration: int = 5  # minutes
    difficulty_preference: float = 0.5  # 0.0 = easy, 1.0 = hard
    new_card_ratio: float = 0.3  # ratio of new vs review cards
    energy_adaptation: bool = True
    circadian_optimization: bool = True


@dataclass
class StudyContext:
    """Context information for study session planning."""
    available_time: int  # minutes
    energy_level: EnergyLevel
    time_of_day: datetime
    environment: str = "quiet"  # quiet, noisy, mobile
    device_type: str = "desktop"  # desktop, mobile, tablet
    interruption_likelihood: float = 0.1  # 0.0 = no interruptions, 1.0 = many
    goals: List[StudyGoal] = field(default_factory=lambda: [StudyGoal.MAINTENANCE])


@dataclass
class StudySegment:
    """A segment within a study session."""
    cards: List[Flashcard]
    estimated_duration: int  # minutes
    difficulty_range: Tuple[float, float]
    segment_type: str  # "warmup", "core", "challenge", "cooldown"
    break_after: bool = False
    break_duration: int = 0


@dataclass
class StudyPlan:
    """Complete study session plan."""
    session_id: str
    total_duration: int  # minutes
    segments: List[StudySegment]
    estimated_cards: int
    difficulty_progression: List[float]
    break_schedule: List[int]  # minutes when breaks occur
    optimization_notes: List[str]
    confidence_score: float  # how confident we are in this plan


class AdaptiveStudyPlanner:
    """
    AI-powered study session planner that creates optimal learning experiences.
    
    This planner considers multiple factors:
    - Available time and energy levels
    - Historical performance patterns
    - Circadian rhythm preferences
    - Learning goals and preferences
    - Card difficulty and review schedules
    """
    
    def __init__(
        self, 
        difficulty_analyzer: DifficultyAnalyzer,
        collection_manager: SmartCollectionManager,
        data_path: Optional[str] = None
    ):
        self.difficulty_analyzer = difficulty_analyzer
        self.collection_manager = collection_manager
        self.data_path = Path(data_path or "data/study_planning")
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Load user preferences and historical data
        self.preferences = self._load_preferences()
        self.performance_history = self._load_performance_history()
        self.circadian_patterns = self._load_circadian_patterns()
    
    def plan_session(
        self, 
        deck: Deck, 
        context: StudyContext,
        preferences: Optional[StudyPreferences] = None
    ) -> StudyPlan:
        """
        Create an optimal study session plan based on context and preferences.
        
        Args:
            deck: The deck to study from
            context: Current study context (time, energy, etc.)
            preferences: Optional user preferences override
            
        Returns:
            Optimized study plan
        """
        prefs = preferences or self.preferences
        
        # Analyze available cards and their states
        card_analysis = self._analyze_available_cards(deck)
        
        # Determine optimal session structure
        session_structure = self._determine_session_structure(context, prefs)
        
        # Select and sequence cards
        card_selection = self._select_cards_for_session(
            deck, card_analysis, session_structure, context, prefs
        )
        
        # Create study segments
        segments = self._create_study_segments(
            card_selection, session_structure, context, prefs
        )
        
        # Generate break schedule
        break_schedule = self._generate_break_schedule(segments, prefs)
        
        # Calculate confidence and optimization notes
        confidence, notes = self._evaluate_plan_quality(
            segments, context, prefs, card_analysis
        )
        
        return StudyPlan(
            session_id=self._generate_session_id(),
            total_duration=context.available_time,
            segments=segments,
            estimated_cards=sum(len(seg.cards) for seg in segments),
            difficulty_progression=[
                sum(card.difficulty for card in seg.cards) / len(seg.cards)
                for seg in segments if seg.cards
            ],
            break_schedule=break_schedule,
            optimization_notes=notes,
            confidence_score=confidence
        )
    
    def _analyze_available_cards(self, deck: Deck) -> Dict[str, Any]:
        """Analyze the current state of cards in the deck."""
        due_cards = deck.get_due_cards()
        all_cards = deck.flashcards
        
        # Categorize cards by difficulty and review status
        easy_cards = [c for c in all_cards if c.difficulty < 0.3]
        medium_cards = [c for c in all_cards if 0.3 <= c.difficulty < 0.7]
        hard_cards = [c for c in all_cards if c.difficulty >= 0.7]
        
        new_cards = [c for c in all_cards if c.review_count == 0]
        review_cards = [c for c in all_cards if c.review_count > 0]
        
        # Calculate urgency scores
        urgency_scores = {}
        for card in all_cards:
            urgency = self._calculate_card_urgency(card)
            urgency_scores[card.id] = urgency
        
        return {
            'total_cards': len(all_cards),
            'due_cards': due_cards,
            'easy_cards': easy_cards,
            'medium_cards': medium_cards,
            'hard_cards': hard_cards,
            'new_cards': new_cards,
            'review_cards': review_cards,
            'urgency_scores': urgency_scores,
            'avg_difficulty': sum(c.difficulty for c in all_cards) / len(all_cards),
            'due_ratio': len(due_cards) / len(all_cards) if all_cards else 0
        }
    
    def _determine_session_structure(
        self, 
        context: StudyContext, 
        prefs: StudyPreferences
    ) -> Dict[str, Any]:
        """Determine the optimal structure for the study session."""
        # Adjust for energy level
        energy_multiplier = {
            EnergyLevel.VERY_LOW: 0.6,
            EnergyLevel.LOW: 0.8,
            EnergyLevel.MEDIUM: 1.0,
            EnergyLevel.HIGH: 1.2,
            EnergyLevel.VERY_HIGH: 1.4
        }[context.energy_level]
        
        # Adjust for time of day (circadian rhythm)
        hour = context.time_of_day.hour
        circadian_multiplier = self._get_circadian_multiplier(hour)
        
        # Calculate effective session parameters
        effective_duration = min(
            context.available_time,
            int(prefs.max_session_length * energy_multiplier * circadian_multiplier)
        )
        
        # Determine session phases
        warmup_duration = max(2, int(effective_duration * 0.1))
        core_duration = int(effective_duration * 0.7)
        challenge_duration = int(effective_duration * 0.15) if context.energy_level.value >= 3 else 0
        cooldown_duration = max(2, int(effective_duration * 0.05))
        
        return {
            'effective_duration': effective_duration,
            'warmup_duration': warmup_duration,
            'core_duration': core_duration,
            'challenge_duration': challenge_duration,
            'cooldown_duration': cooldown_duration,
            'energy_multiplier': energy_multiplier,
            'circadian_multiplier': circadian_multiplier
        }
    
    def _select_cards_for_session(
        self,
        deck: Deck,
        card_analysis: Dict[str, Any],
        session_structure: Dict[str, Any],
        context: StudyContext,
        prefs: StudyPreferences
    ) -> Dict[str, List[Flashcard]]:
        """Select and categorize cards for different session phases."""
        # Estimate cards per minute based on difficulty
        base_cards_per_minute = 2.0
        energy_factor = context.energy_level.value / 3.0
        cards_per_minute = base_cards_per_minute * energy_factor
        
        # Calculate target cards for each phase
        warmup_cards = max(1, int(session_structure['warmup_duration'] * cards_per_minute))
        core_cards = max(1, int(session_structure['core_duration'] * cards_per_minute))
        challenge_cards = max(0, int(session_structure['challenge_duration'] * cards_per_minute))
        cooldown_cards = max(1, int(session_structure['cooldown_duration'] * cards_per_minute))
        
        # Select cards for warmup (easy, familiar cards)
        warmup_selection = self._select_warmup_cards(
            card_analysis, warmup_cards, context
        )
        
        # Select cards for core session (mix based on goals)
        core_selection = self._select_core_cards(
            card_analysis, core_cards, context, prefs
        )
        
        # Select cards for challenge phase (difficult cards)
        challenge_selection = self._select_challenge_cards(
            card_analysis, challenge_cards, context
        ) if challenge_cards > 0 else []
        
        # Select cards for cooldown (easy review)
        cooldown_selection = self._select_cooldown_cards(
            card_analysis, cooldown_cards, context
        )
        
        return {
            'warmup': warmup_selection,
            'core': core_selection,
            'challenge': challenge_selection,
            'cooldown': cooldown_selection
        }
    
    def _select_warmup_cards(
        self, 
        card_analysis: Dict[str, Any], 
        target_count: int,
        context: StudyContext
    ) -> List[Flashcard]:
        """Select easy, familiar cards for warmup."""
        candidates = [
            card for card in card_analysis['easy_cards']
            if card.review_count > 0 and card.calculate_accuracy() > 0.8
        ]
        
        # Sort by familiarity (high accuracy, low difficulty)
        candidates.sort(
            key=lambda c: (c.calculate_accuracy(), -c.difficulty, -c.review_count),
            reverse=True
        )
        
        return candidates[:target_count]
    
    def _select_core_cards(
        self,
        card_analysis: Dict[str, Any],
        target_count: int,
        context: StudyContext,
        prefs: StudyPreferences
    ) -> List[Flashcard]:
        """Select cards for the main study session."""
        # Determine new vs review ratio based on goals
        new_ratio = prefs.new_card_ratio
        if StudyGoal.ACQUISITION in context.goals:
            new_ratio = min(0.5, new_ratio * 1.5)
        elif StudyGoal.REVIEW in context.goals:
            new_ratio = max(0.1, new_ratio * 0.5)
        
        new_count = int(target_count * new_ratio)
        review_count = target_count - new_count
        
        # Select new cards
        new_cards = self._select_new_cards(card_analysis, new_count, context)
        
        # Select review cards (prioritize due cards)
        review_cards = self._select_review_cards(card_analysis, review_count, context)
        
        # Combine and shuffle for optimal spacing
        all_cards = new_cards + review_cards
        return self._optimize_card_sequence(all_cards, context)
    
    def _select_challenge_cards(
        self,
        card_analysis: Dict[str, Any],
        target_count: int,
        context: StudyContext
    ) -> List[Flashcard]:
        """Select challenging cards for advanced practice."""
        candidates = [
            card for card in card_analysis['hard_cards']
            if card.review_count > 0
        ]
        
        # Sort by difficulty and recent performance
        candidates.sort(
            key=lambda c: (c.difficulty, -c.calculate_accuracy()),
            reverse=True
        )
        
        return candidates[:target_count]
    
    def _select_cooldown_cards(
        self,
        card_analysis: Dict[str, Any],
        target_count: int,
        context: StudyContext
    ) -> List[Flashcard]:
        """Select easy cards for session cooldown."""
        candidates = [
            card for card in card_analysis['easy_cards']
            if card.calculate_accuracy() > 0.9
        ]
        
        candidates.sort(key=lambda c: c.calculate_accuracy(), reverse=True)
        return candidates[:target_count]
    
    def _create_study_segments(
        self,
        card_selection: Dict[str, List[Flashcard]],
        session_structure: Dict[str, Any],
        context: StudyContext,
        prefs: StudyPreferences
    ) -> List[StudySegment]:
        """Create structured study segments."""
        segments = []
        
        # Warmup segment
        if card_selection['warmup']:
            segments.append(StudySegment(
                cards=card_selection['warmup'],
                estimated_duration=session_structure['warmup_duration'],
                difficulty_range=(0.0, 0.3),
                segment_type="warmup"
            ))
        
        # Core segment (may be split into multiple segments)
        core_cards = card_selection['core']
        if core_cards:
            # Split core into smaller segments if session is long
            if session_structure['core_duration'] > 20:
                mid_point = len(core_cards) // 2
                segments.append(StudySegment(
                    cards=core_cards[:mid_point],
                    estimated_duration=session_structure['core_duration'] // 2,
                    difficulty_range=(0.2, 0.8),
                    segment_type="core",
                    break_after=True,
                    break_duration=prefs.break_duration
                ))
                segments.append(StudySegment(
                    cards=core_cards[mid_point:],
                    estimated_duration=session_structure['core_duration'] // 2,
                    difficulty_range=(0.2, 0.8),
                    segment_type="core"
                ))
            else:
                segments.append(StudySegment(
                    cards=core_cards,
                    estimated_duration=session_structure['core_duration'],
                    difficulty_range=(0.2, 0.8),
                    segment_type="core"
                ))
        
        # Challenge segment
        if card_selection['challenge']:
            segments.append(StudySegment(
                cards=card_selection['challenge'],
                estimated_duration=session_structure['challenge_duration'],
                difficulty_range=(0.7, 1.0),
                segment_type="challenge"
            ))
        
        # Cooldown segment
        if card_selection['cooldown']:
            segments.append(StudySegment(
                cards=card_selection['cooldown'],
                estimated_duration=session_structure['cooldown_duration'],
                difficulty_range=(0.0, 0.3),
                segment_type="cooldown"
            ))
        
        return segments
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _calculate_card_urgency(self, card: Flashcard) -> float:
        """Calculate how urgently a card needs to be reviewed."""
        if not card.last_reviewed:
            return 1.0  # New cards have high urgency
        
        days_since_review = (datetime.now() - card.last_reviewed).days
        if card.is_due_for_review():
            return min(2.0, 1.0 + (days_since_review * 0.1))
        
        return max(0.1, 1.0 - (days_since_review * 0.05))
    
    def _get_circadian_multiplier(self, hour: int) -> float:
        """Get performance multiplier based on time of day."""
        # Default circadian pattern (can be personalized)
        if 6 <= hour < 10:  # Morning peak
            return 1.2
        elif 10 <= hour < 14:  # Late morning
            return 1.1
        elif 14 <= hour < 16:  # Post-lunch dip
            return 0.8
        elif 16 <= hour < 19:  # Afternoon peak
            return 1.1
        elif 19 <= hour < 22:  # Evening
            return 0.9
        else:  # Night/early morning
            return 0.6
    
    def _load_preferences(self) -> StudyPreferences:
        """Load user preferences from storage."""
        prefs_file = self.data_path / "preferences.json"
        if prefs_file.exists():
            try:
                with open(prefs_file, 'r') as f:
                    data = json.load(f)
                return StudyPreferences(**data)
            except Exception:
                pass
        return StudyPreferences()
    
    def _load_performance_history(self) -> Dict[str, Any]:
        """Load historical performance data."""
        history_file = self.data_path / "performance_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _load_circadian_patterns(self) -> Dict[str, float]:
        """Load personalized circadian rhythm patterns."""
        patterns_file = self.data_path / "circadian_patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    # Additional helper methods would be implemented here...
    def _select_new_cards(self, card_analysis: Dict, count: int, context: StudyContext) -> List[Flashcard]:
        """Select new cards for learning."""
        return card_analysis['new_cards'][:count]
    
    def _select_review_cards(self, card_analysis: Dict, count: int, context: StudyContext) -> List[Flashcard]:
        """Select review cards prioritizing due cards."""
        due_cards = card_analysis['due_cards']
        if len(due_cards) >= count:
            return due_cards[:count]
        
        remaining = count - len(due_cards)
        other_cards = [c for c in card_analysis['review_cards'] if c not in due_cards]
        return due_cards + other_cards[:remaining]
    
    def _optimize_card_sequence(self, cards: List[Flashcard], context: StudyContext) -> List[Flashcard]:
        """Optimize the sequence of cards for better learning."""
        # Simple interleaving for now - can be enhanced with more sophisticated algorithms
        return cards
    
    def _generate_break_schedule(self, segments: List[StudySegment], prefs: StudyPreferences) -> List[int]:
        """Generate optimal break schedule."""
        breaks = []
        current_time = 0
        
        for segment in segments:
            current_time += segment.estimated_duration
            if segment.break_after:
                breaks.append(current_time)
                current_time += segment.break_duration
        
        return breaks
    
    def _evaluate_plan_quality(
        self,
        segments: List[StudySegment],
        context: StudyContext,
        prefs: StudyPreferences,
        card_analysis: Dict[str, Any]
    ) -> Tuple[float, List[str]]:
        """Evaluate the quality of the study plan."""
        confidence = 0.8  # Base confidence
        notes = []
        
        total_cards = sum(len(seg.cards) for seg in segments)
        if total_cards < 5:
            confidence -= 0.2
            notes.append("Limited card selection due to constraints")
        
        if context.energy_level.value < 3:
            notes.append("Session adapted for low energy level")
        
        if context.available_time < 15:
            confidence -= 0.1
            notes.append("Short session may limit effectiveness")
        
        return confidence, notes
