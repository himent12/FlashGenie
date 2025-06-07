"""
Advanced Search and Filtering System for FlashGenie v1.8.3.

This module provides fuzzy search, real-time filtering, and advanced
search capabilities for the Rich Terminal UI.
"""

import re
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
from difflib import SequenceMatcher

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt


@dataclass
class SearchResult:
    """Search result with relevance score."""
    item: Any
    score: float
    matched_fields: List[str]
    highlights: Dict[str, str]


class FuzzySearchEngine:
    """
    Advanced fuzzy search engine with real-time filtering.
    
    Provides intelligent search with typo tolerance, field weighting,
    and relevance scoring.
    """
    
    def __init__(self):
        """Initialize the search engine."""
        self.search_history: List[str] = []
        self.filters: Dict[str, Any] = {}
        self.field_weights: Dict[str, float] = {}
    
    def fuzzy_match(self, query: str, text: str, threshold: float = 0.6) -> float:
        """
        Calculate fuzzy match score between query and text.
        
        Args:
            query: Search query
            text: Text to search in
            threshold: Minimum similarity threshold
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not query or not text:
            return 0.0
        
        query = query.lower().strip()
        text = text.lower().strip()
        
        # Exact match gets highest score
        if query == text:
            return 1.0
        
        # Substring match gets high score
        if query in text:
            return 0.9
        
        # Fuzzy matching using SequenceMatcher
        similarity = SequenceMatcher(None, query, text).ratio()
        
        # Check for word-level matches
        query_words = query.split()
        text_words = text.split()
        
        word_matches = 0
        for q_word in query_words:
            for t_word in text_words:
                if q_word in t_word or SequenceMatcher(None, q_word, t_word).ratio() > 0.8:
                    word_matches += 1
                    break
        
        word_score = word_matches / len(query_words) if query_words else 0
        
        # Combine scores
        final_score = max(similarity, word_score * 0.8)
        
        return final_score if final_score >= threshold else 0.0
    
    def search(
        self, 
        items: List[Dict[str, Any]], 
        query: str,
        fields: List[str],
        max_results: int = 50,
        threshold: float = 0.3
    ) -> List[SearchResult]:
        """
        Perform fuzzy search on items.
        
        Args:
            items: List of items to search
            query: Search query
            fields: Fields to search in
            max_results: Maximum number of results
            threshold: Minimum relevance threshold
            
        Returns:
            List of search results sorted by relevance
        """
        if not query.strip():
            return [SearchResult(item, 1.0, [], {}) for item in items[:max_results]]
        
        results = []
        
        for item in items:
            total_score = 0.0
            matched_fields = []
            highlights = {}
            
            for field in fields:
                field_value = str(item.get(field, ""))
                if not field_value:
                    continue
                
                # Calculate field score
                field_score = self.fuzzy_match(query, field_value, threshold)
                
                if field_score > 0:
                    # Apply field weight
                    weight = self.field_weights.get(field, 1.0)
                    weighted_score = field_score * weight
                    total_score += weighted_score
                    matched_fields.append(field)
                    
                    # Create highlight
                    highlights[field] = self._highlight_matches(query, field_value)
            
            # Normalize score by number of fields
            if matched_fields:
                avg_score = total_score / len(matched_fields)
                if avg_score >= threshold:
                    results.append(SearchResult(
                        item=item,
                        score=avg_score,
                        matched_fields=matched_fields,
                        highlights=highlights
                    ))
        
        # Sort by relevance score
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Add to search history
        if query not in self.search_history:
            self.search_history.append(query)
            if len(self.search_history) > 50:
                self.search_history = self.search_history[-50:]
        
        return results[:max_results]
    
    def _highlight_matches(self, query: str, text: str) -> str:
        """
        Highlight matching parts of text.
        
        Args:
            query: Search query
            text: Text to highlight
            
        Returns:
            Text with Rich markup for highlights
        """
        if not query or not text:
            return text
        
        query_words = query.lower().split()
        highlighted_text = text
        
        for word in query_words:
            # Case-insensitive replacement with highlighting
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted_text = pattern.sub(
                lambda m: f"[bold bright_yellow]{m.group()}[/bold bright_yellow]",
                highlighted_text
            )
        
        return highlighted_text
    
    def set_field_weights(self, weights: Dict[str, float]) -> None:
        """
        Set field weights for search relevance.
        
        Args:
            weights: Dictionary of field names to weight multipliers
        """
        self.field_weights = weights
    
    def add_filter(self, name: str, filter_func: Callable[[Any], bool]) -> None:
        """
        Add a filter function.
        
        Args:
            name: Filter name
            filter_func: Function that returns True for items to include
        """
        self.filters[name] = filter_func
    
    def remove_filter(self, name: str) -> None:
        """Remove a filter."""
        self.filters.pop(name, None)
    
    def apply_filters(self, items: List[Any]) -> List[Any]:
        """Apply all active filters to items."""
        filtered_items = items
        
        for filter_func in self.filters.values():
            filtered_items = [item for item in filtered_items if filter_func(item)]
        
        return filtered_items


class InteractiveSearchInterface:
    """
    Interactive search interface with real-time results.
    
    Provides a live search experience with instant feedback
    and advanced filtering options.
    """
    
    def __init__(self, console: Console):
        """
        Initialize the search interface.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.search_engine = FuzzySearchEngine()
        self.current_results: List[SearchResult] = []
        self.selected_index = 0
    
    def interactive_search(
        self,
        items: List[Dict[str, Any]],
        fields: List[str],
        title: str = "Search",
        display_fields: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Run interactive search with real-time results.
        
        Args:
            items: Items to search through
            fields: Fields to search in
            title: Search interface title
            display_fields: Fields to display in results
            
        Returns:
            Selected item or None if cancelled
        """
        if display_fields is None:
            display_fields = fields
        
        query = ""
        
        while True:
            # Clear screen and show search interface
            self.console.clear()
            
            # Create search layout
            layout = self._create_search_layout(query, title)
            
            # Perform search
            if query.strip():
                self.current_results = self.search_engine.search(items, query, fields)
            else:
                self.current_results = [SearchResult(item, 1.0, [], {}) for item in items[:20]]
            
            # Update results in layout
            results_content = self._create_results_display(display_fields)
            layout["results"].update(Panel(
                results_content,
                title=f"📋 Results ({len(self.current_results)})",
                border_style="bright_blue"
            ))
            
            # Display layout
            self.console.print(layout)
            
            # Get user input
            try:
                action = input("\nAction (type/up/down/enter/esc): ").strip()
                
                if action == "esc":
                    return None
                elif action == "up":
                    if self.current_results and self.selected_index > 0:
                        self.selected_index -= 1
                elif action == "down":
                    if self.current_results and self.selected_index < len(self.current_results) - 1:
                        self.selected_index += 1
                elif action == "enter":
                    if self.current_results and 0 <= self.selected_index < len(self.current_results):
                        return self.current_results[self.selected_index].item
                    return None
                else:
                    # Treat as typing
                    if action == "backspace":
                        query = query[:-1]
                    else:
                        query += action
                    
                    self.selected_index = 0  # Reset selection when query changes
                    
            except KeyboardInterrupt:
                return None
    
    def _create_search_layout(self, query: str, title: str) -> Layout:
        """Create the search interface layout."""
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="results"),
            Layout(name="footer", size=3)
        )
        
        # Header with search box
        search_content = Group(
            Text(f"🔍 {title}", style="bold bright_blue"),
            Text(""),
            Text(f"Search: {query}_", style="bright_white on blue")
        )
        
        layout["header"].update(Panel(
            search_content,
            border_style="bright_blue"
        ))
        
        # Footer with instructions
        instructions = Text()
        instructions.append("Type to search, ", style="dim")
        instructions.append("↑/↓", style="bright_yellow")
        instructions.append(" to navigate, ", style="dim")
        instructions.append("Enter", style="bright_green")
        instructions.append(" to select, ", style="dim")
        instructions.append("Esc", style="bright_red")
        instructions.append(" to cancel", style="dim")
        
        layout["footer"].update(Panel(
            instructions,
            border_style="dim"
        ))
        
        return layout
    
    def _create_results_display(self, display_fields: List[str]) -> Group:
        """Create the results display."""
        if not self.current_results:
            return Group(Text("No results found", style="dim"))
        
        content = []
        
        for i, result in enumerate(self.current_results[:10]):  # Show top 10
            item = result.item
            
            # Create result text
            result_text = Text()
            
            # Selection indicator
            if i == self.selected_index:
                result_text.append("► ", style="bright_blue")
            else:
                result_text.append("  ", style="dim")
            
            # Display fields
            field_parts = []
            for field in display_fields:
                value = str(item.get(field, ""))
                if value:
                    # Use highlighted version if available
                    if field in result.highlights:
                        field_parts.append(f"{field}: {result.highlights[field]}")
                    else:
                        field_parts.append(f"{field}: {value}")
            
            result_text.append(" | ".join(field_parts[:3]))  # Show first 3 fields
            
            # Relevance score
            if result.score < 1.0:
                result_text.append(f" ({result.score:.2f})", style="dim")
            
            content.append(result_text)
        
        if len(self.current_results) > 10:
            content.append(Text(f"... and {len(self.current_results) - 10} more results", style="dim"))
        
        return Group(*content)
    
    def quick_filter_menu(self, items: List[Dict[str, Any]], filters: Dict[str, Callable]) -> List[Dict[str, Any]]:
        """
        Show a quick filter menu for items.
        
        Args:
            items: Items to filter
            filters: Available filters
            
        Returns:
            Filtered items
        """
        active_filters = set()
        
        while True:
            # Show filter menu
            self.console.clear()
            
            filter_content = []
            filter_content.append(Text("📋 Quick Filters", style="bold bright_blue"))
            filter_content.append(Text(""))
            
            for i, (filter_name, filter_func) in enumerate(filters.items(), 1):
                filter_text = Text()
                
                # Checkbox
                if filter_name in active_filters:
                    filter_text.append("☑️ ", style="bright_green")
                else:
                    filter_text.append("☐ ", style="dim")
                
                filter_text.append(f"{i}. {filter_name}", style="bright_white")
                filter_content.append(filter_text)
            
            filter_content.append(Text(""))
            filter_content.append(Text("0. Apply filters and continue", style="bright_green"))
            
            # Show current item count
            filtered_items = items
            for filter_name in active_filters:
                if filter_name in filters:
                    filtered_items = [item for item in filtered_items if filters[filter_name](item)]
            
            filter_content.append(Text(f"\nItems: {len(filtered_items)}/{len(items)}", style="bright_cyan"))
            
            filter_panel = Panel(
                Group(*filter_content),
                title="🔍 Filter Menu",
                border_style="bright_blue",
                padding=(1, 2)
            )
            
            self.console.print(filter_panel)
            
            # Get user choice
            try:
                choice = input("\nEnter choice: ").strip()
                
                if choice == "0":
                    # Apply filters and return
                    for filter_name in active_filters:
                        if filter_name in filters:
                            filtered_items = [item for item in filtered_items if filters[filter_name](item)]
                    return filtered_items
                
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(filters):
                        filter_name = list(filters.keys())[choice_num - 1]
                        if filter_name in active_filters:
                            active_filters.remove(filter_name)
                        else:
                            active_filters.add(filter_name)
                except ValueError:
                    pass
                    
            except KeyboardInterrupt:
                return items
