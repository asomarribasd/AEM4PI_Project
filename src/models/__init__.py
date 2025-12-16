"""
Package initialization for models.
"""

from .pet_models import (
    SpeciesType,
    SizeType,
    Location,
    PetDescription,
    UserInput,
    PetReport
)

from .match_models import (
    ConfidenceLevel,
    MatchCandidate,
    MatchResult,
    FinalOutput
)

__all__ = [
    # Pet models
    'SpeciesType',
    'SizeType',
    'Location',
    'PetDescription',
    'UserInput',
    'PetReport',
    # Match models
    'ConfidenceLevel',
    'MatchCandidate',
    'MatchResult',
    'FinalOutput'
]
