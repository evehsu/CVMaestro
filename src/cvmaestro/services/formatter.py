"""Resume formatting service for output generation."""



class MarkdownFormatter:
    """
    Service for formatting resume content into markdown output.

    This service handles the final formatting and structuring of resume content
    for export. Designed to be extended with multiple format support in future phases.
    """

    # Default section order for professional resumes
    DEFAULT_SECTION_ORDER = [
        "header",
        "contact",
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
        "awards",
        "languages",
        "publications",
        "references",
    ]

    def __init__(self) -> None:
        """Initialize the markdown formatter."""
        pass

    def format_resume(self, sections: dict[str, str], template: str = "default") -> str:
        """
        Format resume sections into a complete markdown document.

        Args:
            sections: Dictionary of section names to content
            template: Template identifier (for future template support)

        Returns:
            Complete formatted resume in markdown
        """
        if not sections:
            return "# Resume\n\n*No content available*"

        # Determine section order
        ordered_sections = self._get_section_order(sections, template)

        # Build formatted resume
        formatted_parts = []

        for section_name in ordered_sections:
            if section_name in sections:
                formatted_section = self._format_section(
                    section_name, sections[section_name], template
                )
                if formatted_section:
                    formatted_parts.append(formatted_section)

        # Join all sections with appropriate spacing
        return "\n\n".join(formatted_parts)

    def _get_section_order(self, sections: dict[str, str], template: str) -> list[str]:
        """
        Determine the order of sections for the given template.

        Args:
            sections: Available sections
            template: Template identifier

        Returns:
            Ordered list of section names
        """
        # For Phase 1, use default order
        # Future phases will support template-specific ordering

        # Start with default order, but only include sections that exist
        ordered = []

        # Add sections in default order if they exist
        for section in self.DEFAULT_SECTION_ORDER:
            if section in sections:
                ordered.append(section)

        # Add any remaining sections not in default order
        for section in sections:
            if section not in ordered:
                ordered.append(section)

        return ordered

    def _format_section(self, section_name: str, content: str, template: str) -> str:
        """
        Format an individual section based on its type.

        Args:
            section_name: Name of the section
            content: Section content
            template: Template identifier

        Returns:
            Formatted section markdown
        """
        if not content.strip():
            return ""

        # Handle special sections
        if section_name == "header":
            return self._format_header_section(content)
        elif section_name == "contact":
            return self._format_contact_section(content)
        elif section_name == "summary":
            return self._format_summary_section(content)
        elif section_name == "experience":
            return self._format_experience_section(content)
        elif section_name == "skills":
            return self._format_skills_section(content)
        else:
            return self._format_generic_section(section_name, content)

    def _format_header_section(self, content: str) -> str:
        """Format header/name section."""
        lines = content.strip().split("\n")
        if lines:
            # First non-empty line becomes the main header
            for line in lines:
                if line.strip():
                    return f"# {line.strip()}"
        return "# Resume"

    def _format_contact_section(self, content: str) -> str:
        """Format contact information section."""
        # Clean up and format contact info
        cleaned_content = content.strip()
        if not cleaned_content:
            return ""

        return f"## Contact\n\n{cleaned_content}"

    def _format_summary_section(self, content: str) -> str:
        """Format professional summary section."""
        cleaned_content = content.strip()
        if not cleaned_content:
            return ""

        return f"## Professional Summary\n\n{cleaned_content}"

    def _format_experience_section(self, content: str) -> str:
        """Format work experience section."""
        cleaned_content = content.strip()
        if not cleaned_content:
            return ""

        # Ensure bullet points are properly formatted
        lines = cleaned_content.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue

            # If line doesn't start with bullet point or header, add bullet
            if not line.startswith(("-", "*", "#", "**")) and not line.endswith(":"):
                # Check if it looks like a responsibility/achievement
                if line and not line.isupper():  # Not a title
                    line = f"- {line}"

            formatted_lines.append(line)

        formatted_content = "\n".join(formatted_lines)
        return f"## Experience\n\n{formatted_content}"

    def _format_skills_section(self, content: str) -> str:
        """Format skills section."""
        cleaned_content = content.strip()
        if not cleaned_content:
            return ""

        # Try to organize skills if they're just comma-separated
        if "," in cleaned_content and "\n" not in cleaned_content:
            skills = [skill.strip() for skill in cleaned_content.split(",")]
            skills = [skill for skill in skills if skill]  # Remove empty

            # Group skills into lines of reasonable length
            formatted_skills = []
            current_line = []
            current_length = 0

            for skill in skills:
                if current_length + len(skill) > 60 and current_line:
                    formatted_skills.append("- " + " • ".join(current_line))
                    current_line = [skill]
                    current_length = len(skill)
                else:
                    current_line.append(skill)
                    current_length += len(skill) + 3  # For " • "

            if current_line:
                formatted_skills.append("- " + " • ".join(current_line))

            formatted_content = "\n".join(formatted_skills)
        else:
            formatted_content = cleaned_content

        return f"## Skills\n\n{formatted_content}"

    def _format_generic_section(self, section_name: str, content: str) -> str:
        """Format a generic section."""
        cleaned_content = content.strip()
        if not cleaned_content:
            return ""

        # Capitalize section name for display
        display_name = section_name.replace("_", " ").title()

        return f"## {display_name}\n\n{cleaned_content}"

    def preview_section(self, section_name: str, content: str, template: str = "default") -> str:
        """
        Generate a preview of a single section.

        Args:
            section_name: Name of the section
            content: Section content
            template: Template identifier

        Returns:
            Formatted section preview
        """
        return self._format_section(section_name, content, template)

    def get_section_guidelines(self, section_name: str) -> list[str]:
        """
        Get formatting guidelines for a specific section.

        Args:
            section_name: Name of the section

        Returns:
            List of formatting guidelines
        """
        guidelines = {
            "summary": [
                "Keep to 3-4 sentences",
                "Focus on key achievements and skills",
                "Tailor to target position",
            ],
            "experience": [
                "Use bullet points for responsibilities",
                "Start with strong action verbs",
                "Include specific metrics and results",
                "List most recent experience first",
            ],
            "skills": [
                "Group by category (Technical, Management, etc.)",
                "List most relevant skills first",
                "Use consistent formatting",
            ],
            "education": [
                "Include degree, institution, and year",
                "Add GPA if above 3.5",
                "Include relevant coursework for recent graduates",
            ],
        }

        return guidelines.get(
            section_name,
            [
                "Use clear, professional language",
                "Keep content relevant to target role",
                "Maintain consistent formatting",
            ],
        )
