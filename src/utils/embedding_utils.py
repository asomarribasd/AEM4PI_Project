"""
Embedding and vector store utilities.
Functions for creating embeddings and managing vector database operations.
"""

import os
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from src.models.pet_models import PetDescription


def create_pet_embedding_text(pet_data: PetDescription) -> str:
    """
    Convert structured pet data to text for embedding.
    
    Args:
        pet_data: Structured pet description
        
    Returns:
        Text representation optimized for embedding
    """
    parts = []
    
    # Species and size
    parts.append(f"{pet_data.size} {pet_data.species}")
    
    # Breed if available
    if pet_data.breed:
        parts.append(f"breed: {pet_data.breed}")
    
    # Colors
    colors_text = ", ".join(pet_data.colors)
    parts.append(f"colors: {colors_text}")
    
    # Distinctive features
    if pet_data.distinctive_features:
        features_text = ", ".join(pet_data.distinctive_features)
        parts.append(f"features: {features_text}")
    
    # Age
    if pet_data.approximate_age:
        parts.append(f"age: {pet_data.approximate_age}")
    
    # Location
    location = pet_data.last_seen_location
    parts.append(f"location: {location.district}, {location.canton}, {location.province}")
    
    if location.additional_details:
        parts.append(f"details: {location.additional_details}")
    
    return " | ".join(parts)


def create_pet_embedding(
    pet_data: PetDescription, 
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-small"
) -> List[float]:
    """
    Generate vector embedding from structured pet data.
    
    Args:
        pet_data: Structured pet description
        api_key: OpenAI API key (uses env var if not provided)
        model: Embedding model to use
        
    Returns:
        Vector embedding as list of floats
        
    Raises:
        ValueError: If API key is missing or API call fails
    """
    try:
        # Get API key
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Create OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Convert pet data to text
        text = create_pet_embedding_text(pet_data)
        
        # Create embedding
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        embedding = response.data[0].embedding
        return embedding
        
    except Exception as e:
        raise ValueError(f"Failed to create embedding: {e}")


def create_text_embedding(
    text: str,
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-small"
) -> List[float]:
    """
    Generate vector embedding from raw text.
    
    Args:
        text: Text to embed
        api_key: OpenAI API key (uses env var if not provided)
        model: Embedding model to use
        
    Returns:
        Vector embedding as list of floats
    """
    try:
        # Get API key
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        # Create OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create embedding
        response = client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding
        
    except Exception as e:
        raise ValueError(f"Failed to create text embedding: {e}")


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between -1 and 1 (higher is more similar)
    """
    import math
    
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity


def batch_create_embeddings(
    texts: List[str],
    api_key: Optional[str] = None,
    model: str = "text-embedding-3-small"
) -> List[List[float]]:
    """
    Create embeddings for multiple texts in batch (more efficient).
    
    Args:
        texts: List of texts to embed
        api_key: OpenAI API key
        model: Embedding model to use
        
    Returns:
        List of embeddings
    """
    try:
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        client = OpenAI(api_key=api_key)
        
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        
        embeddings = [data.embedding for data in response.data]
        return embeddings
        
    except Exception as e:
        raise ValueError(f"Failed to create batch embeddings: {e}")


# ChromaDB integration (will be used when we move from mock database)
def initialize_vector_store(collection_name: str = "pet_reports", persist_directory: str = "./data/vector_store"):
    """
    Initialize ChromaDB vector store.
    
    Args:
        collection_name: Name for the collection
        persist_directory: Directory to persist data
        
    Returns:
        ChromaDB collection object
    """
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Create client
        client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Lost pets and sightings"}
        )
        
        return collection
        
    except ImportError:
        print("ChromaDB not installed. Install with: pip install chromadb")
        return None
    except Exception as e:
        print(f"Failed to initialize vector store: {e}")
        return None


def add_to_vector_store(
    collection,
    pet_id: str,
    embedding: List[float],
    metadata: Dict
):
    """
    Add a pet report to the vector store.
    
    Args:
        collection: ChromaDB collection
        pet_id: Unique identifier
        embedding: Vector embedding
        metadata: Additional data (species, colors, location, etc.)
    """
    try:
        collection.add(
            ids=[pet_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    except Exception as e:
        print(f"Failed to add to vector store: {e}")


def search_vector_store(
    collection,
    query_embedding: List[float],
    top_k: int = 5,
    filter_metadata: Optional[Dict] = None
) -> List[Dict]:
    """
    Search vector store for similar pets.
    
    Args:
        collection: ChromaDB collection
        query_embedding: Query vector
        top_k: Number of results to return
        filter_metadata: Optional metadata filters
        
    Returns:
        List of results with IDs, distances, and metadata
    """
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i]
            })
        
        return formatted
        
    except Exception as e:
        print(f"Failed to search vector store: {e}")
        return []


# Export main functions
__all__ = [
    'create_pet_embedding_text',
    'create_pet_embedding',
    'create_text_embedding',
    'cosine_similarity',
    'batch_create_embeddings',
    'initialize_vector_store',
    'add_to_vector_store',
    'search_vector_store'
]
