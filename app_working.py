"""
Working minimal SHL Assessment Recommender.

Guaranteed to return results for any query.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, HealthResponse, Assessment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender (Working Version)",
    description="Minimal working version for guaranteed results",
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
    {"name": "Numerical Reasoning Test", "url": "https://www.shl.com/solutions/products/product-catalog/numerical-reasoning/", "test_type": "Cognitive"},
    {"name": "Verbal Reasoning Test", "url": "https://www.shl.com/solutions/products/product-catalog/verbal-reasoning/", "test_type": "Cognitive"},
    {"name": "Abstract Reasoning Test", "url": "https://www.shl.com/solutions/products/product-catalog/abstract-reasoning/", "test_type": "Cognitive"},
    {"name": "Situational Judgement Test", "url": "https://www.shl.com/solutions/products/product-catalog/situational-judgement/", "test_type": "Cognitive"},
    {"name": "Customer Service Aptitude Test", "url": "https://www.shl.com/solutions/products/product-catalog/customer-service/", "test_type": "Behavioral"},
    {"name": "Problem Solving Assessment", "url": "https://www.shl.com/solutions/products/product-catalog/problem-solving/", "test_type": "Cognitive"},
]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with guaranteed results.
    """
    try:
        if not request.messages:
            return ChatResponse(
                reply="Hello! I'm here to help you find the right SHL assessments. What type of role are you hiring for?",
                recommendations=[],
                end_of_conversation=False
            )
        
        # Get the latest user message
        latest_message = request.messages[-1]
        if latest_message.role != "user":
            return ChatResponse(
                reply="I'm ready to help you with SHL assessment recommendations. What would you like to know?",
                recommendations=[],
                end_of_conversation=False
            )
        
        user_query = latest_message.content.lower()
        
        # Simple keyword matching
        recommended_assessments = []
        reply = ""
        
        if any(word in user_query for word in ['java', 'jvm', 'spring']):
            recommended_assessments = [STATIC_ASSESSMENTS[0]]  # Java Programming Test
            reply = "For Java development, I recommend the Java Programming Test. This assesses syntax, data structures, and problem-solving skills specific to Java programming."
        
        elif any(word in user_query for word in ['python', 'django', 'flask']):
            recommended_assessments = [STATIC_ASSESSMENTS[1]]  # Python Programming Test
            reply = "For Python development, I recommend the Python Programming Test. This evaluates Python syntax, frameworks, and programming concepts."
        
        elif any(word in user_query for word in ['personality', 'opq', 'behavior', 'style']):
            recommended_assessments = [STATIC_ASSESSMENTS[2]]  # OPQ32
            reply = "For personality assessment, I recommend the OPQ32. This measures 32 behavioral characteristics relevant to workplace performance and predicts how a candidate will fit into your work environment."
        
        elif any(word in user_query for word in ['cognitive', 'reasoning', 'aptitude', 'numerical', 'verbal']):
            recommended_assessments = STATIC_ASSESSMENTS[3:6]  # Cognitive tests
            reply = "For cognitive ability assessment, I recommend tests like G+ General Ability Test, Numerical Reasoning, and Verbal Reasoning. These measure problem-solving capabilities and learning potential."
        
        elif any(word in user_query for word in ['manager', 'leadership', 'lead', 'supervisor']):
            recommended_assessments = [STATIC_ASSESSMENTS[2], STATIC_ASSESSMENTS[3]]  # OPQ32 + Cognitive
            reply = "For leadership roles, I recommend both personality assessment (OPQ32) and cognitive tests (G+ General Ability Test). This combination evaluates both behavioral fit and problem-solving capabilities."
        
        elif any(word in user_query for word in ['developer', 'programmer', 'engineer', 'coder']):
            recommended_assessments = [STATIC_ASSESSMENTS[0], STATIC_ASSESSMENTS[1]]  # Java + Python
            reply = "For software development roles, I recommend both Java Programming Test and Python Programming Test. These assess technical skills across multiple programming languages."
        
        else:
            # Default recommendations
            recommended_assessments = STATIC_ASSESSMENTS[:3]  # Top 3 assessments
            reply = "Here are some popular SHL assessments that might be relevant: Java Programming Test, OPQ32, and G+ General Ability Test. Could you provide more specific details about your role?"
        
        # Convert to proper format
        assessments_response = []
        for i, assessment in enumerate(recommended_assessments):
            assessments_response.append(Assessment(
                name=assessment["name"],
                url=assessment["url"],
                test_type=assessment["test_type"]
            ))
        
        return ChatResponse(
            reply=reply,
            recommendations=assessments_response,
            end_of_conversation=False
        )
        
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
