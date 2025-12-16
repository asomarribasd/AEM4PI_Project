"""
Mock database access utilities to simulate vector store operations.
This module provides functions to load, search, and manage mock pet data
without requiring an actual vector database during development/testing.
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from src.models.pet_models import PetReport, PetDescription, Location


class MockDatabase:
    """Mock database that simulates vector store operations."""
    
    def __init__(self, data_path: str = "data/mock_database.json"):
        """Initialize mock database with data path."""
        self.data_path = data_path
        self._data = None
    
    def load_data(self) -> Dict:
        """Load mock data from JSON file."""
        if self._data is None:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Mock database file not found: {self.data_path}")
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        
        return self._data
    
    def get_all_lost_pets(self) -> List[PetReport]:
        """Get all lost pet reports."""
        data = self.load_data()
        reports = []
        
        for pet_data in data.get('lost_pets', []):
            try:
                report = PetReport(**pet_data)
                reports.append(report)
            except Exception as e:
                print(f"Error loading lost pet {pet_data.get('report_id')}: {e}")
        
        return reports
    
    def get_all_sightings(self) -> List[PetReport]:
        """Get all sighting reports."""
        data = self.load_data()
        reports = []
        
        for sight_data in data.get('sightings', []):
            try:
                report = PetReport(**sight_data)
                reports.append(report)
            except Exception as e:
                print(f"Error loading sighting {sight_data.get('report_id')}: {e}")
        
        return reports
    
    def get_report_by_id(self, report_id: str) -> Optional[PetReport]:
        """Get a specific report by ID."""
        all_reports = self.get_all_lost_pets() + self.get_all_sightings()
        
        for report in all_reports:
            if report.report_id == report_id:
                return report
        
        return None
    
    def search_similar_pets(
        self, 
        query_pet: PetDescription, 
        top_k: int = 5,
        report_type: Optional[str] = None
    ) -> List[Tuple[PetReport, float]]:
        """
        Search for similar pets using simple similarity scoring.
        Returns list of (PetReport, similarity_score) tuples.
        
        Args:
            query_pet: Pet description to search for
            top_k: Maximum number of results to return
            report_type: Filter by 'lost' or 'sighting', or None for both
        
        Returns:
            List of (report, score) tuples sorted by similarity
        """
        # Get all reports
        reports = []
        if report_type is None or report_type == 'lost':
            reports.extend(self.get_all_lost_pets())
        if report_type is None or report_type == 'sighting':
            reports.extend(self.get_all_sightings())
        
        # Calculate similarity scores
        scored_reports = []
        for report in reports:
            score = self._calculate_similarity(query_pet, report.pet_description)
            scored_reports.append((report, score))
        
        # Sort by score (highest first) and return top_k
        scored_reports.sort(key=lambda x: x[1], reverse=True)
        return scored_reports[:top_k]
    
    def _calculate_similarity(self, pet1: PetDescription, pet2: PetDescription) -> float:
        """
        Calculate simple similarity score between two pet descriptions.
        This is a basic algorithm that will be replaced by actual vector similarity.
        
        Scoring factors:
        - Species match: 0.3
        - Size match: 0.2
        - Color overlap: 0.2
        - Feature overlap: 0.2
        - Location proximity: 0.1
        """
        score = 0.0
        
        # Species match (30%)
        if pet1.species == pet2.species:
            score += 0.3
        
        # Size match (20%)
        if pet1.size == pet2.size:
            score += 0.2
        
        # Color overlap (20%)
        colors1 = set(c.lower() for c in pet1.colors)
        colors2 = set(c.lower() for c in pet2.colors)
        if colors1 and colors2:
            color_overlap = len(colors1 & colors2) / len(colors1 | colors2)
            score += 0.2 * color_overlap
        
        # Distinctive features overlap (20%)
        if pet1.distinctive_features and pet2.distinctive_features:
            features1 = set(f.lower() for f in pet1.distinctive_features)
            features2 = set(f.lower() for f in pet2.distinctive_features)
            if features1 and features2:
                feature_overlap = len(features1 & features2) / len(features1 | features2)
                score += 0.2 * feature_overlap
        
        # Location proximity (10%)
        if pet1.last_seen_location.province == pet2.last_seen_location.province:
            score += 0.05
            if pet1.last_seen_location.canton == pet2.last_seen_location.canton:
                score += 0.03
                if pet1.last_seen_location.district == pet2.last_seen_location.district:
                    score += 0.02
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_location_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Estimate distance between two locations (very simplified).
        In reality, you'd use actual geocoding or a distance API.
        
        Returns estimated distance in kilometers.
        """
        # Simple estimation based on location hierarchy
        if loc1.province != loc2.province:
            return 50.0  # Different provinces, assume far
        elif loc1.canton != loc2.canton:
            return 15.0  # Same province, different canton
        elif loc1.district != loc2.district:
            return 3.0   # Same canton, different district
        else:
            return 0.5   # Same district, assume nearby
    
    def calculate_days_since(self, date_str: str) -> int:
        """Calculate number of days since a given date."""
        try:
            report_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now()
            delta = now - report_date
            return delta.days
        except Exception:
            return 0


# Global instance
_mock_db = None


def get_mock_database() -> MockDatabase:
    """Get or create the global mock database instance."""
    global _mock_db
    if _mock_db is None:
        _mock_db = MockDatabase()
    return _mock_db


def search_lost_pets(query_pet: PetDescription, top_k: int = 5) -> List[Tuple[PetReport, float]]:
    """
    Search for similar lost pets.
    
    Args:
        query_pet: Pet description to search for
        top_k: Maximum number of results
    
    Returns:
        List of (PetReport, similarity_score) tuples
    """
    db = get_mock_database()
    return db.search_similar_pets(query_pet, top_k=top_k, report_type='lost')


def search_sightings(query_pet: PetDescription, top_k: int = 5) -> List[Tuple[PetReport, float]]:
    """
    Search for similar sighting reports.
    
    Args:
        query_pet: Pet description to search for
        top_k: Maximum number of results
    
    Returns:
        List of (PetReport, similarity_score) tuples
    """
    db = get_mock_database()
    return db.search_similar_pets(query_pet, top_k=top_k, report_type='sighting')


def search_all_reports(query_pet: PetDescription, top_k: int = 5) -> List[Tuple[PetReport, float]]:
    """
    Search both lost pets and sightings.
    
    Args:
        query_pet: Pet description to search for
        top_k: Maximum number of results
    
    Returns:
        List of (PetReport, similarity_score) tuples
    """
    db = get_mock_database()
    return db.search_similar_pets(query_pet, top_k=top_k, report_type=None)


# Export main functions
__all__ = [
    'MockDatabase',
    'get_mock_database',
    'search_lost_pets',
    'search_sightings',
    'search_all_reports'
]
