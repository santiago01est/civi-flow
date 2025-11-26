# Civi Flow API - Backend Service

Enterprise-grade FastAPI backend service for Civi Flow, an AI-powered civic engagement platform designed to facilitate citizen interaction with government information and services.

## 🏗️ Architecture Overview

This microservice provides a RESTful API built with FastAPI, featuring AI-powered conversational capabilities, document search integration, and real-time notifications. The service is containerized with Docker and designed for horizontal scalability.

### Key Features

- **AI-Powered Chat**: Integration with Azure OpenAI and OpenAI APIs with intelligent fallback mechanisms
- **Document Search**: Azure AI Search integration for government document retrieval
- **Citation Management**: Automatic source attribution and reference linking
- **Conversation Persistence**: MongoDB/Azure Cosmos DB for scalable, cloud-native data storage
- **Notification System**: Real-time notification management
- **Observability**: OpenTelemetry instrumentation for distributed tracing
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

### Tech Stack

- **Framework**: FastAPI 0.100+
- **AI/ML**: OpenAI SDK, Azure OpenAI SDK
- **Database**: Motor (Async MongoDB Driver), Azure Cosmos DB for MongoDB API
- **ODM**: Pydantic models with MongoDB integration
- **Search**: Azure AI Search SDK
- **Observability**: OpenTelemetry, Jaeger
- **Containerization**: Docker, Docker Compose
- **Python**: 3.11+

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- (Optional) Python 3.11+ for local development

### Docker Deployment (Recommended)

1. **Clone and navigate to project**
```bash
git clone <repository-url>
cd civi-flow
```

2. **Configure environment variables**
```bash
cp server/.env.example server/.env
# Edit server/.env with your API keys
```

3. **Start services**
```bash
docker compose up -d
```

4. **Verify deployment**
```bash
curl http://localhost:8000/health
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Local Development Setup

1. **Create virtual environment**
```bash
cd server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize database**
```bash
python init_db.py
```

4. **Run development server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Core Endpoints

#### Chat Management

**POST `/api/v1/chat/message`**

Send a message and receive AI-powered response with source citations.

```bash
curl -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "What are the current regulations on short-term rentals?",
    "conversation_id": "optional-uuid"
  }'
```

**Response Schema:**
```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "string",
    "timestamp": "ISO8601",
    "citations": null,
    "isThinking": false
  },
  "assistant_message": {
    "id": "uuid",
    "role": "model",
    "content": "string",
    "timestamp": "ISO8601",
    "citations": [
      {
        "id": "string",
        "title": "string",
        "uri": "string",
        "type": "PDF|Web",
        "size": "string"
      }
    ],
    "isThinking": false
  },
  "conversation_id": "uuid"
}
```

**GET `/api/v1/chat/history/{conversation_id}`**

Retrieve complete conversation history with all messages.

```bash
curl "http://localhost:8000/api/v1/chat/history/{conversation_id}"
```

#### Notification Management

**GET `/api/v1/notifications`**

List notifications with optional filtering.

**Query Parameters:**
- `user_id` (optional): Filter by user identifier
- `limit` (optional, default: 50): Maximum results to return

**POST `/api/v1/notifications`**

Create a new notification.

**PATCH `/api/v1/notifications/{notification_id}/read`**

Mark notification as read.

#### Health & Status

**GET `/health`**

Health check endpoint for monitoring and load balancers.

```bash
curl http://localhost:8000/health
```

Response: `{"status": "healthy", "service": "civi-chat-api"}`

## 🏛️ Architecture

### Project Structure

```
server/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/           # API route handlers
│   │       │   ├── chat.py         # Chat conversation endpoints
│   │       │   ├── notifications.py # Notification endpoints
│   │       │   └── users.py        # User management
│   │       └── router.py           # API version router
│   ├── config/
│   │   ├── settings.py             # Environment configuration
│   │   ├── azure_clients.py        # Azure SDK clients
│   │   └── telemetry.py            # OpenTelemetry setup
│   ├── core/
│   │   ├── exceptions.py           # Custom exception handlers
│   │   ├── middleware.py           # HTTP middleware
│   │   └── security.py             # Authentication & authorization
│   ├── db/
│   │   └── mongodb.py              # MongoDB connection management
│   ├── models/                     # Pydantic models for MongoDB
│   │   ├── conversation.py         # Conversation & Message models
│   │   ├── notification.py         # Notification model
│   │   └── user.py                 # User model
│   ├── repositories/               # Data access layer
│   │   ├── conversation_repository.py
│   │   ├── notification_repository.py
│   │   └── user_repository.py
│   ├── schemas/                    # Pydantic request/response models
│   │   ├── chat.py
│   │   ├── notification.py
│   │   └── user.py
│   ├── services/                   # Business logic layer
│   │   ├── azure_ai_service.py     # AI model integration
│   │   ├── search_service.py       # Document search
│   │   ├── content_safety_service.py
│   │   └── notification_service.py
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── logger.py
│   │   └── metrics.py
│   └── main.py                     # FastAPI application entry point
├── tests/
│   ├── conftest.py                 # Pytest configuration
│   └── test_*.py                   # Unit and integration tests
├── docker/
│   ├── Dockerfile                  # Production Docker image
│   └── docker-compose.yml          # Development compose file
├── init_db.py                      # Database initialization script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

### Design Patterns

- **Repository Pattern**: Abstracts data access logic from business logic
- **Service Layer**: Encapsulates business rules and external integrations
- **Dependency Injection**: Leverages FastAPI's DI system for testability
- **Schema Validation**: Pydantic models ensure type safety and validation

### Service Components

**AI Service (`azure_ai_service.py`)**
- Multi-provider support (Azure OpenAI, OpenAI)
- Automatic fallback to mock responses for development
- Context-aware response generation with document integration
- Error handling and retry logic

**Search Service (`search_service.py`)**
- Azure AI Search integration for document retrieval
- Automatic citation generation
- Mock data support for development environments

**Repository Layer**
- Clean separation of database operations
- Consistent CRUD interfaces
- Transaction management
- Query optimization

## ⚙️ Configuration

### Environment Variables

The service uses environment variables for configuration. Copy `.env.example` to `.env` and configure as needed.

#### Required for Development (Mock Mode)

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=civi_flow_db
ALLOWED_ORIGINS=["http://localhost:5173"]
```

#### OpenAI Configuration (Recommended)

```env
OPENAI_API_KEY=sk-proj-your-api-key
OPENAI_MODEL=gpt-4o-mini
```

#### Azure OpenAI Configuration (Enterprise)

```env
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

#### Azure AI Search Configuration

```env
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=government-docs
```

#### Database Configuration

**Development (Local MongoDB)**
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=civi_flow_db
```

**Production (Azure Cosmos DB for MongoDB)**
```env
MONGODB_URL=mongodb://<account-name>:<password>@<account-name>.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000
MONGODB_DATABASE_NAME=civi_flow_db
MONGODB_MAX_POOL_SIZE=10
MONGODB_MIN_POOL_SIZE=1
```

**Azure Cosmos DB Setup:**
1. Create Azure Cosmos DB account with MongoDB API
2. Copy connection string from Azure Portal
3. Replace `<account-name>` and `<password>` in MONGODB_URL
4. Database and collections are created automatically on first use

#### CORS Configuration

```env
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000","https://your-domain.com"]
```

### Docker Compose Configuration

The service includes a complete Docker Compose setup with:

- **API Server**: Main FastAPI application
- **Jaeger**: Distributed tracing backend
- **Client**: Frontend application (optional)

**Start all services:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f server
```

**Stop services:**
```bash
docker compose down
```

**Rebuild after code changes:**
```bash
docker compose build server
docker compose up -d
```

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest

# With coverage
pytest --cov=app tests/

# Integration tests
pytest tests/integration/
```

### API Testing Tools

**Using HTTPie:**
```bash
http POST http://localhost:8000/api/v1/chat/message content="Your question here"
```

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"content":"Your question here"}'
```

**Using PowerShell:**
```powershell
$body = @{ content = "Your question here" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat/message" `
  -Method Post -ContentType "application/json" -Body $body
```

## 🔒 Security Considerations

- API keys should be stored in environment variables, never committed to version control
- Use `.env` files for local development only
- In production, use secure secret management (Azure Key Vault, AWS Secrets Manager, etc.)
- CORS origins should be explicitly defined for production environments
- Consider implementing rate limiting for public APIs
- Enable HTTPS in production environments

## 📊 Monitoring & Observability

### OpenTelemetry Integration

The service includes OpenTelemetry instrumentation for:
- HTTP request tracing
- Database query tracing
- External API call tracing
- Custom business logic spans

**View traces in Jaeger UI:**
```
http://localhost:16686
```

### Logging

Structured logging is configured using Python's logging module. Logs include:
- Request/response details
- Error stacktraces
- Performance metrics
- AI service interactions

### Health Checks

**Endpoint:** `GET /health`

Use this endpoint for:
- Container health checks
- Load balancer health probes
- Monitoring system integration

## 🚀 Deployment

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in environment variables
- [ ] Configure Azure Cosmos DB for MongoDB connection string
- [ ] Set up proper CORS origins
- [ ] Enable HTTPS/TLS
- [ ] Configure Azure OpenAI (not OpenAI free tier)
- [ ] Set up Azure AI Search with production index
- [ ] Configure proper logging and monitoring
- [ ] Set up database backups
- [ ] Implement rate limiting
- [ ] Review and update security headers

### Docker Production Build

```bash
docker build -t civi-flow-api:latest -f docker/Dockerfile .
docker run -p 8000:8000 --env-file .env civi-flow-api:latest
```

### Environment-Specific Builds

```bash
# Production
docker compose -f docker-compose.prod.yml up -d

# Staging
docker compose -f docker-compose.staging.yml up -d
```

## 🔗 Integration Examples

### Frontend Integration (React/TypeScript)

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
  conversation_id: string;
}

async function sendMessage(content: string, conversationId?: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content,
      conversation_id: conversationId
    })
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}
```

### Python Client Example

```python
import requests

class CiviFlowClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def send_message(self, content: str, conversation_id: str = None):
        payload = {"content": content}
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        response = requests.post(
            f"{self.base_url}/chat/message",
            json=payload
        )
        response.raise_for_status()
        return response.json()

# Usage
client = CiviFlowClient()
result = client.send_message("What are the zoning regulations?")
print(result["assistant_message"]["content"])
```

## 🐛 Troubleshooting

### Common Issues

**Issue: "No AI service configured" warning**
- **Solution**: Set `OPENAI_API_KEY` or Azure OpenAI credentials in `.env`
- **Note**: Service works with mock responses if neither is configured

**Issue: Database connection errors**
- **Solution**: Verify `MONGODB_URL` connection string is correct
- **Solution**: For Azure Cosmos DB, ensure firewall rules allow your IP
- **Solution**: Check that MongoDB service is running (local) or Cosmos DB account is active (Azure)
- **Solution**: Verify connection string includes SSL parameters for Cosmos DB

**Issue: CORS errors from frontend**
- **Solution**: Add your frontend URL to `ALLOWED_ORIGINS` in `.env`
- **Example**: `ALLOWED_ORIGINS=["http://localhost:5173"]`

**Issue: Container can't find `.env` file**
- **Solution**: Ensure `env_file` is configured in `docker-compose.yaml`
- **Solution**: Verify `.env` file exists in `server/` directory

### Debug Mode

Enable detailed logging:
```env
LOG_LEVEL=DEBUG
```

View container logs:
```bash
docker compose logs -f server
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and returns
- Write docstrings for all public methods
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs` endpoint