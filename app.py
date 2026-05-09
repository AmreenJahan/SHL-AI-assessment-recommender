"""
FastAPI application for SHL Assessment Recommender System.

This module provides the main API endpoints:
- GET /health - Health check endpoint
- POST /chat - Chat endpoint for assessment recommendations

The application is designed to be:
- Stateless (no session memory)
- Fast (30-second timeout requirement)
- Schema compliant (strict validation)
- Production ready
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import ChatRequest, ChatResponse, HealthResponse, Message
from chat_logic import get_chat_logic
from retriever import get_retriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup: Initialize components
    logger.info("Starting SHL Assessment Recommender System...")
    
    try:
        # Initialize retriever (loads catalog and builds index)
        retriever = get_retriever()
        if not retriever.is_ready():
            logger.error("Failed to initialize retriever - catalog may be empty")
        else:
            stats = retriever.get_index_stats()
            logger.info(f"Retriever ready: {stats}")
        
        # Initialize chat logic (loads LLM client)
        chat_logic = get_chat_logic()
        logger.info("Chat logic initialized")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("Shutting down SHL Assessment Recommender System...")


# Create FastAPI application
app = FastAPI(
    title="SHL Assessment Recommender",
    description="AI-powered recommender for SHL assessments",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timeout middleware
@app.middleware("http")
async def add_timeout_header(request: Request, call_next):
    """
    Add timeout information to response headers for monitoring.
    """
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add processing time to headers
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 2.0:  # Log requests taking more than 2 seconds
            logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Request failed after {process_time:.2f}s: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of the service and its components.
    This endpoint is used for monitoring and load balancer health checks.
    
    Returns:
        HealthResponse: Service health status
    """
    try:
        # Check if retriever is ready
        retriever = get_retriever()
        retriever_status = retriever.is_ready()
        
        if not retriever_status:
            logger.warning("Health check: Retriever not ready")
            return HealthResponse(status="degraded")
        
        logger.debug("Health check: All components ready")
        return HealthResponse(status="ok")
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="error")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint for assessment recommendations.
    
    This is the main endpoint that processes user messages and returns
    SHL assessment recommendations. It handles:
    - Initial recommendations
    - Clarification questions
    - Comparisons between assessments
    - Refinements based on conversation history
    
    The endpoint is stateless and processes each request independently.
    
    Args:
        request: ChatRequest containing conversation history
        
    Returns:
        ChatResponse: AI reply with recommendations
        
    Raises:
        HTTPException: For invalid requests or processing errors
    """
    # Validate request
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
    
    # Validate message roles
    for i, message in enumerate(request.messages):
        if message.role not in ["user", "assistant"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid role '{message.role}' in message {i}. Must be 'user' or 'assistant'"
            )
    
    # Ensure last message is from user
    if request.messages[-1].role != "user":
        raise HTTPException(
            status_code=400, 
            detail="Last message must be from user"
        )
    
    try:
        # Process the conversation
        chat_logic = get_chat_logic()
        response = chat_logic.process_message(request.messages)
        
        # Validate response structure
        if not isinstance(response.reply, str):
            raise ValueError("Response reply must be a string")
        
        if not isinstance(response.recommendations, list):
            raise ValueError("Response recommendations must be a list")
        
        if not isinstance(response.end_of_conversation, bool):
            raise ValueError("Response end_of_conversation must be a boolean")
        
        logger.info(f"Processed chat request: {len(request.messages)} messages, "
                   f"{len(response.recommendations)} recommendations")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in chat processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler.
    
    Provides consistent error responses for HTTP exceptions.
    """
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": "http_error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unexpected errors.
    
    Catches any unhandled exceptions and returns a generic error response.
    """
    logger.error(f"Unhandled exception: {type(exc).__name__}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "type": "server_error"}
    )


# Root endpoint for basic info
@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dictionary with API information
    """
    return {
        "name": "SHL Assessment Recommender API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        },
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application directly
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )
