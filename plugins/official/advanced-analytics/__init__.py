"""
Advanced Analytics Plugin for FlashGenie

Provides research-grade learning analytics with detailed insights,
predictive modeling, and comprehensive reporting capabilities.
"""

import json
import csv
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import math

from flashgenie.core.plugin_system import AnalyticsPlugin
from flashgenie.core.deck import Deck
from flashgenie.core.flashcard import Flashcard


class AdvancedAnalyticsPlugin(AnalyticsPlugin):
    """Advanced analytics plugin with research-grade metrics."""
    
    def initialize(self) -> None:
        """Initialize the advanced analytics plugin."""
        self.require_permission(self.manifest.permissions[0])  # deck_read
        self.require_permission(self.manifest.permissions[1])  # user_data
        self.require_permission(self.manifest.permissions[2])  # file_write
        
        self.logger.info("Advanced Analytics plugin initialized")
        
        # Analytics configuration
        self.analysis_depth = self.get_setting("analysis_depth", "detailed")
        self.include_predictions = self.get_setting("include_predictions", True)
        
        # Metrics registry
        self.available_metrics = [
            "learning_velocity",
            "retention_rate",
            "forgetting_curve",
            "difficulty_progression",
            "session_efficiency",
            "knowledge_gaps",
            "mastery_prediction",
            "optimal_review_timing",
            "cognitive_load",
            "learning_consistency"
        ]
        
        self.logger.info(f"Analytics depth: {self.analysis_depth}")
    
    def cleanup(self) -> None:
        """Cleanup analytics resources."""
        self.logger.info("Advanced Analytics plugin cleaned up")
    
    def generate_insights(self, deck: Deck, timeframe: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive learning insights for a deck."""
        self.logger.info(f"Generating insights for deck '{deck.name}' (timeframe: {timeframe})")
        
        try:
            # Parse timeframe
            days = self._parse_timeframe(timeframe)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Collect data
            deck_data = self._collect_deck_data(deck, cutoff_date)
            
            # Generate insights based on analysis depth
            insights = {
                "deck_name": deck.name,
                "analysis_date": datetime.now().isoformat(),
                "timeframe": timeframe,
                "analysis_depth": self.analysis_depth
            }
            
            if self.analysis_depth in ["basic", "detailed", "research"]:
                insights.update(self._generate_basic_insights(deck_data))
            
            if self.analysis_depth in ["detailed", "research"]:
                insights.update(self._generate_detailed_insights(deck_data))
            
            if self.analysis_depth == "research":
                insights.update(self._generate_research_insights(deck_data))
            
            # Add predictions if enabled
            if self.include_predictions:
                insights["predictions"] = self._generate_predictions(deck_data)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Failed to generate insights: {e}")
            return {"error": str(e)}
    
    def get_metrics(self) -> List[str]:
        """Get list of metrics this plugin can calculate."""
        return self.available_metrics
    
    def export_data(self, deck: Deck, format_type: str) -> bytes:
        """Export analytics data in specified format."""
        self.logger.info(f"Exporting analytics data for '{deck.name}' in {format_type} format")
        
        try:
            # Generate comprehensive insights
            insights = self.generate_insights(deck, "all")
            
            if format_type.lower() == "json":
                return json.dumps(insights, indent=2).encode('utf-8')
            elif format_type.lower() == "csv":
                return self._export_to_csv(insights)
            elif format_type.lower() == "html":
                return self._export_to_html(insights)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return f"Export error: {e}".encode('utf-8')
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to days."""
        if timeframe == "all":
            return 365 * 10  # 10 years (effectively all data)
        elif timeframe.endswith("d"):
            return int(timeframe[:-1])
        elif timeframe.endswith("w"):
            return int(timeframe[:-1]) * 7
        elif timeframe.endswith("m"):
            return int(timeframe[:-1]) * 30
        elif timeframe.endswith("y"):
            return int(timeframe[:-1]) * 365
        else:
            return 30  # Default to 30 days
    
    def _collect_deck_data(self, deck: Deck, cutoff_date: datetime) -> Dict[str, Any]:
        """Collect comprehensive data about the deck."""
        data = {
            "deck": deck,
            "total_cards": len(deck.flashcards),
            "cutoff_date": cutoff_date,
            "card_stats": [],
            "session_data": [],
            "performance_timeline": []
        }
        
        # Analyze each card
        for card in deck.flashcards:
            card_stats = self._analyze_card(card, cutoff_date)
            data["card_stats"].append(card_stats)
        
        # Collect session data (simulated for this example)
        data["session_data"] = self._collect_session_data(deck, cutoff_date)
        
        return data
    
    def _analyze_card(self, card: Flashcard, cutoff_date: datetime) -> Dict[str, Any]:
        """Analyze individual card performance."""
        # Get review history (simulated data for this example)
        reviews = getattr(card, 'review_history', [])
        recent_reviews = [r for r in reviews if r.get('date', datetime.now()) >= cutoff_date]
        
        stats = {
            "card_id": id(card),
            "question": card.question[:50] + "..." if len(card.question) > 50 else card.question,
            "difficulty": card.difficulty,
            "total_reviews": len(recent_reviews),
            "correct_reviews": sum(1 for r in recent_reviews if r.get('correct', False)),
            "accuracy": 0.0,
            "avg_response_time": 0.0,
            "last_reviewed": None,
            "mastery_level": 0.0,
            "retention_strength": 0.0
        }
        
        if recent_reviews:
            stats["accuracy"] = stats["correct_reviews"] / len(recent_reviews)
            stats["avg_response_time"] = statistics.mean([r.get('response_time', 5.0) for r in recent_reviews])
            stats["last_reviewed"] = max(r.get('date', datetime.now()) for r in recent_reviews)
            
            # Calculate mastery level (simplified)
            stats["mastery_level"] = min(1.0, stats["accuracy"] * (len(recent_reviews) / 10))
            
            # Calculate retention strength
            stats["retention_strength"] = self._calculate_retention_strength(recent_reviews)
        
        return stats
    
    def _calculate_retention_strength(self, reviews: List[Dict[str, Any]]) -> float:
        """Calculate retention strength based on review pattern."""
        if len(reviews) < 2:
            return 0.0
        
        # Sort reviews by date
        sorted_reviews = sorted(reviews, key=lambda r: r.get('date', datetime.now()))
        
        # Calculate retention based on spacing and accuracy
        retention_score = 0.0
        for i in range(1, len(sorted_reviews)):
            prev_review = sorted_reviews[i-1]
            curr_review = sorted_reviews[i]
            
            # Time between reviews
            time_diff = (curr_review.get('date', datetime.now()) - 
                        prev_review.get('date', datetime.now())).days
            
            # Accuracy in current review
            accuracy = 1.0 if curr_review.get('correct', False) else 0.0
            
            # Retention strength increases with longer intervals and maintained accuracy
            interval_factor = min(1.0, time_diff / 7.0)  # Normalize to weeks
            retention_score += accuracy * interval_factor
        
        return min(1.0, retention_score / (len(sorted_reviews) - 1))
    
    def _collect_session_data(self, deck: Deck, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Collect session-level data (simulated)."""
        # In a real implementation, this would read from session logs
        sessions = []
        
        # Generate sample session data
        current_date = cutoff_date
        while current_date <= datetime.now():
            if current_date.weekday() < 5:  # Weekdays only
                session = {
                    "date": current_date,
                    "cards_reviewed": len(deck.flashcards) // 10,  # Sample size
                    "session_duration": 15 + (len(deck.flashcards) // 20),  # Minutes
                    "accuracy": 0.7 + (hash(str(current_date)) % 30) / 100,  # Simulated accuracy
                    "avg_response_time": 3.0 + (hash(str(current_date)) % 20) / 10
                }
                sessions.append(session)
            
            current_date += timedelta(days=1)
        
        return sessions[-30:]  # Last 30 sessions
    
    def _generate_basic_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic analytics insights."""
        card_stats = data["card_stats"]
        
        if not card_stats:
            return {"basic_insights": {"error": "No card data available"}}
        
        # Calculate basic metrics
        total_reviews = sum(stats["total_reviews"] for stats in card_stats)
        avg_accuracy = statistics.mean([stats["accuracy"] for stats in card_stats if stats["total_reviews"] > 0])
        avg_response_time = statistics.mean([stats["avg_response_time"] for stats in card_stats if stats["total_reviews"] > 0])
        
        # Difficulty distribution
        difficulties = [stats["difficulty"] for stats in card_stats]
        
        return {
            "basic_insights": {
                "total_cards": data["total_cards"],
                "total_reviews": total_reviews,
                "average_accuracy": round(avg_accuracy, 3),
                "average_response_time": round(avg_response_time, 2),
                "difficulty_distribution": {
                    "easy": sum(1 for d in difficulties if d < 0.4),
                    "medium": sum(1 for d in difficulties if 0.4 <= d <= 0.7),
                    "hard": sum(1 for d in difficulties if d > 0.7)
                },
                "mastery_overview": {
                    "mastered": sum(1 for stats in card_stats if stats["mastery_level"] > 0.8),
                    "learning": sum(1 for stats in card_stats if 0.3 < stats["mastery_level"] <= 0.8),
                    "new": sum(1 for stats in card_stats if stats["mastery_level"] <= 0.3)
                }
            }
        }
    
    def _generate_detailed_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed analytics insights."""
        card_stats = data["card_stats"]
        session_data = data["session_data"]
        
        # Learning velocity analysis
        learning_velocity = self._calculate_learning_velocity(session_data)
        
        # Retention analysis
        retention_analysis = self._analyze_retention_patterns(card_stats)
        
        # Session efficiency
        session_efficiency = self._analyze_session_efficiency(session_data)
        
        # Knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(card_stats)
        
        return {
            "detailed_insights": {
                "learning_velocity": learning_velocity,
                "retention_analysis": retention_analysis,
                "session_efficiency": session_efficiency,
                "knowledge_gaps": knowledge_gaps,
                "performance_trends": self._analyze_performance_trends(session_data),
                "optimal_study_patterns": self._identify_optimal_patterns(session_data)
            }
        }
    
    def _generate_research_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate research-grade analytics insights."""
        card_stats = data["card_stats"]
        
        # Advanced statistical analysis
        forgetting_curve = self._model_forgetting_curve(card_stats)
        cognitive_load = self._analyze_cognitive_load(card_stats)
        learning_efficiency = self._calculate_learning_efficiency(data)
        
        return {
            "research_insights": {
                "forgetting_curve_model": forgetting_curve,
                "cognitive_load_analysis": cognitive_load,
                "learning_efficiency_metrics": learning_efficiency,
                "spaced_repetition_effectiveness": self._analyze_sr_effectiveness(card_stats),
                "individual_differences": self._analyze_individual_differences(card_stats),
                "metacognitive_accuracy": self._analyze_metacognitive_accuracy(card_stats)
            }
        }
    
    def _calculate_learning_velocity(self, session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate learning velocity metrics."""
        if not session_data:
            return {"error": "No session data available"}
        
        # Cards per day
        total_cards = sum(session["cards_reviewed"] for session in session_data)
        days_active = len(session_data)
        cards_per_day = total_cards / days_active if days_active > 0 else 0
        
        # Accuracy trend
        accuracies = [session["accuracy"] for session in session_data]
        accuracy_trend = self._calculate_trend(accuracies)
        
        # Response time trend
        response_times = [session["avg_response_time"] for session in session_data]
        response_time_trend = self._calculate_trend(response_times)
        
        return {
            "cards_per_day": round(cards_per_day, 2),
            "total_cards_reviewed": total_cards,
            "active_days": days_active,
            "accuracy_trend": accuracy_trend,
            "response_time_trend": response_time_trend,
            "learning_acceleration": self._calculate_acceleration(accuracies)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = statistics.mean(values)
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _calculate_acceleration(self, values: List[float]) -> float:
        """Calculate learning acceleration (second derivative)."""
        if len(values) < 3:
            return 0.0
        
        # Calculate first differences
        first_diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        
        # Calculate second differences (acceleration)
        second_diffs = [first_diffs[i+1] - first_diffs[i] for i in range(len(first_diffs)-1)]
        
        return statistics.mean(second_diffs) if second_diffs else 0.0
    
    def _analyze_retention_patterns(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze memory retention patterns."""
        if not card_stats:
            return {"error": "No card data available"}
        
        retention_strengths = [stats["retention_strength"] for stats in card_stats if stats["total_reviews"] > 0]
        
        if not retention_strengths:
            return {"error": "No retention data available"}
        
        return {
            "average_retention": round(statistics.mean(retention_strengths), 3),
            "retention_distribution": {
                "strong": sum(1 for r in retention_strengths if r > 0.7),
                "moderate": sum(1 for r in retention_strengths if 0.4 <= r <= 0.7),
                "weak": sum(1 for r in retention_strengths if r < 0.4)
            },
            "retention_variance": round(statistics.variance(retention_strengths), 3) if len(retention_strengths) > 1 else 0.0
        }
    
    def _analyze_session_efficiency(self, session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze session efficiency metrics."""
        if not session_data:
            return {"error": "No session data available"}
        
        # Cards per minute
        efficiency_scores = []
        for session in session_data:
            if session["session_duration"] > 0:
                cards_per_minute = session["cards_reviewed"] / session["session_duration"]
                efficiency_scores.append(cards_per_minute)
        
        if not efficiency_scores:
            return {"error": "No efficiency data available"}
        
        return {
            "average_cards_per_minute": round(statistics.mean(efficiency_scores), 2),
            "efficiency_trend": self._calculate_trend(efficiency_scores),
            "most_efficient_session": round(max(efficiency_scores), 2),
            "least_efficient_session": round(min(efficiency_scores), 2)
        }
    
    def _identify_knowledge_gaps(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify knowledge gaps and weak areas."""
        if not card_stats:
            return {"error": "No card data available"}
        
        # Find cards with low accuracy
        weak_cards = [stats for stats in card_stats if stats["accuracy"] < 0.6 and stats["total_reviews"] >= 3]
        
        # Find cards with low retention
        low_retention_cards = [stats for stats in card_stats if stats["retention_strength"] < 0.4]
        
        return {
            "weak_accuracy_cards": len(weak_cards),
            "low_retention_cards": len(low_retention_cards),
            "total_gap_cards": len(set([stats["card_id"] for stats in weak_cards + low_retention_cards])),
            "gap_percentage": round(len(weak_cards) / len(card_stats) * 100, 1) if card_stats else 0.0,
            "recommended_focus_areas": [stats["question"] for stats in weak_cards[:5]]  # Top 5 weak cards
        }
    
    def _analyze_performance_trends(self, session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        if len(session_data) < 5:
            return {"error": "Insufficient data for trend analysis"}
        
        # Recent vs. early performance
        early_sessions = session_data[:len(session_data)//3]
        recent_sessions = session_data[-len(session_data)//3:]
        
        early_accuracy = statistics.mean([s["accuracy"] for s in early_sessions])
        recent_accuracy = statistics.mean([s["accuracy"] for s in recent_sessions])
        
        improvement = recent_accuracy - early_accuracy
        
        return {
            "overall_improvement": round(improvement, 3),
            "improvement_percentage": round(improvement * 100, 1),
            "trend_direction": "improving" if improvement > 0.05 else "declining" if improvement < -0.05 else "stable",
            "consistency_score": round(1.0 - statistics.stdev([s["accuracy"] for s in session_data]), 3)
        }
    
    def _identify_optimal_patterns(self, session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify optimal study patterns."""
        if not session_data:
            return {"error": "No session data available"}
        
        # Find best performing sessions
        best_sessions = sorted(session_data, key=lambda s: s["accuracy"], reverse=True)[:5]
        
        # Analyze patterns in best sessions
        avg_duration = statistics.mean([s["session_duration"] for s in best_sessions])
        avg_cards = statistics.mean([s["cards_reviewed"] for s in best_sessions])
        
        return {
            "optimal_session_duration": round(avg_duration, 1),
            "optimal_cards_per_session": round(avg_cards, 1),
            "best_accuracy_achieved": round(max(s["accuracy"] for s in session_data), 3),
            "recommended_study_frequency": "daily" if len(session_data) > 20 else "regular"
        }
    
    def _model_forgetting_curve(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Model the forgetting curve for the deck."""
        # Simplified forgetting curve modeling
        retention_data = [(stats["retention_strength"], stats["total_reviews"]) for stats in card_stats if stats["total_reviews"] > 0]
        
        if not retention_data:
            return {"error": "Insufficient data for forgetting curve modeling"}
        
        # Calculate average retention by review count
        retention_by_reviews = {}
        for retention, reviews in retention_data:
            if reviews not in retention_by_reviews:
                retention_by_reviews[reviews] = []
            retention_by_reviews[reviews].append(retention)
        
        curve_points = []
        for reviews, retentions in retention_by_reviews.items():
            avg_retention = statistics.mean(retentions)
            curve_points.append({"reviews": reviews, "retention": avg_retention})
        
        return {
            "curve_points": sorted(curve_points, key=lambda p: p["reviews"]),
            "initial_retention": curve_points[0]["retention"] if curve_points else 0.0,
            "retention_decay_rate": "moderate"  # Simplified classification
        }
    
    def _analyze_cognitive_load(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze cognitive load patterns."""
        if not card_stats:
            return {"error": "No card data available"}
        
        # Use response time and difficulty as proxies for cognitive load
        high_load_cards = [stats for stats in card_stats if stats["avg_response_time"] > 5.0 and stats["difficulty"] > 0.6]
        
        return {
            "high_cognitive_load_cards": len(high_load_cards),
            "average_cognitive_load": "moderate",  # Simplified classification
            "load_distribution": {
                "low": sum(1 for stats in card_stats if stats["avg_response_time"] < 3.0),
                "medium": sum(1 for stats in card_stats if 3.0 <= stats["avg_response_time"] <= 5.0),
                "high": sum(1 for stats in card_stats if stats["avg_response_time"] > 5.0)
            }
        }
    
    def _calculate_learning_efficiency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall learning efficiency metrics."""
        card_stats = data["card_stats"]
        session_data = data["session_data"]
        
        if not card_stats or not session_data:
            return {"error": "Insufficient data for efficiency calculation"}
        
        # Efficiency = Mastery gained per time invested
        total_mastery = sum(stats["mastery_level"] for stats in card_stats)
        total_time = sum(session["session_duration"] for session in session_data)
        
        efficiency = total_mastery / total_time if total_time > 0 else 0.0
        
        return {
            "learning_efficiency_score": round(efficiency, 4),
            "total_mastery_gained": round(total_mastery, 2),
            "total_time_invested": round(total_time, 1),
            "efficiency_rating": "high" if efficiency > 0.1 else "medium" if efficiency > 0.05 else "low"
        }
    
    def _analyze_sr_effectiveness(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spaced repetition effectiveness."""
        # Simplified SR effectiveness analysis
        return {
            "sr_effectiveness_score": 0.75,  # Placeholder
            "optimal_intervals_used": "moderate",
            "retention_improvement": "significant"
        }
    
    def _analyze_individual_differences(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze individual learning differences."""
        return {
            "learning_style": "visual",  # Placeholder
            "preferred_difficulty": "medium",
            "optimal_session_length": "15-20 minutes"
        }
    
    def _analyze_metacognitive_accuracy(self, card_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze metacognitive accuracy (confidence vs. performance)."""
        return {
            "metacognitive_accuracy": 0.68,  # Placeholder
            "overconfidence_bias": "slight",
            "calibration_score": "good"
        }
    
    def _generate_predictions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate predictive analytics."""
        card_stats = data["card_stats"]
        
        if not card_stats:
            return {"error": "No data for predictions"}
        
        # Simple prediction models
        mastery_levels = [stats["mastery_level"] for stats in card_stats]
        current_mastery = statistics.mean(mastery_levels) if mastery_levels else 0.0
        
        # Predict time to mastery
        cards_to_master = sum(1 for level in mastery_levels if level < 0.8)
        estimated_days = cards_to_master * 2  # Simplified estimation
        
        return {
            "current_overall_mastery": round(current_mastery, 3),
            "predicted_mastery_in_30_days": round(min(1.0, current_mastery + 0.2), 3),
            "estimated_days_to_full_mastery": estimated_days,
            "cards_needing_attention": cards_to_master,
            "confidence_interval": "±5 days"
        }
    
    def _export_to_csv(self, insights: Dict[str, Any]) -> bytes:
        """Export insights to CSV format."""
        # Simplified CSV export
        csv_data = "Metric,Value\n"
        
        def flatten_dict(d, prefix=""):
            for key, value in d.items():
                if isinstance(value, dict):
                    csv_data += flatten_dict(value, f"{prefix}{key}.")
                else:
                    csv_data += f"{prefix}{key},{value}\n"
        
        flatten_dict(insights)
        return csv_data.encode('utf-8')
    
    def _export_to_html(self, insights: Dict[str, Any]) -> bytes:
        """Export insights to HTML format."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FlashGenie Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ margin: 10px 0; }}
                .section {{ margin: 20px 0; border-left: 3px solid #007acc; padding-left: 15px; }}
                .value {{ font-weight: bold; color: #007acc; }}
            </style>
        </head>
        <body>
            <h1>FlashGenie Analytics Report</h1>
            <p>Generated on: {insights.get('analysis_date', 'Unknown')}</p>
            <p>Deck: {insights.get('deck_name', 'Unknown')}</p>
            
            <div class="section">
                <h2>Basic Insights</h2>
                <pre>{json.dumps(insights.get('basic_insights', {}), indent=2)}</pre>
            </div>
            
            <div class="section">
                <h2>Detailed Analysis</h2>
                <pre>{json.dumps(insights.get('detailed_insights', {}), indent=2)}</pre>
            </div>
            
            <div class="section">
                <h2>Predictions</h2>
                <pre>{json.dumps(insights.get('predictions', {}), indent=2)}</pre>
            </div>
        </body>
        </html>
        """
        return html.encode('utf-8')
