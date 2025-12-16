"""
Main orchestration pipeline for the AI Multi-Agent Lost Pet Intelligence System.
Coordinates all three agents in sequence to process pet reports.
"""

import os
import sys
import json
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.pet_models import UserInput, PetDescription
from src.models.match_models import FinalOutput
from src.agents.visual_extractor_agent import VisualTextExtractorAgent
from src.agents.similarity_agent import MatchSimilarityAgent
from src.agents.decision_agent import DecisionExplanationAgent


def load_config() -> Dict:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary with configuration settings
    """
    # Load .env file
    load_dotenv()
    
    config = {
        'openai_api_key': os.getenv('OPENAI_API_KEY'),
        'vision_model': os.getenv('OPENAI_VISION_MODEL', 'gpt-4o'),
        'text_model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
        'embedding_model': os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'),
        'similarity_threshold': float(os.getenv('SIMILARITY_THRESHOLD', '0.6')),
        'top_k_matches': int(os.getenv('TOP_K_MATCHES', '5')),
        'use_embeddings': os.getenv('USE_EMBEDDINGS', 'true').lower() == 'true'
    }
    
    # Validate required config
    if not config['openai_api_key']:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
    
    return config


def setup_agents(config: Dict) -> tuple:
    """
    Initialize all three agents with configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (agent1, agent2, agent3)
    """
    print("\n" + "="*60)
    print("INITIALIZING AI MULTI-AGENT SYSTEM")
    print("="*60)
    
    # Agent 1: Visual & Text Extractor
    print("\n[Setup] Initializing Agent 1: Visual & Text Extractor...")
    agent1 = VisualTextExtractorAgent(
        api_key=config['openai_api_key'],
        vision_model=config['vision_model'],
        text_model=config['text_model']
    )
    print("  ✓ Agent 1 ready")
    
    # Agent 2: Match & Similarity
    print("\n[Setup] Initializing Agent 2: Match & Similarity...")
    agent2 = MatchSimilarityAgent(
        api_key=config['openai_api_key'],
        use_embeddings=config['use_embeddings'],
        top_k=config['top_k_matches'],
        similarity_threshold=config['similarity_threshold']
    )
    print(f"  ✓ Agent 2 ready (embeddings: {config['use_embeddings']})")
    
    # Agent 3: Decision & Explanation
    print("\n[Setup] Initializing Agent 3: Decision & Explanation...")
    agent3 = DecisionExplanationAgent(
        api_key=config['openai_api_key'],
        model=config['text_model']
    )
    print("  ✓ Agent 3 ready")
    
    print("\n" + "="*60)
    print("ALL AGENTS INITIALIZED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return agent1, agent2, agent3


def process_pet_report(
    user_input: UserInput,
    agent1: VisualTextExtractorAgent,
    agent2: MatchSimilarityAgent,
    agent3: DecisionExplanationAgent
) -> FinalOutput:
    """
    Orchestrate the sequential agent pipeline.
    
    Args:
        user_input: Validated user input
        agent1: Visual & Text Extractor Agent
        agent2: Match & Similarity Agent
        agent3: Decision & Explanation Agent
        
    Returns:
        FinalOutput with complete results
        
    Raises:
        Exception: If any agent fails critically
    """
    start_time = datetime.now()
    
    print("\n" + "="*60)
    print("PROCESSING PET REPORT")
    print("="*60)
    print(f"Report Type: {user_input.report_type}")
    print(f"Location: {user_input.location.canton}, {user_input.location.province}")
    print(f"Images: {len(user_input.images)}")
    print("="*60)
    
    try:
        # AGENT 1: Extract structured data
        pet_description = agent1.process(user_input)
        
        # AGENT 2: Find matches
        match_result = agent2.process(pet_description)
        
        # AGENT 3: Generate explanation and recommendations
        final_output = agent3.process(pet_description, match_result)
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Add processing metadata
        final_output.processing_metadata.update({
            'processing_time_seconds': processing_time,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        })
        
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        print(f"Total Processing Time: {processing_time:.2f} seconds")
        print("="*60 + "\n")
        
        return final_output
        
    except Exception as e:
        print(f"\n❌ ERROR: Processing failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def display_results(final_output: FinalOutput):
    """
    Display results in a user-friendly format.
    
    Args:
        final_output: Complete output from the system
    """
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    
    # Pet Profile
    print("\n📋 ENRICHED PET PROFILE:")
    profile = final_output.enriched_profile
    print(f"  Species: {profile['species']}")
    print(f"  Size: {profile['size']}")
    print(f"  Colors: {', '.join(profile['colors'])}")
    if profile.get('distinctive_features'):
        print(f"  Features: {', '.join(profile['distinctive_features'])}")
    if profile.get('breed'):
        print(f"  Breed: {profile['breed']}")
    
    # Match Results
    print(f"\n🔍 MATCH RESULTS:")
    print(f"  {final_output.confidence_summary}")
    print(f"  Total candidates found: {final_output.matches.total_candidates_found}")
    print(f"  Matches above threshold: {len(final_output.matches.candidates)}")
    
    if final_output.matches.top_match:
        top = final_output.matches.top_match
        print(f"\n  🎯 TOP MATCH:")
        print(f"     ID: {top.match_id}")
        print(f"     Type: {top.report_type}")
        print(f"     Similarity: {top.similarity_score:.1%}")
        print(f"     Distance: {top.location_distance_km:.1f}km")
        print(f"     Days ago: {top.days_since_report}")
        print(f"     Reasons: {', '.join(top.matching_reasons[:3])}")
    
    # Explanation
    print(f"\n💬 EXPLANATION:")
    print(f"  {final_output.explanation}")
    
    # Recommendations
    print(f"\n✅ RECOMMENDED ACTIONS:")
    for i, action in enumerate(final_output.recommended_actions, 1):
        print(f"  {i}. {action}")
    
    # Metadata
    meta = final_output.processing_metadata
    if 'processing_time_seconds' in meta:
        print(f"\n⏱️  Processing time: {meta['processing_time_seconds']:.2f} seconds")
    
    print("\n" + "="*60 + "\n")


def save_results(final_output: FinalOutput, output_path: str):
    """
    Save results to JSON file.
    
    Args:
        final_output: Complete output
        output_path: Path to save JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_output.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"✓ Results saved to: {output_path}")
    except Exception as e:
        print(f"Warning: Failed to save results: {e}")


def main():
    """Main entry point for the application."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup agents
        agent1, agent2, agent3 = setup_agents(config)
        
        # Example: Process a test case
        # In production, this would come from an API or user interface
        print("Loading example test case...")
        
        # Example user input (you can modify this or load from examples)
        from src.models.pet_models import Location
        
        example_input = UserInput(
            images=[],  # Add image paths if testing with images
            description="""My dog Max is missing since yesterday. He's a medium-sized mixed breed with white and brown patches. 
            He has a very distinctive black spot on his left ear. He was wearing a red collar with a small bell. 
            Max is about 3 years old, very friendly, and responds to his name. Last seen near the park.""",
            location=Location(
                province="San José",
                canton="Escazú",
                district="San Antonio"
            ),
            contact_info="8888-1234",
            report_type="lost"
        )
        
        # Process the report
        final_output = process_pet_report(example_input, agent1, agent2, agent3)
        
        # Display results
        display_results(final_output)
        
        # Save results
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"results_{timestamp}.json")
        save_results(final_output, output_path)
        
        return final_output
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
