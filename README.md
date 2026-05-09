# SHL Assessment Recommender System

A complete but simple AI-powered conversational recommender system for SHL assessments. Built with FastAPI, Sentence Transformers, and FAISS for semantic search.

## 🚀 Features

- **Conversational AI**: Natural language interface for assessment recommendations
- **Semantic Search**: Uses embeddings and FAISS for accurate assessment matching
- **Guardrails**: Built-in safety measures to ensure appropriate responses
- **Stateless API**: No session memory - each request is independent
- **Multiple Scenarios**: Handles recommendations, clarifications, comparisons, and refinements
- **Fast Response**: Optimized for 30-second timeout requirement
- **Schema Compliant**: Strict Pydantic validation for all inputs/outputs

## 📋 Requirements

- Python 3.8+
- API key for OpenRouter OR Gemini (free tier available)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd SHL
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up API key**:
```bash
# For OpenRouter (recommended)
export OPENROUTER_API_KEY="your-openrouter-api-key"

# OR for Gemini
export GEMINI_API_KEY="your-gemini-api-key"
```

4. **Prepare the catalog**:
The system will automatically load assessments from `data/shl_catalog.json`. A sample catalog is included.

## 🏗️ Architecture

```
project/
│
├── app.py                 # Main FastAPI application
├── models.py             # Pydantic data models
├── catalog_loader.py     # Catalog management
├── embedder.py           # Text embedding with Sentence Transformers
├── retriever.py          # FAISS-based semantic search
├── chat_logic.py         # Core conversation logic & LLM integration
├── prompts.py            # LLM prompt templates
├── guardrails.py         # Input validation & safety
├── requirements.txt       # Python dependencies
├── README.md            # This file
└── data/
    └── shl_catalog.json  # SHL assessment catalog
```

## 🔧 How It Works

### 1. **Retrieval System**
- **Embedding Creation**: Uses `all-MiniLM-L6-v2` to create vector representations
- **FAISS Index**: Stores embeddings for fast similarity search
- **Semantic Matching**: Finds assessments based on meaning, not just keywords

### 2. **Clarification Logic**
- Detects vague queries like "hiring a developer"
- Asks targeted questions:
  - Seniority level?
  - Technical vs personality?
  - Specific skills needed?
  - Remote testing requirements?

### 3. **Refinement Handling**
- Combines conversation history with new requests
- Updates recommendations based on additional context
- Maintains conversation flow without session memory

### 4. **Stateless Memory**
- Each request contains full conversation history
- No database or session storage required
- Easy to scale and deploy

### 5. **Guardrails System**
- Blocks inappropriate requests (legal advice, general hiring tips)
- Prevents prompt injection attempts
- Ensures responses stay SHL-focused

## 🚀 Running the Application

### Local Development

1. **Start the server**:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API**:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Production Deployment (Render)

1. **Create `render.yaml`**:
```yaml
services:
  - type: web
    name: shl-recommender
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
```

2. **Deploy to Render**:
- Connect your GitHub repository
- Add your API key as environment variable
- Deploy automatically

## 📡 API Endpoints

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

### POST /chat
Main chat endpoint for assessment recommendations.

**Request**:
```json
{
  "messages": [
    {"role": "user", "content": "Hiring a Java developer"},
    {"role": "assistant", "content": "What seniority level?"},
    {"role": "user", "content": "Mid-level"}
  ]
}
```

**Response**:
```json
{
  "reply": "Based on your needs, I recommend these SHL assessments...",
  "recommendations": [
    {
      "name": "Java Programming Test",
      "url": "https://shl.com/java-test",
      "description": "Assesses Java programming skills...",
      "test_type": "Technical",
      "duration": "45 minutes",
      "remote_testing": true
    }
  ],
  "end_of_conversation": false
}
```

## 🧪 Example Requests

### 1. **Initial Recommendation**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to hire a senior software engineer"}
    ]
  }'
```

### 2. **Clarification Scenario**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "hiring"}
    ]
  }'
```

### 3. **Comparison Scenario**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Compare OPQ and GSA"}
    ]
  }'
```

### 4. **Refinement Scenario**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need to hire a Java developer"},
      {"role": "assistant", "content": "What seniority level?"},
      {"role": "user", "content": "Mid-level"},
      {"role": "user", "content": "Also include personality tests"}
    ]
  }'
```

## 🧪 Testing

### Health Check Test
```bash
curl http://localhost:8000/health
```

### Load Testing (optional)
```bash
# Install artillery
npm install -g artillery

# Create test config
cat > load-test.yml << EOF
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 5

scenarios:
  - name: "Chat endpoint"
    request:
      method: POST
      url: "/chat"
      json:
        messages:
          - role: "user"
            content: "I need to hire a developer"
EOF

# Run load test
artillery run load-test.yml
```

## 🔍 Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: OpenRouter API key (recommended)
- `GEMINI_API_KEY`: Gemini API key (alternative)

### Catalog Configuration
- Edit `data/shl_catalog.json` to update assessments
- Each assessment must have: `name`, `url`, `description`, `test_type`
- Optional fields: `duration`, `remote_testing`

## 🚨 Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (validation errors)
- `500`: Internal server error

Error responses include:
```json
{
  "error": "Error description",
  "type": "error_type"
}
```

## 📊 Performance Optimization

- **Embedding Caching**: Models are loaded once at startup
- **FAISS Index**: Fast similarity search (O(log n) complexity)
- **Batch Processing**: Efficient embedding of multiple texts
- **Timeout Handling**: 30-second limit with proper error handling
- **Memory Management**: Controlled memory usage for large catalogs

## 🔒 Security Considerations

- **Input Validation**: All inputs validated with Pydantic
- **Guardrails**: Blocks inappropriate requests
- **API Key Security**: Use environment variables, never hardcode
- **CORS Configuration**: Configure appropriately for production
- **Rate Limiting**: Consider adding rate limiting for production

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Error**:
   - Check internet connection for model download
   - Verify sufficient disk space
   - Check Python version compatibility

2. **API Key Errors**:
   - Verify environment variable is set
   - Check API key validity
   - Ensure correct API service (OpenRouter vs Gemini)

3. **Empty Catalog**:
   - Verify `data/shl_catalog.json` exists
   - Check JSON format validity
   - Ensure required fields are present

4. **FAISS Index Issues**:
   - Check catalog has assessments
   - Verify embedding model loaded correctly
   - Check memory availability

### Debug Mode
Enable debug logging:
```bash
export PYTHONPATH=$PYTHONPATH:.
uvicorn app:app --reload --log-level debug
```

## 📈 Monitoring

### Health Monitoring
- `/health` endpoint for load balancers
- Response time tracking in headers
- Error logging for troubleshooting

### Performance Metrics
- Request processing time
- Embedding generation time
- FAISS search performance
- LLM API response time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation
- Create an issue in the repository

---

**Built for SHL Labs Assessment Challenge** 🎯
