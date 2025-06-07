"""
Interactive widgets for FlashGenie's Rich Terminal UI.

This module provides reusable UI components and widgets for the terminal interface.
Enhanced for Phase 2 with interactive controls and advanced widgets.
"""

from typing import Any, Dict, List, Union, Optional, Callable
import time
import threading
from datetime import datetime

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.status import Status
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.tree import Tree


class WidgetManager:
    """Manages interactive widgets and UI components."""

    def __init__(self, console: Console):
        """Initialize the widget manager."""
        self.console = console

    def create_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
        show_lines: bool = True
    ) -> Table:
        """Create a formatted table."""
        table = Table(
            title=title,
            show_header=True,
            header_style="bold bright_blue",
            show_lines=show_lines,
            expand=True
        )

        # Add columns
        for header in headers:
            table.add_column(header, style="bright_white")

        # Add rows
        for row in rows:
            table.add_row(*row)

        return table

    def create_stats_panel(self, stats: Dict[str, Any], title: str = "Statistics") -> Panel:
        """Create a statistics panel."""
        stats_content = []

        for key, value in stats.items():
            stat_text = Text()
            stat_text.append(f"{key}: ", style="bright_white")

            # Format value based on type
            if isinstance(value, float):
                if 0 <= value <= 1:
                    # Treat as percentage
                    stat_text.append(f"{value:.1%}", style="bright_green")
                else:
                    stat_text.append(f"{value:.2f}", style="bright_cyan")
            elif isinstance(value, int):
                stat_text.append(str(value), style="bright_cyan")
            else:
                stat_text.append(str(value), style="bright_white")

            stats_content.append(stat_text)

        return Panel(
            Group(*stats_content),
            title=f"📊 {title}",
            border_style="bright_green",
            padding=(1, 2)
        )

    def create_card_display(
        self,
        question: str,
        answer: str = None,
        hint: str = None,
        tags: List[str] = None,
        difficulty: float = None
    ) -> Panel:
        """Create a flashcard display panel."""
        card_content = []

        # Question
        question_text = Text(question, style="bright_white")
        card_content.append(question_text)

        # Answer (if provided)
        if answer:
            card_content.append(Text(""))
            answer_text = Text()
            answer_text.append("Answer: ", style="bright_green")
            answer_text.append(answer, style="bright_white")
            card_content.append(answer_text)

        # Hint (if provided)
        if hint:
            card_content.append(Text(""))
            hint_text = Text()
            hint_text.append("💡 Hint: ", style="bright_yellow")
            hint_text.append(hint, style="dim")
            card_content.append(hint_text)

        # Tags (if provided)
        if tags:
            card_content.append(Text(""))
            tags_text = Text()
            tags_text.append("🏷️  Tags: ", style="bright_blue")
            tags_text.append(", ".join(tags), style="bright_cyan")
            card_content.append(tags_text)

        # Difficulty (if provided)
        if difficulty is not None:
            card_content.append(Text(""))
            diff_text = Text()
            diff_text.append("⭐ Difficulty: ", style="bright_magenta")

            # Show difficulty as stars
            stars = "●" * int(difficulty * 5) + "○" * (5 - int(difficulty * 5))
            if difficulty < 0.3:
                diff_text.append(stars, style="bright_green")
            elif difficulty < 0.7:
                diff_text.append(stars, style="bright_yellow")
            else:
                diff_text.append(stars, style="bright_red")

            card_content.append(diff_text)

        return Panel(
            Group(*card_content),
            title="📚 Flashcard",
            border_style="bright_blue",
            padding=(1, 2)
        )

    def create_status_indicator(self, message: str) -> Status:
        """Create a status indicator with spinner."""
        return Status(message, console=self.console, spinner="dots")

    def create_multi_select_menu(
        self,
        title: str,
        options: List[str],
        description: str = None,
        max_selections: int = None
    ) -> List[int]:
        """
        Create an interactive multi-select menu with checkboxes.

        Args:
            title: Menu title
            options: List of options to choose from
            description: Optional description
            max_selections: Maximum number of selections allowed

        Returns:
            List of selected option indices
        """
        selected = set()
        current = 0

        while True:
            # Clear screen and show menu
            self.console.clear()

            # Create menu content
            menu_content = []

            if description:
                menu_content.append(Text(description, style="dim"))
                menu_content.append(Text(""))

            # Instructions
            instructions = Text()
            instructions.append("Use ↑/↓ to navigate, ", style="dim")
            instructions.append("SPACE", style="bright_yellow")
            instructions.append(" to select/deselect, ", style="dim")
            instructions.append("ENTER", style="bright_green")
            instructions.append(" to confirm", style="dim")
            menu_content.append(instructions)
            menu_content.append(Text(""))

            # Add options with checkboxes
            for i, option in enumerate(options):
                option_text = Text()

                # Checkbox
                if i in selected:
                    option_text.append("☑️ ", style="bright_green")
                else:
                    option_text.append("☐ ", style="dim")

                # Option text with highlighting for current selection
                if i == current:
                    option_text.append(f"► {option}", style="bright_blue bold")
                else:
                    option_text.append(f"  {option}", style="bright_white")

                menu_content.append(option_text)

            # Selection count
            if max_selections:
                count_text = Text(f"\nSelected: {len(selected)}/{max_selections}", style="bright_cyan")
            else:
                count_text = Text(f"\nSelected: {len(selected)}", style="bright_cyan")
            menu_content.append(count_text)

            # Create and display panel
            menu_panel = Panel(
                Group(*menu_content),
                title=f"📋 {title}",
                border_style="bright_blue",
                padding=(1, 2)
            )

            self.console.print(menu_panel)

            # Get user input (simplified for demo - in real implementation would use keyboard input)
            try:
                action = input("\nAction (u/d/space/enter/q): ").strip().lower()

                if action == 'u' and current > 0:
                    current -= 1
                elif action == 'd' and current < len(options) - 1:
                    current += 1
                elif action == 'space':
                    if current in selected:
                        selected.remove(current)
                    else:
                        if max_selections is None or len(selected) < max_selections:
                            selected.add(current)
                elif action == 'enter':
                    return sorted(list(selected))
                elif action == 'q':
                    return []

            except KeyboardInterrupt:
                return []

    def create_progress_dashboard(
        self,
        tasks: Dict[str, Dict[str, Any]],
        title: str = "Progress Dashboard"
    ) -> Layout:
        """
        Create a progress dashboard with multiple progress bars.

        Args:
            tasks: Dictionary of task information
            title: Dashboard title

        Returns:
            Rich Layout with progress dashboard
        """
        layout = Layout()

        # Split into header and body
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body")
        )

        # Header
        header_text = Text(title, style="bold bright_blue")
        timestamp = datetime.now().strftime("%H:%M:%S")
        header_content = Columns([
            Align.left(header_text),
            Align.right(Text(f"⏰ {timestamp}", style="dim"))
        ])

        header_panel = Panel(
            header_content,
            style="bright_blue",
            height=3
        )
        layout["header"].update(header_panel)

        # Body with progress bars
        progress_content = []

        for task_name, task_info in tasks.items():
            current = task_info.get("current", 0)
            total = task_info.get("total", 100)
            status = task_info.get("status", "running")

            # Progress bar
            progress_chars = int((current / total) * 30) if total > 0 else 0
            if status == "complete":
                progress_bar = "█" * 30
                bar_style = "bright_green"
            elif status == "error":
                progress_bar = "█" * progress_chars + "░" * (30 - progress_chars)
                bar_style = "bright_red"
            else:
                progress_bar = "█" * progress_chars + "░" * (30 - progress_chars)
                bar_style = "bright_blue"

            # Task line
            task_text = Text()
            task_text.append(f"{task_name}: ", style="bright_white")
            task_text.append(progress_bar, style=bar_style)
            task_text.append(f" {current}/{total} ({current/total:.0%})" if total > 0 else " 0/0", style="bright_white")

            # Status indicator
            if status == "complete":
                task_text.append(" ✅", style="bright_green")
            elif status == "error":
                task_text.append(" ❌", style="bright_red")
            elif status == "running":
                task_text.append(" ⏳", style="bright_yellow")

            progress_content.append(task_text)

        body_panel = Panel(
            Group(*progress_content),
            title="📊 Task Progress",
            border_style="bright_blue",
            padding=(1, 2)
        )
        layout["body"].update(body_panel)

        return layout

    def create_form_builder(self, fields: Dict[str, Dict[str, Any]], title: str = "Form") -> Dict[str, Any]:
        """
        Create an interactive form with validation.

        Args:
            fields: Dictionary of field definitions
            title: Form title

        Returns:
            Dictionary of user inputs
        """
        results = {}

        # Show form header
        form_header = Panel(
            Group(
                Text(f"📝 {title}", style="bold bright_blue"),
                Text("Fill out the following form. Press Ctrl+C to cancel.", style="dim")
            ),
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(form_header)

        # Process each field
        for field_name, field_config in fields.items():
            field_type = field_config.get("type", "text")
            prompt_text = field_config.get("prompt", field_name.replace("_", " ").title())
            default = field_config.get("default")
            required = field_config.get("required", False)
            validation = field_config.get("validation")

            while True:
                try:
                    # Show field prompt
                    field_panel = Panel(
                        Text(prompt_text, style="bright_yellow"),
                        title=f"Field: {field_name}",
                        border_style="bright_yellow",
                        padding=(0, 1)
                    )
                    self.console.print(field_panel)

                    # Get input based on type
                    if field_type == "text":
                        value = Prompt.ask("Value", default=default, console=self.console)
                    elif field_type == "int":
                        value = IntPrompt.ask("Value", default=default, console=self.console)
                    elif field_type == "float":
                        value = FloatPrompt.ask("Value", default=default, console=self.console)
                    elif field_type == "bool":
                        value = Confirm.ask("Value", default=default, console=self.console)
                    elif field_type == "choice":
                        choices = field_config.get("choices", [])
                        if choices:
                            self.console.print("Available choices:")
                            for i, choice in enumerate(choices, 1):
                                self.console.print(f"  {i}. {choice}")
                            choice_idx = IntPrompt.ask(
                                "Choice number",
                                choices=list(range(1, len(choices) + 1)),
                                console=self.console
                            )
                            value = choices[choice_idx - 1]
                        else:
                            value = Prompt.ask("Value", default=default, console=self.console)
                    else:
                        value = Prompt.ask("Value", default=default, console=self.console)

                    # Validate required fields
                    if required and not value:
                        self.console.print("❌ This field is required.", style="bright_red")
                        continue

                    # Custom validation
                    if validation and value:
                        if callable(validation):
                            if not validation(value):
                                self.console.print("❌ Invalid value. Please try again.", style="bright_red")
                                continue
                        elif isinstance(validation, dict):
                            min_val = validation.get("min")
                            max_val = validation.get("max")
                            pattern = validation.get("pattern")

                            if min_val is not None and value < min_val:
                                self.console.print(f"❌ Value must be at least {min_val}.", style="bright_red")
                                continue
                            if max_val is not None and value > max_val:
                                self.console.print(f"❌ Value must be at most {max_val}.", style="bright_red")
                                continue
                            if pattern and isinstance(value, str):
                                import re
                                if not re.match(pattern, value):
                                    self.console.print("❌ Value doesn't match required pattern.", style="bright_red")
                                    continue

                    results[field_name] = value
                    self.console.print(f"✅ {field_name}: {value}", style="bright_green")
                    break

                except KeyboardInterrupt:
                    self.console.print("\n❌ Form cancelled", style="bright_red")
                    return {}
                except Exception as e:
                    self.console.print(f"❌ Error: {e}", style="bright_red")

        # Show form summary
        summary_content = []
        for key, value in results.items():
            summary_content.append(Text(f"{key}: {value}", style="bright_white"))

        summary_panel = Panel(
            Group(*summary_content),
            title="📋 Form Summary",
            border_style="bright_green",
            padding=(1, 2)
        )
        self.console.print(summary_panel)

        return results