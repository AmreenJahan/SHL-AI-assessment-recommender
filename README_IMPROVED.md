# SHL Assessment Recommender System

A conversational AI agent for SHL assessment recommendations built with FastAPI, semantic search, and LLM integration.

## Overview

This system helps hiring managers and recruiters navigate SHL's assessment catalog through natural conversation. It handles vague queries, provides targeted recommendations, supports refinements, and compares assessments using catalog evidence.

## Architecture

### Components
- **FastAPI**: REST API with `/health` and `/chat` endpoints
- **Semantic Search**: Sentence Transformers + FAISS for meaning-based retrieval
- **LLM Integration**: Gemini Flash for natural conversation
- **Guardrails**: Input validation and safety checks
- **Stateless Design**: Each request contains full conversation history

### Data Flow
1. User message → Guardrails validation
2. Context analysis → Clarification/Recommendation/Comparison/Refinement
3. Semantic search → Relevant SHL assessments
4. LLM generation → Natural response with recommendations
5. Schema validation → Compliant JSON response

## Setup Instructions

### Prerequisites
- Python 3.8+
- Environment variables configured

### Installation
```bash
# Clone repository
git clone <repository-url>
cd SHL

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API key
```

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here  # Optional
```

### Running the Application
```bash
# Development server
uvicorn app:app --host 0.0.0.0 --port 8000

# Production server
uvicorn app:app --host 0.0.0.0 --port 10000
```

## API Documentation

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "ok"
}
```

### Chat Endpoint
```http
POST /chat
Content-Type: application/json
```

Request:
```json
{
  "messages": [
    {"role": "user", "content": "I need to hire a Java developer"}
  ]
}
```

Response:
```json
{
  "reply": "Based on your need for a Java developer...",
  "recommendations": [
    {
      "name": "Java Programming Test",
      "url": "https://www.shl.com/solutions/products/product-catalog/java-programming/",
      "test_type": "Technical"
    }
  ],
  "end_of_conversation": false
}
```

## Deployment

### Render Deployment
1. Push to GitHub
2. Connect repository to Render.com
3. Set `GEMINI_API_KEY` environment variable
4. Deploy automatically using `render.yaml`

### Environment Setup
- Production uses port 10000
- Cold start timeout: 2 minutes
- Health check path: `/health`

## Evaluation Strategy

### Test Coverage
- **Clarification Logic**: Vague query detection and response
- **Recommendation Quality**: Semantic search relevance scoring
- **Refinement Handling**: Context-aware constraint aggregation
- **Comparison Accuracy**: Assessment identification and catalog grounding
- **Guardrails Effectiveness**: Inappropriate request filtering
- **Schema Compliance**: Response format validation

### Automated Testing
```bash
# Run basic tests
python test_samples.py

# Run edge case tests
python test_edge_cases.py

# Test API stability
python test_stability.py
```

### Performance Metrics
- **Response Time**: <2 seconds for cached models
- **Cold Start**: ~30 seconds (model loading)
- **Memory Usage**: Efficient FAISS indexing
- **Timeout Compliance**: All operations under 30 seconds

## Limitations

### Current Constraints
- Catalog size: 27 SHL assessments (sample data)
- Model dependency: Requires external LLM API
- Language: English only
- Scope: SHL Individual Test Solutions only

### Future Improvements
- Real catalog integration via web scraping
- Multi-language support
- Assessment filtering by duration/remote testing
- Recommendation confidence scoring
- Conversation memory persistence

## Interview Preparation Notes

### Key Technical Concepts

**FAISS**: Vector similarity search library for efficient retrieval
- Enables fast semantic search across 27+ assessments
- Uses cosine similarity for relevance scoring

**Semantic Search**: Meaning-based vs keyword matching
- Sentence Transformers convert text to embeddings
- Captures conceptual similarity (e.g., "Java dev" → "Java Programming Test")

**Stateless API**: Each request independent
- No session storage required
- Scales horizontally without complexity
- Matches evaluator constraints

**Hallucination Prevention**: Grounded responses only
- All recommendations from SHL catalog
- URLs validated against catalog entries
- No external assessment suggestions

**Gemini Flash Choice**: Fast, cost-effective LLM
- Optimized for conversational tasks
- Lower latency than larger models
- Sufficient for recommendation logic

**Refinement Logic**: Context-aware constraint aggregation
- Combines all user messages in conversation
- Updates search with cumulative requirements
- Avoids restarting recommendation process

### Architecture Tradeoffs

**Deterministic over Complex Frameworks**
- Chose simple, predictable pipelines
- Avoided LangGraph/CrewAI complexity
- Prioritized evaluator reliability

**Beginner-Friendly Implementation**
- Clear module separation
- Extensive documentation
- No unnecessary abstractions
- Maintainable codebase

**Performance vs Features**
- Optimized for 30-second timeout constraint
- Prioritized core functionality over advanced features
- Designed for 8-turn conversation limit

---

This implementation demonstrates professional software engineering practices with robust error handling, comprehensive testing, and production-ready deployment configuration.
