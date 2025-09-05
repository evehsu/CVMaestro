"""Terminal-based user interface for CVMaestro."""

import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from ..models import Resume, UserProfile
from ..services import ContentAnalyzer


class TerminalInterface:
    """
    Terminal-based interface for user interaction.

    Provides a conversational interface for collecting user information,
    displaying analysis results, and guiding the resume improvement process.
    """

    def __init__(self) -> None:
        """Initialize the terminal interface."""
        self.console = Console()
        self.content_analyzer = ContentAnalyzer()

    def welcome_user(self) -> None:
        """Display welcome message and introduction."""
        self.console.clear()

        welcome_text = Text("CVMaestro", style="bold magenta")
        welcome_text.append(" - Intelligent Resume Builder", style="bold blue")

        welcome_panel = Panel(
            welcome_text,
            subtitle="Transform your resume with AI-powered insights",
            border_style="blue",
        )

        self.console.print(welcome_panel)
        self.console.print()

        intro_text = [
            "Welcome to CVMaestro! I'll help you create a professional, impactful resume.",
            "",
            "Here's what we'll do together:",
            "  1. Collect your basic information",
            "  2. Analyze your current resume (if you have one)",
            "  3. Identify areas for improvement",
            "  4. Generate an enhanced resume",
            "",
            "Let's get started! ✨",
        ]

        for line in intro_text:
            self.console.print(line)

        self.console.print()
        Prompt.ask("Press Enter to continue", default="")

    def collect_user_profile(self) -> UserProfile:
        """
        Collect user profile information through interactive prompts.

        Returns:
            UserProfile object with collected information
        """
        self.console.print("\n[bold blue]📝 Let's start with your basic information[/bold blue]\n")

        # Collect target position
        target_position = Prompt.ask(
            "What position are you targeting?", default="Software Engineer"
        ).strip()

        # Collect years of experience
        years_of_experience = IntPrompt.ask(
            "How many years of relevant work experience do you have?", default=2
        )

        # Collect target level (optional)
        target_level = None
        if Confirm.ask("Would you like to specify your target career level?", default=False):
            level_choices = ["junior", "mid", "senior", "executive"]
            self.console.print("\nCareer levels:")
            for i, level in enumerate(level_choices, 1):
                self.console.print(f"  {i}. {level.title()}")

            level_choice = IntPrompt.ask(
                "Select your target level (1-4)", choices=["1", "2", "3", "4"], default=2
            )
            target_level = level_choices[level_choice - 1]

        # Create and validate profile
        profile = UserProfile(
            years_of_experience=years_of_experience,
            target_position=target_position,
            target_level=target_level,
        )

        # Show profile summary
        self.display_profile_summary(profile)

        return profile

    def display_profile_summary(self, profile: UserProfile) -> None:
        """Display a summary of the collected profile information."""
        table = Table(title="Your Profile Summary", border_style="green")
        table.add_column("Field", style="bold")
        table.add_column("Value", style="cyan")

        table.add_row("Target Position", profile.target_position)
        table.add_row("Years of Experience", str(profile.years_of_experience))
        table.add_row("Experience Tier", profile.get_experience_tier().title())

        if profile.target_level:
            table.add_row("Target Level", profile.target_level.title())
        else:
            table.add_row("Suggested Level", profile.suggest_target_level().title())

        self.console.print(table)
        self.console.print()

    def collect_resume_file(self) -> str | None:
        """
        Collect resume file path from user.

        Returns:
            Path to resume file, or None if user chooses to start from scratch
        """
        self.console.print("\n[bold blue]📄 Resume File[/bold blue]\n")

        has_resume = Confirm.ask("Do you have an existing resume file to improve?", default=True)

        if not has_resume:
            self.console.print("No problem! We'll help you build one from scratch.")
            return None

        while True:
            file_path = Prompt.ask(
                "Enter the path to your resume file (markdown format supported)", default=""
            ).strip()

            if not file_path:
                if Confirm.ask("Skip file upload and start from scratch?", default=False):
                    return None
                continue

            # Validate file exists
            path = Path(file_path).expanduser().resolve()
            if path.exists():
                self.console.print(f"✅ Found resume file: {path}")
                return str(path)
            else:
                self.console.print(f"❌ File not found: {file_path}")
                if Confirm.ask("Try again?", default=True):
                    continue
                else:
                    return None

    def display_resume_analysis(self, resume: Resume) -> None:
        """
        Display resume analysis results.

        Args:
            resume: Resume object with analysis results
        """
        self.console.print("\n[bold blue]🔍 Resume Analysis Results[/bold blue]\n")

        if resume.is_empty():
            self.console.print("No content found to analyze.")
            return

        # Create sections table
        table = Table(title="Resume Sections", border_style="blue")
        table.add_column("Section", style="bold")
        table.add_column("Content Length", justify="right")
        table.add_column("Quality Score", justify="center")
        table.add_column("Status", justify="center")

        for section_name in resume.get_all_sections():
            content = resume.get_section(section_name)
            word_count = len(content.split())
            quality_score = self.content_analyzer.assess_quality(content, section_name)

            # Determine status
            if quality_score >= 0.8:
                status = "[green]Good[/green]"
            elif quality_score >= 0.6:
                status = "[yellow]Needs Work[/yellow]"
            else:
                status = "[red]Poor[/red]"

            table.add_row(
                section_name.title(), f"{word_count} words", f"{quality_score:.1f}", status
            )

        self.console.print(table)
        self.console.print()

    def display_section_problems(self, section_name: str, problems: list[str]) -> None:
        """
        Display problems identified in a specific section.

        Args:
            section_name: Name of the section
            problems: List of problems to display
        """
        if not problems:
            return

        self.console.print(f"\n[bold red]⚠️ Issues in {section_name.title()} section:[/bold red]")
        for i, problem in enumerate(problems, 1):
            self.console.print(f"  {i}. {problem}")

    def prompt_for_missing_info(self, section_name: str, questions: list[str]) -> dict[str, str]:
        """
        Prompt user for missing information in a section.

        Args:
            section_name: Name of the section needing information
            questions: List of questions to ask

        Returns:
            Dictionary of question -> answer pairs
        """
        self.console.print(
            f"\n[bold blue]📝 Let's improve your {section_name.title()} section[/bold blue]\n"
        )

        answers = {}
        for i, question in enumerate(questions, 1):
            self.console.print(f"Question {i}/{len(questions)}:")
            answer = Prompt.ask(question, default="").strip()
            if answer:
                answers[question] = answer

        return answers

    def confirm_changes(self, section_name: str, old_content: str, new_content: str) -> bool:
        """
        Show proposed changes and get user confirmation.

        Args:
            section_name: Name of the section being changed
            old_content: Original content
            new_content: Proposed new content

        Returns:
            True if user confirms changes
        """
        self.console.print(
            f"\n[bold blue]📝 Proposed changes for {section_name.title()}:[/bold blue]\n"
        )

        # Show old content
        old_panel = Panel(
            old_content[:500] + ("..." if len(old_content) > 500 else ""),
            title="Current Content",
            border_style="red",
        )
        self.console.print(old_panel)

        # Show new content
        new_panel = Panel(
            new_content[:500] + ("..." if len(new_content) > 500 else ""),
            title="Improved Content",
            border_style="green",
        )
        self.console.print(new_panel)

        return Confirm.ask("\nApply these changes?", default=True)

    def show_progress(self, description: str, items: list[str]) -> None:
        """
        Show progress for a list of items.

        Args:
            description: Description of the task
            items: List of items being processed
        """
        self.console.print(f"\n[bold blue]{description}[/bold blue]")

        for _item in track(items, description="Processing..."):
            time.sleep(0.5)  # Simulate processing time

    def display_final_summary(self, resume: Resume) -> None:
        """
        Display final summary of resume improvements.

        Args:
            resume: Final resume object
        """
        self.console.print("\n[bold green]🎉 Resume improvement complete![/bold green]\n")

        # Show statistics
        improved_sections = sum(
            1 for section in resume.get_all_sections() if resume.has_revised_content(section)
        )
        total_sections = len(resume.get_all_sections())

        stats_table = Table(title="Improvement Summary", border_style="green")
        stats_table.add_column("Metric", style="bold")
        stats_table.add_column("Value", style="cyan")

        stats_table.add_row("Total Sections", str(total_sections))
        stats_table.add_row("Improved Sections", str(improved_sections))
        stats_table.add_row("Improvement Rate", f"{improved_sections / total_sections * 100:.1f}%")

        self.console.print(stats_table)
        self.console.print()

    def prompt_export_options(self) -> dict[str, str]:
        """
        Prompt user for export options.

        Returns:
            Dictionary with export preferences
        """
        self.console.print("\n[bold blue]💾 Export Options[/bold blue]\n")

        export_format = Prompt.ask("Export format", choices=["markdown", "txt"], default="markdown")

        output_path = Prompt.ask("Output file path", default=f"improved_resume.{export_format}")

        return {"format": export_format, "path": output_path}

    def display_error(self, message: str) -> None:
        """Display an error message."""
        error_panel = Panel(f"[bold red]Error:[/bold red] {message}", border_style="red")
        self.console.print(error_panel)

    def display_success(self, message: str) -> None:
        """Display a success message."""
        success_panel = Panel(f"[bold green]Success:[/bold green] {message}", border_style="green")
        self.console.print(success_panel)
