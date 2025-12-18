"""
Quick test to verify URL generation
"""
import json
from src.agents.similarity_agent import MatchSimilarityAgent
from src.models.pet_models import PetDescription, Location, SpeciesType, SizeType

# Create sample pet description
pet_desc = PetDescription(
    species=SpeciesType.DOG,
    size=SizeType.MEDIUM,
    colors=["white", "brown"],
    distinctive_features=["black spot on left ear"],
    breed="Mixed breed",
    approximate_age="adult",
    last_seen_location=Location(
        province="San José",
        canton="Escazú",
        district="San Antonio"
    )
)

# Create agent
agent = MatchSimilarityAgent(use_embeddings=False)

# Process and get results
result = agent.process(pet_desc)

print("\n" + "="*60)
print("URL GENERATION TEST")
print("="*60)

if result.candidates:
    print(f"\nFound {len(result.candidates)} matches:\n")
    for i, candidate in enumerate(result.candidates[:3], 1):
        print(f"{i}. Match ID: {candidate.match_id}")
        print(f"   Similarity: {candidate.similarity_score:.1%}")
        print(f"   View URL: {candidate.view_url}")
        print(f"   Distance: {candidate.location_distance_km}km")
        print()
    
    # Show top match
    if result.top_match:
        print(f"Top Match URL: {result.top_match.view_url}")
else:
    print("\nNo matches found")

print("="*60)
