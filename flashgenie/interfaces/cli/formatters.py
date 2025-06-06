"""
Output formatting utilities for the CLI interface.

This module provides functions for formatting and displaying
information in the terminal with colors and styling.
"""

from typing import List, Dict, Any, Optional
import os

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    # Fallback if colorama is not available
    COLORS_AVAILABLE = False
    
    class _DummyColor:
        def __getattr__(self, name):
            return ""
    
    Fore = Back = Style = _DummyColor()


class OutputFormatter:
    """
    Formatter for terminal output with color support.
    """
    
    def __init__(self, use_colors: bool = None):
        """
        Initialize the output formatter.
        
        Args:
            use_colors: Whether to use colors (auto-detect if None)
        """
        if use_colors is None:
            # Auto-detect color support
            use_colors = COLORS_AVAILABLE and self._supports_color()
        
        self.use_colors = use_colors
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports colors."""
        return (
            hasattr(os.sys.stdout, "isatty") and 
            os.sys.stdout.isatty() and 
            os.environ.get("TERM") != "dumb"
        )
    
    def success(self, text: str) -> str:
        """Format success message."""
        if self.use_colors:
            return f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}"
        return f"✓ {text}"
    
    def error(self, text: str) -> str:
        """Format error message."""
        if self.use_colors:
            return f"{Fore.RED}✗ {text}{Style.RESET_ALL}"
        return f"✗ {text}"
    
    def warning(self, text: str) -> str:
        """Format warning message."""
        if self.use_colors:
            return f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}"
        return f"⚠ {text}"
    
    def info(self, text: str) -> str:
        """Format info message."""
        if self.use_colors:
            return f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}"
        return f"ℹ {text}"
    
    def highlight(self, text: str) -> str:
        """Highlight text."""
        if self.use_colors:
            return f"{Style.BRIGHT}{text}{Style.RESET_ALL}"
        return text
    
    def dim(self, text: str) -> str:
        """Dim text."""
        if self.use_colors:
            return f"{Style.DIM}{text}{Style.RESET_ALL}"
        return text
    
    def header(self, text: str, char: str = "=") -> str:
        """Format header with underline."""
        underline = char * len(text)
        if self.use_colors:
            return f"{Style.BRIGHT}{text}{Style.RESET_ALL}\n{underline}"
        return f"{text}\n{underline}"
    
    def subheader(self, text: str) -> str:
        """Format subheader."""
        return self.header(text, "-")
    
    def progress_bar(self, current: int, total: int, width: int = 30) -> str:
        """Create a progress bar."""
        if total == 0:
            percentage = 0
        else:
            percentage = current / total
        
        filled = int(width * percentage)
        bar = "█" * filled + "░" * (width - filled)
        
        if self.use_colors:
            return f"{Fore.GREEN}{bar}{Style.RESET_ALL} {current}/{total} ({percentage:.1%})"
        return f"{bar} {current}/{total} ({percentage:.1%})"
    
    def table(self, headers: List[str], rows: List[List[str]], 
              max_width: int = 80) -> str:
        """Format data as a table."""
        if not rows:
            return "No data to display"
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Adjust widths if table is too wide
        total_width = sum(col_widths) + len(headers) * 3 - 1
        if total_width > max_width:
            # Proportionally reduce column widths
            reduction_factor = max_width / total_width
            col_widths = [max(10, int(w * reduction_factor)) for w in col_widths]
        
        # Format table
        lines = []
        
        # Header
        header_line = " | ".join(
            header.ljust(col_widths[i])[:col_widths[i]] 
            for i, header in enumerate(headers)
        )
        if self.use_colors:
            header_line = f"{Style.BRIGHT}{header_line}{Style.RESET_ALL}"
        lines.append(header_line)
        
        # Separator
        separator = "-+-".join("-" * w for w in col_widths)
        lines.append(separator)
        
        # Data rows
        for row in rows:
            row_line = " | ".join(
                str(cell).ljust(col_widths[i])[:col_widths[i]]
                for i, cell in enumerate(row)
            )
            lines.append(row_line)
        
        return "\n".join(lines)
    
    def quiz_question(self, question: str, question_num: int, total: int) -> str:
        """Format a quiz question."""
        header = f"Question {question_num}/{total}"
        if self.use_colors:
            header = f"{Style.BRIGHT}{Fore.BLUE}{header}{Style.RESET_ALL}"
        
        separator = "=" * len(header)
        
        return f"\n{header}\n{separator}\n\n{question}\n"
    
    def quiz_result(self, correct: bool, correct_answer: str, 
                   user_answer: str = None) -> str:
        """Format quiz result."""
        if correct:
            result = self.success("Correct!")
        else:
            result = self.error("Incorrect!")
            if user_answer:
                result += f"\nYour answer: {self.dim(user_answer)}"
            result += f"\nCorrect answer: {self.highlight(correct_answer)}"
        
        return result
    
    def quiz_stats(self, correct: int, total: int, accuracy: float) -> str:
        """Format quiz statistics."""
        stats = [
            f"Questions answered: {total}",
            f"Correct answers: {correct}",
            f"Accuracy: {accuracy:.1%}"
        ]
        
        if self.use_colors:
            if accuracy >= 0.8:
                color = Fore.GREEN
            elif accuracy >= 0.6:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            
            stats[-1] = f"Accuracy: {color}{accuracy:.1%}{Style.RESET_ALL}"
        
        return "\n".join(stats)
    
    def deck_summary(self, deck_info: Dict[str, Any]) -> str:
        """Format deck summary information."""
        lines = [
            f"Name: {self.highlight(deck_info['name'])}",
            f"Cards: {deck_info['card_count']}",
        ]
        
        if deck_info.get('due_count', 0) > 0:
            lines.append(f"Due for review: {self.warning(str(deck_info['due_count']))}")
        
        if deck_info.get('description'):
            lines.append(f"Description: {deck_info['description']}")
        
        if deck_info.get('tags'):
            tags = ", ".join(deck_info['tags'])
            lines.append(f"Tags: {self.dim(tags)}")
        
        return "\n".join(lines)
    
    def menu_options(self, options: List[str], title: str = "Options") -> str:
        """Format menu options."""
        lines = [self.header(title)]
        
        for i, option in enumerate(options, 1):
            lines.append(f"{i}. {option}")
        
        return "\n".join(lines)
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_separator(self, char: str = "-", width: int = 50) -> str:
        """Create a separator line."""
        return char * width
