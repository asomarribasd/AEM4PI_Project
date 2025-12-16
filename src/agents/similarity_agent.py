"""
Agent 2: Match & Similarity Agent
Searches for similar pets using embeddings and similarity scoring.
"""

import os
from typing import List, Tuple, Optional
from datetime import datetime
from src.models.pet_models import PetDescription, PetReport
from src.models.match_models import MatchCandidate, MatchResult, ConfidenceLevel
from src.utils.data_access import get_mock_database, MockDatabase
from src.utils.embedding_utils import create_pet_embedding, cosine_similarity


class MatchSimilarityAgent:
    """
    Agent responsible for finding similar pets using vector similarity search.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        use_embeddings: bool = True,
        top_k: int = 5,
        similarity_threshold: float = 0.6
    ):
        """
        Initialize the Match & Similarity Agent.
        
        Args:
            api_key: OpenAI API key for embeddings
            use_embeddings: Whether to use real embeddings (requires API) or mock similarity
            top_k: Maximum number of matches to return
            similarity_threshold: Minimum similarity score for matches
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.use_embeddings = use_embeddings and self.api_key is not None
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.db = get_mock_database()
    
    def generate_embedding(self, pet_data: PetDescription) -> Optional[List[float]]:
        """
        Generate vector embedding for pet description.
        
        Args:
            pet_data: Structured pet description
            
        Returns:
            Embedding vector or None if embeddings disabled
        """
        if not self.use_embeddings:
            return None
        
        try:
            embedding = create_pet_embedding(pet_data, api_key=self.api_key)
            return embedding
        except Exception as e:
            print(f"  Warning: Failed to create embedding: {e}")
            return None
    
    def search_with_embeddings(
        self, 
        query_embedding: List[float],
        report_type: Optional[str] = None
    ) -> List[Tuple[PetReport, float]]:
        """
        Search using actual vector embeddings (when available).
        
        Args:
            query_embedding: Query vector
            report_type: Filter by 'lost' or 'sighting'
            
        Returns:
            List of (report, similarity_score) tuples
        """
        # Get all reports
        reports = []
        if report_type is None or report_type == 'lost':
            reports.extend(self.db.get_all_lost_pets())
        if report_type is None or report_type == 'sighting':
            reports.extend(self.db.get_all_sightings())
        
        # Calculate similarity for each report
        scored_reports = []
        for report in reports:
            # Generate embedding for this report
            try:
                report_embedding = create_pet_embedding(
                    report.pet_description,
                    api_key=self.api_key
                )
                
                # Calculate cosine similarity
                similarity = cosine_similarity(query_embedding, report_embedding)
                
                # Convert from [-1, 1] to [0, 1] range
                normalized_similarity = (similarity + 1) / 2
                
                scored_reports.append((report, normalized_similarity))
                
            except Exception as e:
                print(f"  Warning: Failed to score {report.report_id}: {e}")
                continue
        
        # Sort by similarity (highest first)
        scored_reports.sort(key=lambda x: x[1], reverse=True)
        
        return scored_reports[:self.top_k]
    
    def search_with_mock(
        self,
        query_pet: PetDescription,
        report_type: Optional[str] = None
    ) -> List[Tuple[PetReport, float]]:
        """
        Search using mock similarity algorithm (no API calls).
        
        Args:
            query_pet: Pet description to search for
            report_type: Filter by 'lost' or 'sighting'
            
        Returns:
            List of (report, similarity_score) tuples
        """
        return self.db.search_similar_pets(query_pet, top_k=self.top_k, report_type=report_type)
    
    def calculate_matching_reasons(
        self,
        query_pet: PetDescription,
        candidate_pet: PetDescription
    ) -> List[str]:
        """
        Generate human-readable reasons why pets match.
        
        Args:
            query_pet: Query pet description
            candidate_pet: Candidate match description
            
        Returns:
            List of matching reasons
        """
        reasons = []
        
        # Species match
        if query_pet.species == candidate_pet.species:
            reasons.append(f"Same species ({query_pet.species})")
        
        # Size match
        if query_pet.size == candidate_pet.size:
            reasons.append(f"Same size ({query_pet.size})")
        
        # Color overlap
        query_colors = set(c.lower() for c in query_pet.colors)
        candidate_colors = set(c.lower() for c in candidate_pet.colors)
        common_colors = query_colors & candidate_colors
        if common_colors:
            reasons.append(f"Matching colors: {', '.join(common_colors)}")
        
        # Feature overlap
        if query_pet.distinctive_features and candidate_pet.distinctive_features:
            query_features = set(f.lower() for f in query_pet.distinctive_features)
            candidate_features = set(f.lower() for f in candidate_pet.distinctive_features)
            common_features = query_features & candidate_features
            if common_features:
                reasons.append(f"Similar features: {', '.join(common_features)}")
        
        # Breed match
        if query_pet.breed and candidate_pet.breed:
            if query_pet.breed.lower() in candidate_pet.breed.lower() or \
               candidate_pet.breed.lower() in query_pet.breed.lower():
                reasons.append(f"Similar breed ({query_pet.breed})")
        
        # Location proximity
        if query_pet.last_seen_location.province == candidate_pet.last_seen_location.province:
            if query_pet.last_seen_location.canton == candidate_pet.last_seen_location.canton:
                reasons.append(f"Same area ({query_pet.last_seen_location.canton})")
            else:
                reasons.append(f"Same province ({query_pet.last_seen_location.province})")
        
        return reasons if reasons else ["General similarity in description"]
    
    def create_match_candidate(
        self,
        report: PetReport,
        similarity_score: float,
        query_pet: PetDescription
    ) -> MatchCandidate:
        """
        Create a MatchCandidate from a report and similarity score.
        
        Args:
            report: Pet report from database
            similarity_score: Calculated similarity
            query_pet: Original query pet
            
        Returns:
            MatchCandidate object
        """
        # Calculate matching reasons
        reasons = self.calculate_matching_reasons(query_pet, report.pet_description)
        
        # Calculate location distance
        distance = self.db.calculate_location_distance(
            query_pet.last_seen_location,
            report.pet_description.last_seen_location
        )
        
        # Calculate days since report
        days_since = self.db.calculate_days_since(report.report_date)
        
        return MatchCandidate(
            match_id=report.report_id,
            report_type=report.report_type,
            similarity_score=similarity_score,
            matching_reasons=reasons,
            location_distance_km=distance,
            days_since_report=days_since,
            contact_available=bool(report.contact_info)
        )
    
    def determine_confidence(self, candidates: List[MatchCandidate]) -> ConfidenceLevel:
        """
        Determine overall confidence level based on match quality.
        
        Args:
            candidates: List of match candidates
            
        Returns:
            Confidence level
        """
        if not candidates:
            return ConfidenceLevel.NONE
        
        top_score = candidates[0].similarity_score
        
        if top_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif top_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def process(self, pet_description: PetDescription) -> MatchResult:
        """
        Main processing method - find similar pets and create match result.
        
        Args:
            pet_description: Structured pet description from Agent 1
            
        Returns:
            MatchResult with candidates and metadata
        """
        print("\n[Agent 2: Match & Similarity] Starting search...")
        
        # Generate embedding if using real embeddings
        query_embedding = None
        if self.use_embeddings:
            print("  - Generating embedding...")
            query_embedding = self.generate_embedding(pet_description)
            if query_embedding:
                print("  - Embedding generated successfully")
        
        # Search for matches
        if query_embedding is not None:
            print("  - Searching with embeddings...")
            scored_reports = self.search_with_embeddings(query_embedding)
        else:
            print("  - Searching with mock similarity...")
            scored_reports = self.search_with_mock(pet_description)
        
        print(f"  - Found {len(scored_reports)} potential matches")
        
        # Filter by threshold and create candidates
        candidates = []
        for report, score in scored_reports:
            if score >= self.similarity_threshold:
                candidate = self.create_match_candidate(report, score, pet_description)
                candidates.append(candidate)
        
        print(f"  - {len(candidates)} matches above threshold ({self.similarity_threshold})")
        
        # Determine top match
        top_match = candidates[0] if candidates else None
        
        # Determine confidence
        confidence = self.determine_confidence(candidates)
        
        # Create result
        result = MatchResult(
            candidates=candidates,
            top_match=top_match,
            confidence_level=confidence,
            total_candidates_found=len(scored_reports),
            search_timestamp=datetime.now().isoformat()
        )
        
        print(f"[Agent 2] ✓ Search complete!")
        print(f"  Confidence: {confidence.value}")
        if top_match:
            print(f"  Top match: {top_match.match_id} (score: {top_match.similarity_score:.3f})")
        
        return result


# Export
__all__ = ['MatchSimilarityAgent']
