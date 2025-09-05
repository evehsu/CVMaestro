"""User profile data model for CVMaestro."""


from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    """
    User profile containing experience and target information.

    This model captures essential user information needed for
    resume customization and template selection.
    """

    years_of_experience: int = Field(
        ge=0, le=50, description="Total years of relevant work experience"
    )
    target_position: str = Field(
        min_length=1, max_length=100, description="Target job position or role"
    )
    target_level: str | None = Field(
        default=None, description="Target career level (junior, mid, senior, executive)"
    )
    industry: str | None = Field(default=None, description="Target industry or field")

    @field_validator("target_level")
    @classmethod
    def validate_target_level(cls, v: str | None) -> str | None:
        """Validate target level is from allowed values."""
        if v is None:
            return v

        allowed_levels = {"junior", "mid", "senior", "executive"}
        if v.lower() not in allowed_levels:
            raise ValueError(f"target_level must be one of: {', '.join(allowed_levels)}")
        return v.lower()

    def validate_profile(self) -> bool:
        """
        Validate profile completeness and consistency.

        Returns:
            True if profile is valid and complete
        """
        # Basic validation - has required fields
        if not self.target_position or self.years_of_experience < 0:
            return False

        # Consistency checks
        if self.target_level == "junior" and self.years_of_experience > 3:
            return False
        if self.target_level == "executive" and self.years_of_experience < 8:
            return False

        return True

    def get_experience_tier(self) -> str:
        """
        Categorize experience level for template selection.

        Returns:
            Experience tier: entry, mid, senior, or executive
        """
        if self.years_of_experience <= 2:
            return "entry"
        elif self.years_of_experience <= 7:
            return "mid"
        elif self.years_of_experience <= 15:
            return "senior"
        else:
            return "executive"

    def suggest_target_level(self) -> str:
        """
        Suggest appropriate target level based on experience.

        Returns:
            Suggested target level
        """
        tier = self.get_experience_tier()
        if tier == "entry":
            return "junior"
        elif tier == "mid":
            return "mid"
        elif tier == "senior":
            return "senior"
        else:
            return "executive"

    def is_career_change(self) -> bool:
        """
        Detect if user might be making a career change.

        Returns:
            True if profile suggests career transition
        """
        # This is a placeholder for Phase 1
        # In later phases, this could analyze target_position vs current experience
        return False
