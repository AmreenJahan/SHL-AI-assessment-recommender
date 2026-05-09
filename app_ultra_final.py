"""
Ultra-lightweight FastAPI application for SHL Assessment Recommender.

Optimized for 512MB memory constraints with no ML dependencies.
"""

import os
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, HealthResponse
from retriever_ultra import get_ultra_retriever
from chat_logic_ultra import get_ultra_chat_logic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender (Ultra-Lightweight)",
    description="Memory-optimized conversational agent for SHL assessment recommendations",
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with ultra-lightweight processing.
    
    Processes conversation and returns SHL assessment recommendations.
    """
    try:
        # Initialize components on demand
        chat_logic = get_ultra_chat_logic()
        
        # Process message
        response = chat_logic.process_message(request.messages)
        
        return response
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
