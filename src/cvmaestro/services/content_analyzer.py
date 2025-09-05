"""Content analysis service for resume quality assessment."""

import os
import re
from typing import Any

from openai import OpenAI


class ContentAnalyzer:
    """
    Service for analyzing resume content quality and generating improvements.

    This service provides the core AI-powered content analysis functionality
    for Phase 1, designed to be extended in future phases.
    """

    def __init__(self) -> None:
        """Initialize the content analyzer with OpenAI client."""
        # Initialize OpenAI client - API key should be set in environment
        self.client = None
        if os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI()

    def assess_quality(self, section_content: str, section_type: str = "general") -> float:
        """
        Assess the quality of resume section content.

        Args:
            section_content: Content to analyze
            section_type: Type of section (experience, education, skills, etc.)

        Returns:
            Quality score from 0.0 to 1.0
        """
        if not section_content.strip():
            return 0.0

        # Basic quality metrics (Phase 1 implementation)
        score = 0.0

        # Length check (not too short, not too long)
        word_count = len(section_content.split())
        if section_type in ["experience", "summary"]:
            if 20 <= word_count <= 200:
                score += 0.3
        else:
            if 5 <= word_count <= 100:
                score += 0.3

        # Action verbs check (for experience sections)
        if section_type == "experience":
            action_verbs = [
                "achieved",
                "managed",
                "led",
                "developed",
                "implemented",
                "created",
                "improved",
                "increased",
                "reduced",
                "optimized",
            ]
            found_verbs = sum(1 for verb in action_verbs if verb in section_content.lower())
            score += min(found_verbs / 3, 0.3)

        # Quantifiable results check
        numbers_pattern = r"\d+%|\d+\+|\$\d+|\d+[kmb]|\d+ years?"
        quantifiable_count = len(re.findall(numbers_pattern, section_content, re.IGNORECASE))
        if quantifiable_count > 0:
            score += 0.2

        # Professional language check (basic)
        unprofessional_words = ["stuff", "things", "lots", "really", "very", "awesome"]
        unprofessional_count = sum(
            1 for word in unprofessional_words if word in section_content.lower()
        )
        if unprofessional_count == 0:
            score += 0.2

        return min(score, 1.0)

    def suggest_improvements(self, content: str, section_type: str = "general") -> list[str]:
        """
        Generate improvement suggestions for content.

        Args:
            content: Content to analyze
            section_type: Type of section

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        if not content.strip():
            suggestions.append("Add content to this section")
            return suggestions

        # Basic rule-based suggestions (Phase 1)
        word_count = len(content.split())

        # Length suggestions
        if section_type in ["experience", "summary"] and word_count < 20:
            suggestions.append("Consider adding more detail and specific examples")
        elif word_count > 200:
            suggestions.append("Consider making the content more concise")

        # Action verbs suggestion (for experience)
        if section_type == "experience":
            action_verbs = ["achieved", "managed", "led", "developed", "implemented"]
            if not any(verb in content.lower() for verb in action_verbs):
                suggestions.append("Start bullet points with strong action verbs")

        # Quantification suggestion
        numbers_pattern = r"\d+%|\d+\+|\$\d+|\d+[kmb]|\d+ years?"
        if not re.search(numbers_pattern, content, re.IGNORECASE):
            suggestions.append("Add specific numbers, percentages, or metrics where possible")

        # Professional language check
        unprofessional_words = ["stuff", "things", "lots", "really", "very", "awesome"]
        found_unprofessional = [word for word in unprofessional_words if word in content.lower()]
        if found_unprofessional:
            suggestions.append(f"Replace informal words: {', '.join(found_unprofessional)}")

        return suggestions

    def improve_content_with_ai(
        self, content: str, section_type: str = "general", user_context: dict[str, Any] = None
    ) -> str:
        """
        Use AI to improve content quality.

        Args:
            content: Original content to improve
            section_type: Type of section
            user_context: Additional context about user (position, experience)

        Returns:
            Improved content
        """
        if not self.client:
            # Fallback to rule-based improvement if no OpenAI client
            return self._rule_based_improvement(content, section_type)

        try:
            # Construct prompt based on section type
            system_prompt = self._get_improvement_prompt(section_type, user_context)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Improve this content:\n\n{content}"},
                ],
                max_tokens=500,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"AI improvement failed: {e}")
            return self._rule_based_improvement(content, section_type)

    def _get_improvement_prompt(
        self, section_type: str, user_context: dict[str, Any] = None
    ) -> str:
        """Generate appropriate prompt for content improvement."""
        base_prompt = """You are a professional resume writer. Improve the provided content \
to be more professional, impactful, and ATS-friendly.

Guidelines:
- Use strong action verbs
- Include specific metrics where possible
- Keep language professional and concise
- Focus on achievements and results
- Maintain accuracy - don't add false information"""

        if section_type == "experience":
            return base_prompt + "\n- Format as bullet points starting with action verbs"
        elif section_type == "summary":
            return base_prompt + "\n- Create a compelling professional summary"
        elif section_type == "skills":
            return base_prompt + "\n- Organize skills by category and relevance"
        else:
            return base_prompt

    def _rule_based_improvement(self, content: str, section_type: str) -> str:
        """Fallback rule-based content improvement."""
        # Basic cleanup and formatting
        improved = content.strip()

        # Remove multiple spaces
        improved = re.sub(r"\s+", " ", improved)

        # Capitalize first letter of sentences
        improved = re.sub(
            r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), improved
        )

        return improved
