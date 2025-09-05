"""Main application entry point for CVMaestro."""

from pathlib import Path

import click

from .interfaces import TerminalInterface
from .models import Resume, UserProfile
from .services import ContentAnalyzer


class ResumeImprover:
    """
    Main application controller that orchestrates the resume improvement process.

    This class implements the core workflow from the PRD:
    1. User input collection
    2. Resume analysis and problem identification
    3. Iterative content improvement
    """

    def __init__(self) -> None:
        """Initialize the resume improver."""
        self.ui = TerminalInterface()
        self.content_analyzer = ContentAnalyzer()
        self.user_profile: UserProfile | None = None
        self.resume: Resume | None = None

    def run(self) -> None:
        """Run the main application workflow."""
        try:
            # Welcome and collect user information
            self.ui.welcome_user()
            self.user_profile = self.ui.collect_user_profile()

            # Load or create resume
            self.resume = self._load_or_create_resume()

            # Analyze current resume
            if not self.resume.is_empty():
                self._analyze_resume()

            # Improve resume content
            self._improve_resume_content()

            # Export final resume
            self._export_resume()

            # Show completion summary
            self.ui.display_final_summary(self.resume)

        except KeyboardInterrupt:
            self.ui.display_error("Process interrupted by user")
        except Exception as e:
            self.ui.display_error(f"An unexpected error occurred: {e}")

    def _load_or_create_resume(self) -> Resume:
        """Load existing resume or create new one."""
        resume = Resume()

        # Try to load existing resume file
        file_path = self.ui.collect_resume_file()

        if file_path:
            try:
                resume.parse_resume(file_path)
                self.ui.display_success(f"Successfully loaded resume from {file_path}")
            except Exception as e:
                self.ui.display_error(f"Could not load resume file: {e}")
                # Continue with empty resume

        return resume

    def _analyze_resume(self) -> None:
        """Analyze current resume and display results."""
        self.ui.display_resume_analysis(self.resume)

        # Analyze each section for problems
        for section_name in self.resume.get_all_sections():
            content = self.resume.get_section(section_name)
            suggestions = self.content_analyzer.suggest_improvements(content, section_name)

            if suggestions:
                self.ui.display_section_problems(section_name, suggestions)

    def _improve_resume_content(self) -> None:
        """Improve resume content section by section."""
        sections_to_process = self.resume.get_all_sections() if not self.resume.is_empty() else []

        # If resume is empty, help create basic sections
        if self.resume.is_empty():
            sections_to_process = self._create_basic_sections()

        # Process each section
        self.ui.show_progress("Improving resume sections", sections_to_process)

        for section_name in sections_to_process:
            self._process_section(section_name)

    def _create_basic_sections(self) -> list[str]:
        """Create basic resume sections from scratch."""
        basic_sections = ["summary", "experience", "education", "skills"]

        for section in basic_sections:
            # Ask user for content
            questions = self._get_section_questions(section)
            if questions:
                answers = self.ui.prompt_for_missing_info(section, questions)

                if answers:
                    # Create content from answers
                    content = self._create_content_from_answers(section, answers)
                    self.resume.update_section(section, content)

        return basic_sections

    def _process_section(self, section_name: str) -> None:
        """Process and improve a single resume section."""
        current_content = self.resume.get_section(section_name)

        if not current_content.strip():
            # Section is empty, try to get content from user
            questions = self._get_section_questions(section_name)
            if questions:
                answers = self.ui.prompt_for_missing_info(section_name, questions)
                if answers:
                    current_content = self._create_content_from_answers(section_name, answers)
                    self.resume.update_section(section_name, current_content)

        if current_content.strip():
            # Improve existing content
            improved_content = self.content_analyzer.improve_content_with_ai(
                current_content,
                section_name,
                {
                    "position": self.user_profile.target_position,
                    "experience": self.user_profile.years_of_experience,
                },
            )

            # Show changes to user and get confirmation
            if improved_content != current_content:
                if self.ui.confirm_changes(section_name, current_content, improved_content):
                    self.resume.update_section(section_name, improved_content, revised=True)
                    self.ui.display_success(f"Improved {section_name} section")

    def _get_section_questions(self, section_name: str) -> list[str]:
        """Get questions for gathering content for a specific section."""
        questions = {
            "summary": [
                "What are your key professional strengths?",
                "What makes you unique as a candidate?",
                "What are your main career achievements?",
            ],
            "experience": [
                "What is your most recent job title and company?",
                "What were your main responsibilities?",
                "What were your key achievements in this role?",
                "Can you provide specific metrics or numbers?",
            ],
            "education": [
                "What is your highest degree?",
                "From which institution did you graduate?",
                "When did you graduate?",
                "What was your major/field of study?",
            ],
            "skills": [
                "What are your technical skills?",
                "What software/tools do you use?",
                "What are your key professional competencies?",
                "Do you have any certifications?",
            ],
        }

        return questions.get(
            section_name,
            [
                f"Please provide content for your {section_name} section:",
            ],
        )

    def _create_content_from_answers(self, section_name: str, answers: dict[str, str]) -> str:
        """Create section content from user answers."""
        # Basic content creation - can be enhanced in future phases
        if section_name == "experience":
            # Format as bullet points
            content_parts = []
            for question, answer in answers.items():
                if "responsibilities" in question.lower():
                    bullets = [f"- {line.strip()}" for line in answer.split("\n") if line.strip()]
                    content_parts.extend(bullets)
                else:
                    content_parts.append(f"- {answer}")
            return "\n".join(content_parts)

        elif section_name == "skills":
            # Format as comma-separated list
            all_skills = []
            for answer in answers.values():
                skills = [skill.strip() for skill in answer.replace(",", "\n").split("\n")]
                all_skills.extend([s for s in skills if s])
            return ", ".join(set(all_skills))  # Remove duplicates

        else:
            # Default: combine all answers
            return " ".join(answers.values())

    def _export_resume(self) -> None:
        """Export the final resume."""
        export_options = self.ui.prompt_export_options()

        try:
            # Generate final resume content
            final_content = self.resume.export_markdown()

            # Write to file
            output_path = Path(export_options["path"])
            output_path.write_text(final_content, encoding="utf-8")

            self.ui.display_success(f"Resume exported to {output_path}")

        except Exception as e:
            self.ui.display_error(f"Could not export resume: {e}")


@click.command()
@click.version_option()
def main() -> None:
    """
    CVMaestro - Intelligent Resume Builder

    Transform your resume with AI-powered insights and professional guidance.
    """
    app = ResumeImprover()
    app.run()


if __name__ == "__main__":
    main()
