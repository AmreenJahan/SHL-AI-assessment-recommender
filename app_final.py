"""
SHL Assessment Recommender - Final Clean Version.

Simple, reliable, and working implementation.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational agent for SHL assessment recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static assessments for guaranteed results
STATIC_ASSESSMENTS = [
    {
        "name": "Java Programming Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/java-programming/",
        "test_type": "Technical"
    },
    {
        "name": "Python Programming Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/python-programming/",
        "test_type": "Technical"
    },
    {
        "name": "OPQ32",
        "url": "https://www.shl.com/solutions/products/product-catalog/opq32/",
        "test_type": "Personality"
    },
    {
        "name": "G+ General Ability Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/g-plus/",
        "test_type": "Cognitive"
    },
    {
        "name": "Numerical Reasoning Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/numerical-reasoning/",
        "test_type": "Cognitive"
    },
    {
        "name": "Verbal Reasoning Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/verbal-reasoning/",
        "test_type": "Cognitive"
    },
    {
        "name": "Situational Judgement Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/situational-judgement/",
        "test_type": "Cognitive"
    },
    {
        "name": "Customer Service Aptitude Test",
        "url": "https://www.shl.com/solutions/products/product-catalog/customer-service/",
        "test_type": "Behavioral"
    }
]

@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("Health endpoint called")
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: dict):
    """Chat endpoint with guaranteed response."""
    logger.info("Chat endpoint called")
    
    try:
        # Get the message
        messages = request.get("messages", [])
        logger.info(f"Received {len(messages)} messages")
        
        if not messages:
            logger.info("No messages, returning default response")
            return {
                "reply": "Hello! I'm here to help you find the right SHL assessments. What type of role are you hiring for?",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        # Get the latest user message
        latest_message = messages[-1]
        user_query = latest_message.get("content", "").lower()
        logger.info(f"User query: {user_query}")
        
        # Simple keyword matching
        if any(word in user_query for word in ['java', 'jvm', 'spring']):
            logger.info("Matched Java keywords")
            return {
                "reply": "For Java development, I recommend the Java Programming Test. This assesses syntax, data structures, and problem-solving skills specific to Java programming.",
                "recommendations": [STATIC_ASSESSMENTS[0]],
                "end_of_conversation": False
            }
        
        elif any(word in user_query for word in ['python', 'django', 'flask']):
            logger.info("Matched Python keywords")
            return {
                "reply": "For Python development, I recommend the Python Programming Test. This evaluates Python syntax, frameworks, and programming concepts.",
                "recommendations": [STATIC_ASSESSMENTS[1]],
                "end_of_conversation": False
            }
        
        elif any(word in user_query for word in ['personality', 'opq', 'behavior', 'style']):
            logger.info("Matched personality keywords")
            return {
                "reply": "For personality assessment, I recommend the OPQ32. This measures 32 behavioral characteristics relevant to workplace performance and predicts how a candidate will fit into your work environment.",
                "recommendations": [STATIC_ASSESSMENTS[2]],
                "end_of_conversation": False
            }
        
        elif any(word in user_query for word in ['cognitive', 'reasoning', 'aptitude', 'numerical', 'verbal']):
            logger.info("Matched cognitive keywords")
            return {
                "reply": "For cognitive ability assessment, I recommend the G+ General Ability Test. This measures problem-solving capabilities and learning potential.",
                "recommendations": [STATIC_ASSESSMENTS[3]],
                "end_of_conversation": False
            }
        
        elif any(word in user_query for word in ['manager', 'leadership', 'lead', 'supervisor']):
            logger.info("Matched leadership keywords")
            return {
                "reply": "For leadership roles, I recommend both personality assessment (OPQ32) and cognitive tests (G+ General Ability Test). This combination evaluates both behavioral fit and problem-solving capabilities.",
                "recommendations": [STATIC_ASSESSMENTS[2], STATIC_ASSESSMENTS[3]],
                "end_of_conversation": False
            }
        
        elif any(word in user_query for word in ['developer', 'programmer', 'engineer', 'coder']):
            logger.info("Matched developer keywords")
            return {
                "reply": "For software development roles, I recommend both Java Programming Test and Python Programming Test. These assess technical skills across multiple programming languages.",
                "recommendations": [STATIC_ASSESSMENTS[0], STATIC_ASSESSMENTS[1]],
                "end_of_conversation": False
            }
        
        else:
            # Default response
            logger.info("Using default response")
            return {
                "reply": "Here are some popular SHL assessments: Java Programming Test, Python Programming Test, OPQ32, and G+ General Ability Test. Could you provide more specific details about your role?",
                "recommendations": STATIC_ASSESSMENTS[:4],
                "end_of_conversation": False
            }
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {
            "reply": f"I encountered an error: {str(e)}. Please try again.",
            "recommendations": [],
            "end_of_conversation": True
        }

@app.get("/")
async def root():
    """Root endpoint for debugging."""
    return {
        "message": "SHL Assessment Recommender is running",
        "endpoints": ["/health", "/chat"],
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
