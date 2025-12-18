"""
Pydantic models for matching and similarity results.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for matches."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class MatchCandidate(BaseModel):
    """A potential match from the database."""
    match_id: str = Field(..., description="ID of the matched report")
    report_type: str = Field(..., description="Type of matched report: 'lost' or 'sighting'")
    similarity_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Similarity score between 0 and 1"
    )
    matching_reasons: List[str] = Field(
        default_factory=list,
        description="Human-readable reasons for the match"
    )
    location_distance_km: Optional[float] = Field(
        None, 
        ge=0.0,
        description="Approximate distance between locations in kilometers"
    )
    days_since_report: Optional[int] = Field(
        None,
        ge=0,
        description="Number of days since the report was created"
    )
    pet_name: Optional[str] = Field(None, description="Name of the pet if available")
    contact_available: bool = Field(default=False, description="Whether contact info is available")
    view_url: Optional[str] = Field(None, description="URL to view full report details")

    @field_validator('similarity_score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Ensure similarity score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity score must be between 0.0 and 1.0")
        return round(v, 3)


class MatchResult(BaseModel):
    """Results from the similarity search."""
    candidates: List[MatchCandidate] = Field(
        default_factory=list,
        description="List of potential matches"
    )
    top_match: Optional[MatchCandidate] = Field(
        None,
        description="The best match if any meet threshold"
    )
    confidence_level: ConfidenceLevel = Field(
        default=ConfidenceLevel.NONE,
        description="Overall confidence in matches"
    )
    total_candidates_found: int = Field(
        default=0,
        ge=0,
        description="Total number of candidates found"
    )
    search_timestamp: str = Field(
        ...,
        description="ISO timestamp of when search was performed"
    )

    @field_validator('top_match')
    @classmethod
    def validate_top_match(cls, v: Optional[MatchCandidate], info) -> Optional[MatchCandidate]:
        """Ensure top_match is consistent with candidates."""
        candidates = info.data.get('candidates', [])
        if v and v not in candidates:
            # Top match should be from candidates list
            return None
        return v


class FinalOutput(BaseModel):
    """Final output presented to the user."""
    enriched_profile: dict = Field(
        ...,
        description="Structured pet profile extracted by Agent 1"
    )
    matches: MatchResult = Field(
        ...,
        description="Match results from Agent 2"
    )
    explanation: str = Field(
        ...,
        min_length=20,
        description="Human-readable explanation of results"
    )
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next steps for the user"
    )
    confidence_summary: str = Field(
        ...,
        description="Summary of match confidence"
    )
    processing_metadata: dict = Field(
        default_factory=dict,
        description="Metadata about processing (timing, agent info, etc.)"
    )

    @field_validator('recommended_actions')
    @classmethod
    def validate_actions(cls, v: List[str]) -> List[str]:
        """Ensure recommended actions are not empty."""
        return [action.strip() for action in v if action and action.strip()]


# Export all models
__all__ = [
    'ConfidenceLevel',
    'MatchCandidate',
    'MatchResult',
    'FinalOutput'
]
