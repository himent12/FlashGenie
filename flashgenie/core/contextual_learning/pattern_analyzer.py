"""
Pattern analysis utilities for the contextual learning system.

This module provides functions to identify and analyze performance patterns.
"""

from typing import Dict, List, Any
import statistics
from .models import PerformancePattern


class PatternAnalyzer:
    """Analyzes performance patterns based on context."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        pass
    
    def analyze_time_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze time-based performance patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of time-based performance patterns
        """
        patterns = []
        
        # Group by time of day
        time_groups = {}
        for session in performance_history:
            time_of_day = session.get("time_of_day", "unknown")
            if time_of_day not in time_groups:
                time_groups[time_of_day] = []
            time_groups[time_of_day].append(session)
        
        # Analyze each time group
        for time_of_day, sessions in time_groups.items():
            if len(sessions) >= 3:  # Need minimum data
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                avg_completion = statistics.mean([s.get("completion_rate", 0) for s in sessions])
                
                if avg_accuracy > 0.8:  # High performance pattern
                    pattern = PerformancePattern(
                        pattern_id=f"time_{time_of_day}",
                        name=f"High Performance - {time_of_day.title()}",
                        description=f"Consistently high performance during {time_of_day}",
                        context_factors={"time_of_day": time_of_day},
                        performance_metrics={"accuracy": avg_accuracy, "completion_rate": avg_completion},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_energy_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze energy-based performance patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of energy-based performance patterns
        """
        patterns = []
        
        # Group by energy level
        energy_groups = {}
        for session in performance_history:
            energy = session.get("energy_level", 3)
            if energy not in energy_groups:
                energy_groups[energy] = []
            energy_groups[energy].append(session)
        
        # Find optimal energy levels
        for energy_level, sessions in energy_groups.items():
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                
                if avg_accuracy > 0.85:
                    pattern = PerformancePattern(
                        pattern_id=f"energy_{energy_level}",
                        name=f"Optimal Energy Level {energy_level}",
                        description=f"High performance at energy level {energy_level}",
                        context_factors={"energy_level": energy_level},
                        performance_metrics={"accuracy": avg_accuracy},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_environment_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze environment-based performance patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of environment-based performance patterns
        """
        patterns = []
        
        # Group by environment
        env_groups = {}
        for session in performance_history:
            environment = session.get("environment", "unknown")
            if environment not in env_groups:
                env_groups[environment] = []
            env_groups[environment].append(session)
        
        # Find optimal environments
        for environment, sessions in env_groups.items():
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                avg_satisfaction = statistics.mean([s.get("satisfaction", 3) for s in sessions])
                
                if avg_accuracy > 0.8 and avg_satisfaction > 3.5:
                    pattern = PerformancePattern(
                        pattern_id=f"env_{environment}",
                        name=f"Optimal Environment - {environment.title()}",
                        description=f"High performance in {environment} environment",
                        context_factors={"environment": environment},
                        performance_metrics={"accuracy": avg_accuracy, "satisfaction": avg_satisfaction},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_difficulty_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze difficulty preference patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of difficulty-based performance patterns
        """
        patterns = []
        
        # Group by difficulty ranges
        difficulty_ranges = [(0.0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)]
        
        for min_diff, max_diff in difficulty_ranges:
            relevant_sessions = [
                s for s in performance_history
                if min_diff <= s.get("avg_difficulty", 0.5) < max_diff
            ]
            
            if len(relevant_sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in relevant_sessions])
                avg_engagement = statistics.mean([s.get("engagement", 3) for s in relevant_sessions])
                
                if avg_accuracy > 0.8 and avg_engagement > 3.5:
                    pattern = PerformancePattern(
                        pattern_id=f"difficulty_{min_diff}_{max_diff}",
                        name=f"Optimal Difficulty Range {min_diff}-{max_diff}",
                        description=f"High performance with difficulty {min_diff}-{max_diff}",
                        context_factors={"difficulty_range": (min_diff, max_diff)},
                        performance_metrics={"accuracy": avg_accuracy, "engagement": avg_engagement},
                        occurrence_count=len(relevant_sessions),
                        confidence_level=min(len(relevant_sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_session_length_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze session length performance patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of session length-based performance patterns
        """
        patterns = []
        
        # Group by session length ranges
        length_ranges = [(0, 15), (15, 30), (30, 45), (45, 60), (60, 120)]
        
        for min_length, max_length in length_ranges:
            relevant_sessions = [
                s for s in performance_history
                if min_length <= s.get("duration", 30) < max_length
            ]
            
            if len(relevant_sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in relevant_sessions])
                avg_completion = statistics.mean([s.get("completion_rate", 0) for s in relevant_sessions])
                avg_satisfaction = statistics.mean([s.get("satisfaction", 3) for s in relevant_sessions])
                
                if avg_accuracy > 0.8 and avg_completion > 0.8:
                    pattern = PerformancePattern(
                        pattern_id=f"length_{min_length}_{max_length}",
                        name=f"Optimal Session Length {min_length}-{max_length} min",
                        description=f"High performance with {min_length}-{max_length} minute sessions",
                        context_factors={"session_length_range": (min_length, max_length)},
                        performance_metrics={
                            "accuracy": avg_accuracy, 
                            "completion_rate": avg_completion,
                            "satisfaction": avg_satisfaction
                        },
                        occurrence_count=len(relevant_sessions),
                        confidence_level=min(len(relevant_sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def analyze_break_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Analyze break frequency and duration patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of break-related performance patterns
        """
        patterns = []
        
        # Group by break frequency
        break_groups = {}
        for session in performance_history:
            break_count = session.get("break_count", 0)
            session_duration = session.get("duration", 30)
            
            # Calculate breaks per hour
            if session_duration > 0:
                breaks_per_hour = (break_count / session_duration) * 60
                break_category = self._categorize_break_frequency(breaks_per_hour)
                
                if break_category not in break_groups:
                    break_groups[break_category] = []
                break_groups[break_category].append(session)
        
        # Analyze each break frequency group
        for break_category, sessions in break_groups.items():
            if len(sessions) >= 3:
                avg_accuracy = statistics.mean([s.get("accuracy", 0) for s in sessions])
                avg_focus = statistics.mean([s.get("focus_rating", 3) for s in sessions])
                
                if avg_accuracy > 0.8 and avg_focus > 3.5:
                    pattern = PerformancePattern(
                        pattern_id=f"breaks_{break_category}",
                        name=f"Optimal Break Pattern - {break_category.title()}",
                        description=f"High performance with {break_category} break frequency",
                        context_factors={"break_pattern": break_category},
                        performance_metrics={"accuracy": avg_accuracy, "focus": avg_focus},
                        occurrence_count=len(sessions),
                        confidence_level=min(len(sessions) / 10, 1.0)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _categorize_break_frequency(self, breaks_per_hour: float) -> str:
        """Categorize break frequency."""
        if breaks_per_hour < 1:
            return "minimal"
        elif breaks_per_hour < 2:
            return "low"
        elif breaks_per_hour < 3:
            return "moderate"
        elif breaks_per_hour < 4:
            return "frequent"
        else:
            return "very_frequent"
    
    def identify_all_patterns(self, performance_history: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """
        Identify all performance patterns.
        
        Args:
            performance_history: Historical performance data
            
        Returns:
            List of all identified performance patterns
        """
        all_patterns = []
        
        # Analyze different types of patterns
        all_patterns.extend(self.analyze_time_patterns(performance_history))
        all_patterns.extend(self.analyze_energy_patterns(performance_history))
        all_patterns.extend(self.analyze_environment_patterns(performance_history))
        all_patterns.extend(self.analyze_difficulty_patterns(performance_history))
        all_patterns.extend(self.analyze_session_length_patterns(performance_history))
        all_patterns.extend(self.analyze_break_patterns(performance_history))
        
        # Sort by confidence level
        all_patterns.sort(key=lambda p: p.confidence_level, reverse=True)
        
        return all_patterns
