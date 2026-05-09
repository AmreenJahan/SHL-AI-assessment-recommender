"""
Debug version of SHL Assessment Recommender.

Adds extensive logging to identify the exact issue.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, HealthResponse, Assessment

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender (Debug Version)",
    description="Debug version with extensive logging",
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

# Static assessments for guaranteed results
STATIC_ASSESSMENTS = [
    {"name": "Java Programming Test", "url": "https://www.shl.com/solutions/products/product-catalog/java-programming/", "test_type": "Technical"},
    {"name": "Python Programming Test", "url": "https://www.shl.com/solutions/products/product-catalog/python-programming/", "test_type": "Technical"},
    {"name": "OPQ32", "url": "https://www.shl.com/solutions/products/product-catalog/opq32/", "test_type": "Personality"},
    {"name": "G+ General Ability Test", "url": "https://www.shl.com/solutions/products/product-catalog/g-plus/", "test_type": "Cognitive"},
]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    logger.info("Health check called")
    return HealthResponse(status="ok")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with guaranteed results and debug logging.
    """
    logger.info(f"Chat endpoint called with {len(request.messages)} messages")
    
    try:
        if not request.messages:
            logger.warning("No messages provided")
            return ChatResponse(
                reply="Hello! I'm here to help you find the right SHL assessments. What type of role are you hiring for?",
                recommendations=[],
                end_of_conversation=False
            )
        
        # Get the latest user message
        latest_message = request.messages[-1]
        logger.info(f"Latest message: {latest_message}")
        
        if latest_message.role != "user":
            logger.warning(f"Invalid message role: {latest_message.role}")
            return ChatResponse(
                reply="I'm ready to help you with SHL assessment recommendations. What would you like to know?",
                recommendations=[],
                end_of_conversation=False
            )
        
        user_query = latest_message.content.lower()
        logger.info(f"User query: {user_query}")
        
        # Simple keyword matching
        recommended_assessments = []
        reply = ""
        
        if any(word in user_query for word in ['java', 'jvm', 'spring']):
            recommended_assessments = [STATIC_ASSESSMENTS[0]]  # Java Programming Test
            reply = "For Java development, I recommend the Java Programming Test. This assesses syntax, data structures, and problem-solving skills specific to Java programming."
            logger.info("Matched Java keywords")
        
        elif any(word in user_query for word in ['python', 'django', 'flask']):
            recommended_assessments = [STATIC_ASSESSMENTS[1]]  # Python Programming Test
            reply = "For Python development, I recommend the Python Programming Test. This evaluates Python syntax, frameworks, and programming concepts."
            logger.info("Matched Python keywords")
        
        elif any(word in user_query for word in ['personality', 'opq', 'behavior', 'style']):
            recommended_assessments = [STATIC_ASSESSMENTS[2]]  # OPQ32
            reply = "For personality assessment, I recommend the OPQ32. This measures 32 behavioral characteristics relevant to workplace performance and predicts how a candidate will fit into your work environment."
            logger.info("Matched personality keywords")
        
        elif any(word in user_query for word in ['cognitive', 'reasoning', 'aptitude', 'numerical', 'verbal']):
            recommended_assessments = [STATIC_ASSESSMENTS[3]]  # G+ General Ability Test
            reply = "For cognitive ability assessment, I recommend the G+ General Ability Test. This measures problem-solving capabilities and learning potential."
            logger.info("Matched cognitive keywords")
        
        else:
            # Default recommendations
            recommended_assessments = STATIC_ASSESSMENTS[:3]  # Top 3 assessments
            reply = "Here are some popular SHL assessments that might be relevant: Java Programming Test, OPQ32, and G+ General Ability Test. Could you provide more specific details about your role?"
            logger.info("Using default recommendations")
        
        # Convert to proper format
        assessments_response = []
        logger.info(f"Creating {len(recommended_assessments)} assessment responses")
        
        for i, assessment in enumerate(recommended_assessments):
            try:
                assessment_response = Assessment(
                    name=assessment["name"],
                    url=assessment["url"],
                    test_type=assessment["test_type"]
                )
                assessments_response.append(assessment_response)
                logger.info(f"Created assessment {i+1}: {assessment['name']}")
            except Exception as e:
                logger.error(f"Error creating assessment {i+1}: {e}")
                raise
        
        logger.info(f"Final response: {len(assessments_response)} assessments")
        
        return ChatResponse(
            reply=reply,
            recommendations=assessments_response,
            end_of_conversation=False
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="debug"
    )
