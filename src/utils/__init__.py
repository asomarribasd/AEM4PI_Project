"""
Package initialization for utilities.
"""

from .data_access import (
    MockDatabase,
    get_mock_database,
    search_lost_pets,
    search_sightings,
    search_all_reports
)

from .image_utils import (
    validate_image_format,
    resize_image_for_api,
    encode_image_to_base64,
    get_image_info,
    process_multiple_images,
    create_placeholder_image
)

from .embedding_utils import (
    create_pet_embedding_text,
    create_pet_embedding,
    create_text_embedding,
    cosine_similarity,
    batch_create_embeddings,
    initialize_vector_store,
    add_to_vector_store,
    search_vector_store
)

__all__ = [
    # Data access
    'MockDatabase',
    'get_mock_database',
    'search_lost_pets',
    'search_sightings',
    'search_all_reports',
    # Image utilities
    'validate_image_format',
    'resize_image_for_api',
    'encode_image_to_base64',
    'get_image_info',
    'process_multiple_images',
    'create_placeholder_image',
    # Embedding utilities
    'create_pet_embedding_text',
    'create_pet_embedding',
    'create_text_embedding',
    'cosine_similarity',
    'batch_create_embeddings',
    'initialize_vector_store',
    'add_to_vector_store',
    'search_vector_store'
]
