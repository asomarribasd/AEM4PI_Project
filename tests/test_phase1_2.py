"""
Test script to validate Phase 1 & 2 implementation.
Tests Pydantic models, validation, and mock database functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.pet_models import Location, PetDescription, UserInput, PetReport
from src.models.match_models import MatchCandidate, MatchResult, ConfidenceLevel
from src.utils.data_access import get_mock_database, search_lost_pets, search_all_reports


def test_location_validation():
    """Test Location model validation."""
    print("\n" + "="*60)
    print("Testing Location Validation")
    print("="*60)
    
    # Valid location
    try:
        location = Location(
            province="San José",
            canton="Escazú",
            district="San Rafael"
        )
        print(f"✓ Valid location created: {location.province}, {location.canton}")
    except Exception as e:
        print(f"✗ Failed to create valid location: {e}")
    
    # Invalid province
    try:
        invalid_location = Location(
            province="Madrid",
            canton="Test",
            district="Test"
        )
        print("✗ Invalid province accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Invalid province rejected: {str(e)[:60]}...")
    
    # Empty canton
    try:
        invalid_location = Location(
            province="San José",
            canton="",
            district="Test"
        )
        print("✗ Empty canton accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Empty canton rejected: {str(e)}")


def test_pet_description():
    """Test PetDescription model."""
    print("\n" + "="*60)
    print("Testing PetDescription Model")
    print("="*60)
    
    try:
        pet = PetDescription(
            species="dog",
            size="medium",
            colors=["white", "brown"],
            distinctive_features=["black spot on ear", "red collar"],
            breed="Mixed breed",
            last_seen_location=Location(
                province="San José",
                canton="Escazú",
                district="San Rafael"
            )
        )
        print(f"✓ PetDescription created: {pet.species}, {pet.size}, colors: {pet.colors}")
        print(f"  Features: {pet.distinctive_features}")
    except Exception as e:
        print(f"✗ Failed to create PetDescription: {e}")
    
    # Test with no colors (should fail)
    try:
        invalid_pet = PetDescription(
            species="dog",
            size="medium",
            colors=[],
            last_seen_location=Location(
                province="San José",
                canton="Escazú",
                district="San Rafael"
            )
        )
        print("✗ Empty colors list accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Empty colors rejected: {str(e)}")


def test_user_input():
    """Test UserInput validation."""
    print("\n" + "="*60)
    print("Testing UserInput Validation")
    print("="*60)
    
    # Valid input
    try:
        user_input = UserInput(
            images=["path/to/image1.jpg", "path/to/image2.jpg"],
            description="My dog is missing. Medium sized, white and brown.",
            location=Location(
                province="San José",
                canton="Escazú",
                district="San Rafael"
            ),
            contact_info="8888-1234"
        )
        print(f"✓ UserInput created with {len(user_input.images)} images")
        print(f"  Description length: {len(user_input.description)} chars")
    except Exception as e:
        print(f"✗ Failed to create UserInput: {e}")
    
    # Too many images
    try:
        invalid_input = UserInput(
            images=["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg", "img6.jpg"],
            description="Test description with enough characters",
            location=Location(
                province="San José",
                canton="Escazú",
                district="San Rafael"
            )
        )
        print("✗ Too many images accepted (should have failed)")
    except ValueError as e:
        print(f"✓ Too many images rejected: {str(e)}")


def test_mock_database():
    """Test mock database functionality."""
    print("\n" + "="*60)
    print("Testing Mock Database")
    print("="*60)
    
    try:
        db = get_mock_database()
        
        # Load lost pets
        lost_pets = db.get_all_lost_pets()
        print(f"✓ Loaded {len(lost_pets)} lost pet reports")
        
        # Load sightings
        sightings = db.get_all_sightings()
        print(f"✓ Loaded {len(sightings)} sighting reports")
        
        # Display first lost pet
        if lost_pets:
            first_pet = lost_pets[0]
            print(f"\n  First report: {first_pet.report_id}")
            print(f"  Species: {first_pet.pet_description.species}")
            print(f"  Location: {first_pet.pet_description.last_seen_location.canton}")
        
    except Exception as e:
        print(f"✗ Failed to load mock database: {e}")
        import traceback
        traceback.print_exc()


def test_similarity_search():
    """Test similarity search functionality."""
    print("\n" + "="*60)
    print("Testing Similarity Search")
    print("="*60)
    
    try:
        # Create a query pet similar to LOST-001
        query_pet = PetDescription(
            species="dog",
            size="medium",
            colors=["white", "brown"],
            distinctive_features=["black spot on ear"],
            last_seen_location=Location(
                province="San José",
                canton="Escazú",
                district="San Antonio"
            )
        )
        
        # Search for similar pets
        results = search_lost_pets(query_pet, top_k=3)
        
        print(f"✓ Found {len(results)} matches")
        for i, (report, score) in enumerate(results, 1):
            print(f"\n  Match {i}: {report.report_id} (score: {score:.3f})")
            print(f"    Species: {report.pet_description.species}")
            print(f"    Colors: {report.pet_description.colors}")
            print(f"    Location: {report.pet_description.last_seen_location.canton}")
        
    except Exception as e:
        print(f"✗ Failed similarity search: {e}")
        import traceback
        traceback.print_exc()


def test_match_models():
    """Test match-related models."""
    print("\n" + "="*60)
    print("Testing Match Models")
    print("="*60)
    
    try:
        # Create a match candidate
        candidate = MatchCandidate(
            match_id="LOST-001",
            report_type="lost",
            similarity_score=0.85,
            matching_reasons=["same colors", "same area", "similar features"],
            location_distance_km=2.5,
            days_since_report=3
        )
        print(f"✓ MatchCandidate created: {candidate.match_id}")
        print(f"  Score: {candidate.similarity_score}")
        print(f"  Reasons: {len(candidate.matching_reasons)}")
        
        # Create match result
        match_result = MatchResult(
            candidates=[candidate],
            top_match=candidate,
            confidence_level=ConfidenceLevel.HIGH,
            total_candidates_found=1,
            search_timestamp="2025-12-16T10:00:00"
        )
        print(f"✓ MatchResult created with {len(match_result.candidates)} candidates")
        print(f"  Confidence: {match_result.confidence_level}")
        
    except Exception as e:
        print(f"✗ Failed to create match models: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PHASE 1 & 2 VALIDATION TESTS")
    print("="*60)
    
    test_location_validation()
    test_pet_description()
    test_user_input()
    test_match_models()
    test_mock_database()
    test_similarity_search()
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review any failures above")
    print("2. Verify mock database contains expected data")
    print("3. Ready to proceed to Phase 3 (Utilities)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
