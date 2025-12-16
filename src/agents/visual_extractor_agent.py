"""
Agent 1: Visual & Text Extractor Agent
Processes multimodal inputs (images + text) to extract structured pet descriptions.
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from src.models.pet_models import PetDescription, Location, UserInput
from src.utils.image_utils import process_multiple_images, validate_image_format
import json


class VisualTextExtractorAgent:
    """
    Agent responsible for extracting structured pet information from images and text.
    Uses GPT-4 Vision for image analysis and text processing.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        vision_model: str = "gpt-4o",
        text_model: str = "gpt-4o"
    ):
        """
        Initialize the Visual & Text Extractor Agent.
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            vision_model: Model for image analysis
            text_model: Model for text processing
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.vision_model = vision_model
        self.text_model = text_model
    
    def analyze_images(self, image_paths: List[str]) -> Dict:
        """
        Analyze pet images using GPT-4 Vision to extract visual features.
        
        Args:
            image_paths: List of paths to pet images
            
        Returns:
            Dictionary with extracted visual features
        """
        if not image_paths:
            return {
                "species": None,
                "size": None,
                "colors": [],
                "distinctive_features": [],
                "breed": None,
                "approximate_age": None
            }
        
        try:
            # Process images (validate and encode)
            processed_images = process_multiple_images(image_paths, validate=True)
            
            # Filter valid images
            valid_images = [img for img in processed_images if img['valid']]
            
            if not valid_images:
                raise ValueError("No valid images found")
            
            # Build messages for vision API
            content = [{
                "type": "text",
                "text": """Analyze these pet images and extract the following information in JSON format:
{
  "species": "dog|cat|other",
  "size": "small|medium|large",
  "colors": ["color1", "color2"],
  "distinctive_features": ["feature1", "feature2"],
  "breed": "breed name or null if unknown",
  "approximate_age": "puppy|young adult|adult|senior or null if unknown"
}

Be specific about distinctive features like: collar color, ear shape, markings, scars, tail characteristics, eye color, etc.
Provide only the JSON, no additional text."""
            }]
            
            # Add images
            for img in valid_images[:3]:  # Limit to 3 images to control costs
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img['base64']}"
                    }
                })
            
            # Call vision API
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": content
                }],
                max_tokens=500,
                temperature=0.2
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            result = self._extract_json(result_text)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing images: {e}")
            return {
                "species": None,
                "size": None,
                "colors": [],
                "distinctive_features": [],
                "breed": None,
                "approximate_age": None
            }
    
    def analyze_text(self, description: str, location: Location) -> Dict:
        """
        Analyze user text description to extract pet information.
        
        Args:
            description: Free-text pet description
            location: Location information
            
        Returns:
            Dictionary with extracted text features
        """
        try:
            prompt = f"""Analyze this pet description and extract information in JSON format:

Description: "{description}"
Location: {location.district}, {location.canton}, {location.province}

Extract:
{{
  "species": "dog|cat|other",
  "size": "small|medium|large",
  "colors": ["color1", "color2"],
  "distinctive_features": ["feature1", "feature2"],
  "breed": "breed name or null",
  "approximate_age": "puppy|young adult|adult|senior or null",
  "additional_context": "any other relevant information"
}}

Be conservative - only extract information explicitly mentioned. Return only JSON."""
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "You are a precise information extractor. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            result = self._extract_json(result_text)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                "species": None,
                "size": None,
                "colors": [],
                "distinctive_features": [],
                "breed": None,
                "approximate_age": None
            }
    
    def merge_and_validate(
        self, 
        image_data: Dict, 
        text_data: Dict, 
        location: Location,
        last_seen_date: Optional[str] = None
    ) -> PetDescription:
        """
        Merge image and text analysis results into validated PetDescription.
        
        Args:
            image_data: Results from image analysis
            text_data: Results from text analysis
            location: Location information
            last_seen_date: Date pet was last seen
            
        Returns:
            Validated PetDescription model
        """
        # Merge data, preferring image data for visual features
        merged = {
            "species": image_data.get("species") or text_data.get("species") or "other",
            "size": image_data.get("size") or text_data.get("size") or "medium",
            "colors": self._merge_lists(image_data.get("colors", []), text_data.get("colors", [])),
            "distinctive_features": self._merge_lists(
                image_data.get("distinctive_features", []), 
                text_data.get("distinctive_features", [])
            ),
            "breed": image_data.get("breed") or text_data.get("breed"),
            "approximate_age": image_data.get("approximate_age") or text_data.get("approximate_age"),
            "last_seen_location": location,
            "last_seen_date": last_seen_date
        }
        
        # Ensure at least one color
        if not merged["colors"]:
            merged["colors"] = ["unknown"]
        
        # Create validated model
        try:
            pet_description = PetDescription(**merged)
            return pet_description
        except Exception as e:
            print(f"Validation error: {e}")
            # Retry with minimal valid data
            minimal = {
                "species": "other",
                "size": "medium",
                "colors": ["unknown"],
                "last_seen_location": location
            }
            return PetDescription(**minimal)
    
    def process(self, user_input: UserInput) -> PetDescription:
        """
        Main processing method - orchestrates the full extraction pipeline.
        
        Args:
            user_input: User's raw input data
            
        Returns:
            Structured and validated PetDescription
        """
        print("\n[Agent 1: Visual & Text Extractor] Starting extraction...")
        
        # Step 1: Analyze images
        print(f"  - Analyzing {len(user_input.images)} images...")
        image_data = self.analyze_images(user_input.images)
        print(f"  - Image analysis complete: {image_data.get('species')}, {image_data.get('size')}")
        
        # Step 2: Analyze text
        print(f"  - Analyzing text description...")
        text_data = self.analyze_text(user_input.description, user_input.location)
        print(f"  - Text analysis complete")
        
        # Step 3: Merge and validate
        print(f"  - Merging and validating data...")
        pet_description = self.merge_and_validate(
            image_data, 
            text_data, 
            user_input.location
        )
        
        print(f"[Agent 1] ✓ Extraction complete!")
        print(f"  Result: {pet_description.species} | {pet_description.size} | Colors: {pet_description.colors}")
        print(f"  Features: {pet_description.distinctive_features}")
        
        return pet_description
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from text that may contain markdown or other formatting."""
        try:
            # Try direct parsing first
            return json.loads(text)
        except:
            # Try to find JSON in markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find any JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError("No valid JSON found in response")
    
    def _merge_lists(self, list1: List[str], list2: List[str]) -> List[str]:
        """Merge two lists, removing duplicates while preserving order."""
        seen = set()
        result = []
        for item in list1 + list2:
            if item and item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
        return result


# Export
__all__ = ['VisualTextExtractorAgent']
