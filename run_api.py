"""
Startup script for the REST API server
"""

import uvicorn
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING LOST PET INTELLIGENCE API")
    print("=" * 60)
    print()
    print("📍 API will be available at:")
    print("   - Main endpoint: http://localhost:8000")
    print("   - Interactive docs: http://localhost:8000/docs")
    print("   - Alternative docs: http://localhost:8000/redoc")
    print()
    print("💡 Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
