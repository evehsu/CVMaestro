"""Resume parsing service for various file formats."""

import re
from pathlib import Path


class ResumeParser:
    """
    Service for parsing resume files into structured sections.

    Phase 1 implementation focuses on markdown parsing.
    Future phases will extend to support PDF and Word formats.
    """

    # Common resume section patterns
    SECTION_PATTERNS = [
        # Standard sections
        r"^#+\s*(summary|profile|objective)",
        r"^#+\s*(experience|work\s+experience|employment)",
        r"^#+\s*(education|academic\s+background)",
        r"^#+\s*(skills|technical\s+skills|core\s+competencies)",
        r"^#+\s*(projects|notable\s+projects)",
        r"^#+\s*(certifications?|licenses?)",
        r"^#+\s*(awards?|achievements?|honors?)",
        r"^#+\s*(contact|contact\s+information)",
        r"^#+\s*(languages?)",
        r"^#+\s*(publications?)",
        r"^#+\s*(references?)",
        # Generic header pattern
        r"^#+\s*(.+)",
    ]

    def __init__(self) -> None:
        """Initialize the resume parser."""
        pass

    def parse_markdown_file(self, file_path: str) -> dict[str, str]:
        """
        Parse a markdown resume file into sections.

        Args:
            file_path: Path to the markdown file

        Returns:
            Dictionary with section names as keys and content as values

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not readable or empty
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Could not read file {file_path}: {e}") from e

        if not content.strip():
            raise ValueError("Resume file is empty")

        return self._parse_markdown_content(content)

    def _parse_markdown_content(self, content: str) -> dict[str, str]:
        """
        Parse markdown content into sections.

        Args:
            content: Raw markdown content

        Returns:
            Dictionary of sections
        """
        sections = {}
        lines = content.split("\n")
        current_section = None
        current_content = []

        # Handle case where resume starts without a header
        header_found = False

        for line in lines:
            # Check if this line is a section header
            section_name = self._extract_section_name(line)

            if section_name:
                # Save previous section if it exists
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = section_name
                current_content = []
                header_found = True

            else:
                # Add to current section content
                if header_found:
                    # We're in a section, add the line
                    current_content.append(line)
                else:
                    # No header found yet, treat as general content
                    if current_section is None:
                        current_section = "header"
                        current_content = []
                    current_content.append(line)

        # Save the last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        # Clean up empty sections
        sections = {k: v for k, v in sections.items() if v.strip()}

        return sections

    def _extract_section_name(self, line: str) -> str | None:
        """
        Extract section name from a line if it's a header.

        Args:
            line: Line to check

        Returns:
            Section name if line is a header, None otherwise
        """
        line = line.strip()

        # Check each pattern
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Get the captured group (section name)
                if match.groups():
                    section_name = match.group(1).strip()
                else:
                    # For patterns without groups, extract from the line
                    section_name = re.sub(r"^#+\s*", "", line).strip()

                # Normalize section name
                return self._normalize_section_name(section_name)

        return None

    def _normalize_section_name(self, name: str) -> str:
        """
        Normalize section names to standard format.

        Args:
            name: Raw section name

        Returns:
            Normalized section name
        """
        name = name.lower().strip()

        # Map variations to standard names
        mappings = {
            "summary": "summary",
            "profile": "summary",
            "objective": "summary",
            "professional summary": "summary",
            "experience": "experience",
            "work experience": "experience",
            "employment": "experience",
            "professional experience": "experience",
            "education": "education",
            "academic background": "education",
            "skills": "skills",
            "technical skills": "skills",
            "core competencies": "skills",
            "projects": "projects",
            "notable projects": "projects",
            "certifications": "certifications",
            "certification": "certifications",
            "licenses": "certifications",
            "license": "certifications",
            "awards": "awards",
            "award": "awards",
            "achievements": "awards",
            "achievement": "awards",
            "honors": "awards",
            "honor": "awards",
            "contact": "contact",
            "contact information": "contact",
            "languages": "languages",
            "language": "languages",
            "publications": "publications",
            "publication": "publications",
            "references": "references",
            "reference": "references",
        }

        # Return mapped name or original if no mapping
        return mappings.get(name, name)

    def validate_parsed_resume(self, sections: dict[str, str]) -> list[str]:
        """
        Validate parsed resume sections and identify issues.

        Args:
            sections: Parsed resume sections

        Returns:
            List of validation issues
        """
        issues = []

        # Check for essential sections
        essential_sections = ["experience", "education"]
        for section in essential_sections:
            if section not in sections:
                issues.append(f"Missing essential section: {section}")

        # Check for empty sections
        empty_sections = [name for name, content in sections.items() if not content.strip()]
        if empty_sections:
            issues.append(f"Empty sections found: {', '.join(empty_sections)}")

        # Check for very short sections
        short_sections = [
            name
            for name, content in sections.items()
            if len(content.split()) < 3 and name in ["experience", "summary"]
        ]
        if short_sections:
            issues.append(f"Sections may need more detail: {', '.join(short_sections)}")

        return issues
