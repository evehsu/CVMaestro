"""Resume data model for CVMaestro."""

from pydantic import BaseModel, Field


class Resume(BaseModel):
    """
    Core resume model that manages raw and revised content by sections.

    This class forms the foundation for all resume processing operations,
    designed to be extended in future phases.
    """

    raw_content: dict[str, str] = Field(
        default_factory=dict, description="Original content organized by section names"
    )
    revised_content: dict[str, str] = Field(
        default_factory=dict, description="AI-improved content organized by section names"
    )
    template: str = Field(default="default", description="Template identifier for formatting")

    def parse_resume(self, file_path: str) -> None:
        """
        Parse resume file and populate raw_content by sections.

        Args:
            file_path: Path to the resume file (markdown format for Phase 1)
        """
        from ..services.parser import ResumeParser

        parser = ResumeParser()
        self.raw_content = parser.parse_markdown_file(file_path)

    def get_section(self, section_name: str) -> str:
        """
        Get content for a specific resume section.

        Args:
            section_name: Name of the section to retrieve

        Returns:
            Section content, empty string if section doesn't exist
        """
        return self.raw_content.get(section_name, "")

    def update_section(self, section_name: str, content: str, revised: bool = False) -> None:
        """
        Update content for a specific section.

        Args:
            section_name: Name of the section to update
            content: New content for the section
            revised: If True, updates revised_content; otherwise updates raw_content
        """
        if revised:
            self.revised_content[section_name] = content
        else:
            self.raw_content[section_name] = content

    def get_all_sections(self) -> list[str]:
        """
        Get list of all sections in the resume.

        Returns:
            List of section names
        """
        return list(self.raw_content.keys())

    def has_revised_content(self, section_name: str) -> bool:
        """
        Check if a section has revised content.

        Args:
            section_name: Name of the section to check

        Returns:
            True if section has revised content
        """
        return section_name in self.revised_content

    def export_markdown(self) -> str:
        """
        Generate final markdown resume using revised content where available.

        Returns:
            Complete resume in markdown format
        """
        from ..services.formatter import MarkdownFormatter

        formatter = MarkdownFormatter()

        # Use revised content where available, fall back to raw content
        final_content = {}
        for section in self.raw_content.keys():
            if section in self.revised_content:
                final_content[section] = self.revised_content[section]
            else:
                final_content[section] = self.raw_content[section]

        return formatter.format_resume(final_content, self.template)

    def is_empty(self) -> bool:
        """
        Check if the resume has any content.

        Returns:
            True if resume has no content
        """
        return len(self.raw_content) == 0
