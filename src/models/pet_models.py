"""
Pydantic models for pet data validation and structured outputs.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class SpeciesType(str, Enum):
    """Valid pet species."""
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


class SizeType(str, Enum):
    """Valid pet sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class Location(BaseModel):
    """Location information for Costa Rica."""
    province: str = Field(..., description="Province name in Costa Rica")
    canton: str = Field(..., description="Canton (county) name")
    district: str = Field(..., description="District name")
    additional_details: Optional[str] = Field(None, description="Additional location details (e.g., near a park)")

    @field_validator('province')
    @classmethod
    def validate_province(cls, v: str) -> str:
        """Validate that province is one of Costa Rica's provinces."""
        valid_provinces = [
            "San José", "Alajuela", "Cartago", "Heredia", 
            "Guanacaste", "Puntarenas", "Limón"
        ]
        if v not in valid_provinces:
            raise ValueError(f"Province must be one of: {', '.join(valid_provinces)}")
        return v

    @field_validator('canton', 'district')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Ensure canton and district are not empty."""
        if not v or not v.strip():
            raise ValueError("Canton and district cannot be empty")
        return v.strip()


class PetDescription(BaseModel):
    """Structured pet description extracted from images and text."""
    species: SpeciesType = Field(..., description="Type of animal")
    size: SizeType = Field(..., description="Size category of the pet")
    colors: List[str] = Field(..., min_length=1, description="Primary colors of the pet")
    distinctive_features: List[str] = Field(
        default_factory=list, 
        description="Notable features like scars, collars, spots, etc."
    )
    breed: Optional[str] = Field(None, description="Breed if identifiable")
    approximate_age: Optional[str] = Field(None, description="Estimated age (e.g., puppy, adult, senior)")
    last_seen_location: Location = Field(..., description="Location where pet was last seen")
    last_seen_date: Optional[str] = Field(None, description="Date when pet was last seen")
    
    @field_validator('colors')
    @classmethod
    def validate_colors(cls, v: List[str]) -> List[str]:
        """Ensure colors are not empty strings."""
        cleaned = [color.strip().lower() for color in v if color and color.strip()]
        if not cleaned:
            raise ValueError("At least one color must be provided")
        return cleaned

    @field_validator('distinctive_features')
    @classmethod
    def clean_features(cls, v: List[str]) -> List[str]:
        """Clean and normalize distinctive features."""
        return [feat.strip() for feat in v if feat and feat.strip()]


class UserInput(BaseModel):
    """Raw user input for reporting a lost pet or sighting."""
    images: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="File paths to pet images (max 5)"
    )
    description: str = Field(..., min_length=10, description="Free-text description of the pet")
    location: Location = Field(..., description="Location information")
    contact_info: Optional[str] = Field(None, description="Contact information (phone or email)")
    report_type: str = Field(default="lost", description="Type of report: 'lost' or 'sighting'")
    
    @field_validator('images')
    @classmethod
    def validate_image_paths(cls, v: List[str]) -> List[str]:
        """Validate image paths."""
        if len(v) > 5:
            raise ValueError("Maximum 5 images allowed")
        return v

    @field_validator('report_type')
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type."""
        if v not in ["lost", "sighting"]:
            raise ValueError("report_type must be 'lost' or 'sighting'")
        return v


class PetReport(BaseModel):
    """Complete pet report stored in the database."""
    report_id: str = Field(..., description="Unique identifier for the report")
    report_type: str = Field(..., description="Type: 'lost' or 'sighting'")
    pet_description: PetDescription = Field(..., description="Structured pet information")
    raw_description: str = Field(..., description="Original user description")
    image_paths: List[str] = Field(default_factory=list, description="Paths to uploaded images")
    contact_info: Optional[str] = Field(None, description="Contact information")
    report_date: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="When the report was created"
    )
    status: str = Field(default="active", description="Report status: active, resolved, expired")

    @field_validator('report_type')
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """Validate report type."""
        if v not in ["lost", "sighting"]:
            raise ValueError("report_type must be 'lost' or 'sighting'")
        return v


# Export all models
__all__ = [
    'SpeciesType',
    'SizeType',
    'Location',
    'PetDescription',
    'UserInput',
    'PetReport'
]
