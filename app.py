#!/usr/bin/env python3
"""
YouTube Agent Roma - Web API Application
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from agents.yt_bundle.executors import YouTubeAgentExecutor
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    topic: str
    audience: Optional[str] = "general"
    query: Optional[str] = None

class AnalysisRequest(BaseModel):
    data: Dict[str, Any]

class ProcessRequest(BaseModel):
    input_data: Dict[str, Any]

class Response(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Agent Roma API",
    description="AI-powered YouTube content analysis and processing agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the executor
executor = YouTubeAgentExecutor()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {"message": "YouTube Agent Roma API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "YouTube Agent Roma API"}

@app.post("/search", response_model=Response)
async def search_content(request: SearchRequest):
    """Search for YouTube content based on topic and audience"""
    try:
        # Create search query from topic and audience
        query = request.query or f"{request.topic} for {request.audience}"
        
        result = executor.execute("search", query=query)
        
        return Response(
            success=result.get("success", False),
            message="Search completed successfully" if result.get("success") else "Search failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=Response)
async def analyze_content(request: AnalysisRequest):
    """Analyze YouTube content data"""
    try:
        result = executor.execute("analyze", data=request.data)
        
        return Response(
            success=result.get("success", False),
            message="Analysis completed successfully" if result.get("success") else "Analysis failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process", response_model=Response)
async def process_content(request: ProcessRequest):
    """Process YouTube content data"""
    try:
        result = executor.execute("process", input_data=request.input_data)
        
        return Response(
            success=result.get("success", False),
            message="Processing completed successfully" if result.get("success") else "Processing failed",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CLI compatibility - keep the original main function for CLI usage
def main():
    """CLI application entry point"""
    print("YouTube Agent Roma - Starting CLI mode...")
    
    try:
        from agents.yt_bundle.executors import main as run_agent
        run_agent()
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)

