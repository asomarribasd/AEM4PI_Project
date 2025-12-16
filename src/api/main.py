"""
FastAPI REST API for AI Multi-Agent Lost Pet Intelligence System
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.pet_models import UserInput, Location
from src.main import load_config, setup_agents, process_pet_report

# Initialize FastAPI app
app = FastAPI(
    title="Lost Pet Intelligence API",
    description="AI-powered multi-agent system for matching lost pets and sightings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agents (initialized once)
agents = None
config = None


@app.on_event("startup")
async def startup_event():
    """Initialize agents when API starts"""
    global agents, config
    print("🚀 Starting Lost Pet Intelligence API...")
    config = load_config()
    agent1, agent2, agent3 = setup_agents(config)
    agents = (agent1, agent2, agent3)
    print("✅ All agents initialized successfully!")


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Lost Pet Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "lost_report": "/api/v1/report/lost",
            "sighting_report": "/api/v1/report/sighting",
            "search": "/api/v1/search",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents_initialized": agents is not None,
        "config_loaded": config is not None
    }


@app.post("/api/v1/report/lost")
async def report_lost_pet(
    province: str = Form(..., description="Province in Costa Rica"),
    canton: str = Form(..., description="Canton"),
    district: str = Form(..., description="District"),
    description: str = Form(..., min_length=10, description="Pet description (min 10 characters)"),
    additional_details: Optional[str] = Form(None, description="Additional location details"),
    images: List[UploadFile] = File(default=[], description="Pet images (max 5)")
):
    """
    Report a lost pet
    
    - **province**: One of the 7 Costa Rica provinces
    - **canton**: Canton name
    - **district**: District name
    - **description**: Detailed description of the lost pet
    - **additional_details**: Optional additional location info
    - **images**: Optional images (JPEG, PNG, GIF, BMP, WebP, max 5MB each)
    """
    try:
        # Validate number of images
        if len(images) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 images allowed"
            )
        
        # Process uploaded images
        image_paths = []
        temp_dir = tempfile.mkdtemp()
        
        for idx, image in enumerate(images):
            if image.filename:
                # Validate file size (5MB max)
                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image {image.filename} exceeds 5MB limit"
                    )
                
                # Save temporarily
                temp_path = Path(temp_dir) / f"upload_{idx}_{image.filename}"
                with open(temp_path, 'wb') as f:
                    f.write(contents)
                image_paths.append(str(temp_path))
        
        # Create Location object
        location = Location(
            province=province,
            canton=canton,
            district=district,
            additional_details=additional_details
        )
        
        # Create UserInput object
        user_input = UserInput(
            report_type="lost",
            location=location,
            description=description,
            images=image_paths
        )
        
        # Process through agents
        if agents is None:
            raise HTTPException(status_code=503, detail="Agents not initialized")
        
        result = process_pet_report(user_input, *agents)
        
        # Clean up temp files
        for path in image_paths:
            try:
                os.remove(path)
            except:
                pass
        
        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "result": result.dict() if hasattr(result, 'dict') else result.model_dump()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/report/sighting")
async def report_sighting(
    province: str = Form(..., description="Province in Costa Rica"),
    canton: str = Form(..., description="Canton"),
    district: str = Form(..., description="District"),
    description: str = Form(..., min_length=10, description="Sighting description (min 10 characters)"),
    additional_details: Optional[str] = Form(None, description="Additional location details"),
    images: List[UploadFile] = File(default=[], description="Sighting images (max 5)")
):
    """
    Report a pet sighting
    
    - **province**: One of the 7 Costa Rica provinces
    - **canton**: Canton name
    - **district**: District name
    - **description**: Detailed description of the sighting
    - **additional_details**: Optional additional location info
    - **images**: Optional images (JPEG, PNG, GIF, BMP, WebP, max 5MB each)
    """
    try:
        # Validate number of images
        if len(images) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 images allowed"
            )
        
        # Process uploaded images
        image_paths = []
        temp_dir = tempfile.mkdtemp()
        
        for idx, image in enumerate(images):
            if image.filename:
                # Validate file size (5MB max)
                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Image {image.filename} exceeds 5MB limit"
                    )
                
                # Save temporarily
                temp_path = Path(temp_dir) / f"upload_{idx}_{image.filename}"
                with open(temp_path, 'wb') as f:
                    f.write(contents)
                image_paths.append(str(temp_path))
        
        # Create Location object
        location = Location(
            province=province,
            canton=canton,
            district=district,
            additional_details=additional_details
        )
        
        # Create UserInput object
        user_input = UserInput(
            report_type="sighting",
            location=location,
            description=description,
            images=image_paths
        )
        
        # Process through agents
        if agents is None:
            raise HTTPException(status_code=503, detail="Agents not initialized")
        
        result = process_pet_report(user_input, *agents)
        
        # Clean up temp files
        for path in image_paths:
            try:
                os.remove(path)
            except:
                pass
        
        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "result": result.dict() if hasattr(result, 'dict') else result.model_dump()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/search")
async def search_pets(
    province: Optional[str] = None,
    species: Optional[str] = None,
    size: Optional[str] = None,
    limit: int = 10
):
    """
    Search for pets in the database (basic search endpoint)
    
    - **province**: Filter by province
    - **species**: Filter by species (dog/cat)
    - **size**: Filter by size (small/medium/large)
    - **limit**: Maximum results to return
    """
    try:
        # This would query your database/vector store
        # For now, return a placeholder response
        return {
            "success": True,
            "message": "Search functionality - coming soon",
            "filters": {
                "province": province,
                "species": species,
                "size": size,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
