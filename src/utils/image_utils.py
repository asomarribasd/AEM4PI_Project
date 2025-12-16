"""
Image processing utilities for handling pet images.
Functions for validation, resizing, encoding, and batch processing.
"""

import os
import base64
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from PIL import Image
import io


# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
MAX_IMAGE_SIZE_MB = 5
MAX_DIMENSION = 2048  # Max width or height for API efficiency


def validate_image_format(file_path: str) -> bool:
    """
    Validate that a file exists and is a valid image format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        # Check file extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            print(f"Unsupported format: {file_ext}. Supported: {SUPPORTED_FORMATS}")
            return False
        
        # Try to open with PIL to verify it's a valid image
        with Image.open(file_path) as img:
            img.verify()
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            print(f"File too large: {file_size_mb:.2f}MB (max: {MAX_IMAGE_SIZE_MB}MB)")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error validating image {file_path}: {e}")
        return False


def resize_image_for_api(image_path: str, max_size: Tuple[int, int] = (MAX_DIMENSION, MAX_DIMENSION)) -> bytes:
    """
    Resize large images to reduce API costs while maintaining quality.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum dimensions (width, height)
        
    Returns:
        Resized image as bytes
        
    Raises:
        ValueError: If image cannot be processed
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (handles PNG with transparency)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            return buffer.getvalue()
            
    except Exception as e:
        raise ValueError(f"Failed to resize image {image_path}: {e}")


def encode_image_to_base64(image_path: str, resize: bool = True) -> str:
    """
    Convert image to base64 string for API calls.
    
    Args:
        image_path: Path to the image file
        resize: Whether to resize before encoding
        
    Returns:
        Base64 encoded string
        
    Raises:
        ValueError: If image cannot be processed
    """
    try:
        if resize:
            image_bytes = resize_image_for_api(image_path)
        else:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        
        encoded = base64.b64encode(image_bytes).decode('utf-8')
        return encoded
        
    except Exception as e:
        raise ValueError(f"Failed to encode image {image_path}: {e}")


def get_image_info(image_path: str) -> Dict[str, any]:
    """
    Get information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                'path': image_path,
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'file_size_mb': os.path.getsize(image_path) / (1024 * 1024)
            }
    except Exception as e:
        return {
            'path': image_path,
            'error': str(e)
        }


def process_multiple_images(image_paths: List[str], validate: bool = True) -> List[Dict[str, any]]:
    """
    Batch process multiple pet images.
    
    Args:
        image_paths: List of image file paths
        validate: Whether to validate images before processing
        
    Returns:
        List of dictionaries with processed image data and metadata
    """
    results = []
    
    for image_path in image_paths:
        result = {
            'path': image_path,
            'valid': False,
            'base64': None,
            'info': None,
            'error': None
        }
        
        try:
            # Validate if requested
            if validate:
                if not validate_image_format(image_path):
                    result['error'] = 'Validation failed'
                    results.append(result)
                    continue
            
            # Get image info
            result['info'] = get_image_info(image_path)
            
            # Encode image
            result['base64'] = encode_image_to_base64(image_path, resize=True)
            result['valid'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        results.append(result)
    
    return results


def create_placeholder_image(text: str, size: Tuple[int, int] = (400, 400)) -> bytes:
    """
    Create a placeholder image for testing when real images aren't available.
    
    Args:
        text: Text to display on placeholder
        size: Image dimensions
        
    Returns:
        Image as bytes
    """
    try:
        from PIL import ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', size, color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text_position = (size[0] // 4, size[1] // 2)
        draw.text(text_position, text, fill='black')
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Failed to create placeholder: {e}")
        return b''


# Export main functions
__all__ = [
    'validate_image_format',
    'resize_image_for_api',
    'encode_image_to_base64',
    'get_image_info',
    'process_multiple_images',
    'create_placeholder_image'
]
