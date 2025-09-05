"""Tests for resume parser."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cvmaestro.services.parser import ResumeParser


def test_parse_markdown_content():
    """Test parsing markdown content into sections."""
    parser = ResumeParser()

    content = """# John Doe

## Contact
Email: john@example.com

## Experience
Software Developer at Tech Co.
- Built web applications
- Worked with Python

## Skills
Python, JavaScript
"""

    sections = parser._parse_markdown_content(content)

    assert "contact" in sections
    assert "experience" in sections
    assert "skills" in sections
    assert "Email: john@example.com" in sections["contact"]
    assert "Python, JavaScript" in sections["skills"]


def test_normalize_section_names():
    """Test section name normalization."""
    parser = ResumeParser()

    assert parser._normalize_section_name("Work Experience") == "experience"
    assert parser._normalize_section_name("Technical Skills") == "skills"
    assert parser._normalize_section_name("Professional Summary") == "summary"
    assert parser._normalize_section_name("Education") == "education"


def test_extract_section_name():
    """Test section header extraction."""
    parser = ResumeParser()

    assert parser._extract_section_name("## Experience") == "experience"
    assert parser._extract_section_name("# Professional Summary") == "summary"
    assert parser._extract_section_name("### Skills") == "skills"
    assert parser._extract_section_name("Not a header") is None
