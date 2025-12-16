"""
Agent 3: Decision & Explanation Agent
Interprets match results and generates user-friendly explanations and recommendations.
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from src.models.pet_models import PetDescription
from src.models.match_models import MatchResult, MatchCandidate, ConfidenceLevel, FinalOutput


class DecisionExplanationAgent:
    """
    Agent responsible for interpreting similarity results and generating
    human-friendly explanations and actionable recommendations.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
    ):
        """
        Initialize the Decision & Explanation Agent.
        
        Args:
            api_key: OpenAI API key
            model: Model for generating explanations
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def should_notify_user(self, match: MatchCandidate) -> bool:
        """
        Determine if a match is significant enough to notify the user.
        
        Args:
            match: Match candidate
            
        Returns:
            True if user should be notified
        """
        # High similarity matches
        if match.similarity_score >= 0.75:
            return True
        
        # Medium similarity with same area
        if match.similarity_score >= 0.6 and match.location_distance_km and match.location_distance_km < 5:
            return True
        
        # Recent sightings with decent similarity
        if match.report_type == "sighting" and match.days_since_report <= 7 and match.similarity_score >= 0.65:
            return True
        
        return False
    
    def generate_explanation(
        self,
        pet_profile: PetDescription,
        match_result: MatchResult
    ) -> str:
        """
        Generate a natural language explanation of the match results.
        
        Args:
            pet_profile: Original pet description
            match_result: Match results from Agent 2
            
        Returns:
            Human-readable explanation
        """
        try:
            # Build context for LLM
            profile_text = self._format_pet_profile(pet_profile)
            matches_text = self._format_matches(match_result)
            
            prompt = f"""You are helping someone find their lost pet. Analyze these results and provide a clear, empathetic explanation.

PET PROFILE:
{profile_text}

MATCH RESULTS:
Confidence Level: {match_result.confidence_level.value}
Total Candidates Found: {match_result.total_candidates_found}
Matches Above Threshold: {len(match_result.candidates)}

{matches_text}

Write a 2-3 sentence explanation that:
1. Summarizes the search results
2. Highlights the most promising match (if any)
3. Is empathetic and encouraging
4. Is specific about matching details

Be concise but warm. Don't use phrases like "I found" - speak directly about the results."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in lost pet recovery."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.7
            )
            
            explanation = response.choices[0].message.content.strip()
            return explanation
            
        except Exception as e:
            print(f"  Warning: Failed to generate AI explanation: {e}")
            return self._generate_fallback_explanation(pet_profile, match_result)
    
    def generate_recommendations(
        self,
        match_result: MatchResult,
        pet_profile: PetDescription
    ) -> List[str]:
        """
        Generate actionable next steps for the user.
        
        Args:
            match_result: Match results
            pet_profile: Pet description
            
        Returns:
            List of recommended actions
        """
        recommendations = []
        
        if not match_result.candidates:
            # No matches found
            recommendations.extend([
                "Continue monitoring for new sightings in your area",
                "Post on local social media groups and pet recovery pages",
                "Visit nearby shelters and veterinary clinics",
                "Put up physical flyers in the neighborhood",
                "Check back regularly as new reports are added daily"
            ])
        elif match_result.confidence_level == ConfidenceLevel.HIGH:
            # High confidence match
            top_match = match_result.top_match
            recommendations.extend([
                f"Contact the reporter of {top_match.match_id} immediately - this is a strong match",
                "Bring photos of your pet when meeting to verify identity",
                "Ask specific questions about distinctive features to confirm",
                "Be prepared to provide proof of ownership if the pet is found"
            ])
            
            if top_match.report_type == "sighting":
                recommendations.append(f"Visit the sighting location ({pet_profile.last_seen_location.canton}) as soon as possible")
        
        elif match_result.confidence_level == ConfidenceLevel.MEDIUM:
            # Medium confidence
            recommendations.extend([
                "Review the potential matches carefully and contact reporters for more details",
                "Ask for additional photos or descriptions to verify",
                "Continue active searching in the reported areas",
                "Post your pet's information on local lost pet groups"
            ])
            
            # Location-specific advice
            if match_result.top_match and match_result.top_match.location_distance_km:
                dist = match_result.top_match.location_distance_km
                if dist < 5:
                    recommendations.append(f"Focus search efforts within {dist:.1f}km of last known location")
        
        else:
            # Low confidence
            recommendations.extend([
                "The matches found have low similarity - continue searching",
                "Expand your search radius to nearby areas",
                "Post detailed descriptions and clear photos on multiple platforms",
                "Contact local animal control and shelters with your pet's description",
                "Consider offering a reward to increase community engagement"
            ])
        
        # General recommendations
        if pet_profile.distinctive_features:
            recommendations.append(f"When posting, emphasize distinctive features: {', '.join(pet_profile.distinctive_features[:3])}")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def create_confidence_summary(self, match_result: MatchResult) -> str:
        """
        Create a brief summary of match confidence.
        
        Args:
            match_result: Match results
            
        Returns:
            Confidence summary text
        """
        confidence = match_result.confidence_level
        
        if confidence == ConfidenceLevel.HIGH:
            return "High confidence match found! This could be your pet."
        elif confidence == ConfidenceLevel.MEDIUM:
            return "Moderate confidence matches found. Worth investigating further."
        elif confidence == ConfidenceLevel.LOW:
            return "Low confidence matches. Continue searching and monitoring."
        else:
            return "No strong matches found yet. Keep searching and check back regularly."
    
    def process(
        self,
        pet_profile: PetDescription,
        match_result: MatchResult
    ) -> FinalOutput:
        """
        Main processing method - generate complete output for user.
        
        Args:
            pet_profile: Original pet description from Agent 1
            match_result: Match results from Agent 2
            
        Returns:
            FinalOutput with explanation and recommendations
        """
        print("\n[Agent 3: Decision & Explanation] Generating output...")
        
        # Generate explanation
        print("  - Generating explanation...")
        explanation = self.generate_explanation(pet_profile, match_result)
        
        # Generate recommendations
        print("  - Generating recommendations...")
        recommendations = self.generate_recommendations(match_result, pet_profile)
        
        # Create confidence summary
        confidence_summary = self.create_confidence_summary(match_result)
        
        # Create final output
        final_output = FinalOutput(
            enriched_profile=pet_profile.model_dump(),
            matches=match_result,
            explanation=explanation,
            recommended_actions=recommendations,
            confidence_summary=confidence_summary,
            processing_metadata={
                "agent_1": "Visual & Text Extractor",
                "agent_2": "Match & Similarity",
                "agent_3": "Decision & Explanation",
                "total_matches_found": match_result.total_candidates_found,
                "matches_above_threshold": len(match_result.candidates)
            }
        )
        
        print(f"[Agent 3] ✓ Output generation complete!")
        print(f"  Confidence: {confidence_summary}")
        print(f"  Recommendations: {len(recommendations)}")
        
        return final_output
    
    def _format_pet_profile(self, pet: PetDescription) -> str:
        """Format pet profile for LLM prompt."""
        features = ", ".join(pet.distinctive_features) if pet.distinctive_features else "none specified"
        return f"""Species: {pet.species}
Size: {pet.size}
Colors: {", ".join(pet.colors)}
Distinctive Features: {features}
Breed: {pet.breed or "unknown"}
Location: {pet.last_seen_location.canton}, {pet.last_seen_location.province}"""
    
    def _format_matches(self, result: MatchResult) -> str:
        """Format match results for LLM prompt."""
        if not result.candidates:
            return "No matches found above similarity threshold."
        
        text = []
        for i, match in enumerate(result.candidates[:3], 1):  # Top 3
            reasons = "; ".join(match.matching_reasons[:4])
            text.append(f"""Match {i} ({match.match_id}):
  - Type: {match.report_type}
  - Similarity: {match.similarity_score:.2%}
  - Distance: {match.location_distance_km:.1f}km
  - Days ago: {match.days_since_report}
  - Reasons: {reasons}""")
        
        return "\n\n".join(text)
    
    def _generate_fallback_explanation(
        self,
        pet_profile: PetDescription,
        match_result: MatchResult
    ) -> str:
        """Generate a simple explanation without AI when API fails."""
        if not match_result.candidates:
            return f"No matches found yet for this {pet_profile.size} {pet_profile.species}. We'll keep searching and notify you of new reports in {pet_profile.last_seen_location.canton}."
        
        top = match_result.top_match
        confidence_text = {
            ConfidenceLevel.HIGH: "strong",
            ConfidenceLevel.MEDIUM: "moderate",
            ConfidenceLevel.LOW: "weak"
        }.get(match_result.confidence_level, "")
        
        return f"Found {len(match_result.candidates)} potential matches with {confidence_text} similarity. The top match ({top.match_id}) has a {top.similarity_score:.0%} similarity score and is located {top.location_distance_km:.1f}km away. Review the details and contact the reporter if it looks promising."


# Export
__all__ = ['DecisionExplanationAgent']
