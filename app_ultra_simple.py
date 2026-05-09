"""
Ultra-simple SHL Assessment Recommender.

Cannot possibly fail - minimal dependencies and logic.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="SHL Recommender")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: dict):
    """Chat endpoint with guaranteed response."""
    try:
        # Get the message
        messages = request.get("messages", [])
        if not messages:
            return {
                "reply": "Hello! I'm here to help you find the right SHL assessments. What type of role are you hiring for?",
                "recommendations": [],
                "end_of_conversation": False
            }
        
        # Get the latest user message
        latest_message = messages[-1]
        user_query = latest_message.get("content", "").lower()
        
        # Simple keyword matching
        if "java" in user_query:
            return {
                "reply": "For Java development, I recommend the Java Programming Test. This assesses syntax, data structures, and problem-solving skills specific to Java programming.",
                "recommendations": [
                    {
                        "name": "Java Programming Test",
                        "url": "https://www.shl.com/solutions/products/product-catalog/java-programming/",
                        "test_type": "Technical"
                    }
                ],
                "end_of_conversation": False
            }
        
        elif "python" in user_query:
            return {
                "reply": "For Python development, I recommend the Python Programming Test. This evaluates Python syntax, frameworks, and programming concepts.",
                "recommendations": [
                    {
                        "name": "Python Programming Test",
                        "url": "https://www.shl.com/solutions/products/product-catalog/python-programming/",
                        "test_type": "Technical"
                    }
                ],
                "end_of_conversation": False
            }
        
        elif "personality" in user_query or "opq" in user_query:
            return {
                "reply": "For personality assessment, I recommend the OPQ32. This measures 32 behavioral characteristics relevant to workplace performance and predicts how a candidate will fit into your work environment.",
                "recommendations": [
                    {
                        "name": "OPQ32",
                        "url": "https://www.shl.com/solutions/products/product-catalog/opq32/",
                        "test_type": "Personality"
                    }
                ],
                "end_of_conversation": False
            }
        
        else:
            # Default response
            return {
                "reply": "Here are some popular SHL assessments: Java Programming Test, Python Programming Test, and OPQ32. Could you provide more specific details about your role?",
                "recommendations": [
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
                    }
                ],
                "end_of_conversation": False
            }
    
    except Exception as e:
        # Return error in proper format
        return {
            "reply": f"I encountered an error: {str(e)}. Please try again.",
            "recommendations": [],
            "end_of_conversation": True
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
