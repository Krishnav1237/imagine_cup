# ADHD Learning Platform - Complete Backend Setup Guide

## 📂 Complete File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry
│   ├── config.py                    # Configuration management
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py              # Database connection
│   │   └── auth.py                  # Authentication utilities
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                # SQLAlchemy models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic schemas
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py              # Auth endpoints
│   │       ├── content.py           # Content management
│   │       ├── learning.py          # Learning sessions
│   │       └── analytics.py         # Analytics endpoints
│   │
│   └── services/
│       ├── __init__.py
│       ├── content_processor.py     # Content processing orchestrator
│       ├── youtube_downloader.py    # YouTube downloader
│       ├── pdf_processor.py         # PDF text extraction
│       ├── pptx_processor.py        # PowerPoint extraction
│       ├── adaptive_engine.py       # Adaptive learning engine
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── adapter.py           # Storage interface
│       │   ├── local.py             # Local file storage
│       │   └── azure_blob.py        # Azure Blob storage
│       │
│       ├── transcription/
│       │   ├── __init__.py
│       │   └── transcriber.py       # Whisper/Azure Speech
│       │
│       └── chunking/
│           ├── __init__.py
│           └── ai_chunker.py        # Claude AI chunking
│
├── data/                            # Local SQLite database
├── uploads/                         # Local file uploads
├── tests/                           # Test files
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── .env                             # Your configuration (gitignored)
├── setup.py                         # Setup script
└── README.md                        # Documentation
```

## 🚀 Installation Steps

### 1. Prerequisites

```bash
# Python 3.9+
python --version

# FFmpeg (for audio processing)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt-get install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### 2. Clone and Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

**Minimum configuration for local development:**
```env
DEPLOYMENT_MODE=local
SECRET_KEY=your-random-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 4. Initialize Database

```bash
# Run setup script
python setup.py
```

This will:
- ✅ Create database tables
- ✅ Create test user (test@example.com / password123)
- ✅ Verify configuration
- ✅ Create necessary directories

### 5. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration Options

### Local Development Mode

```env
DEPLOYMENT_MODE=local
DATABASE_URL=sqlite:///./data/adhd_learning.db
UPLOAD_DIR=./uploads
ANTHROPIC_API_KEY=sk-ant-...
```

Features:
- SQLite database
- Local file storage
- Whisper transcription
- Synchronous processing

### Azure Production Mode

```env
DEPLOYMENT_MODE=azure

# Database
AZURE_DB_SERVER=myserver.postgres.database.azure.com
AZURE_DB_NAME=adhd_learning
AZURE_DB_USER=adminuser
AZURE_DB_PASSWORD=SecurePassword123!

# Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER=content

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=eastus
```

Features:
- PostgreSQL database
- Azure Blob Storage
- Azure Speech Services
- Async processing with queues

## 📡 API Usage Examples

### 1. Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=securepass123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
```

### 2. Upload Content

```bash
# Upload YouTube video
curl -X POST http://localhost:8000/api/v1/content/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "source_type=youtube" \
  -F "source_url=https://youtube.com/watch?v=VIDEO_ID" \
  -F "title=My Learning Video"

# Upload PDF
curl -X POST http://localhost:8000/api/v1/content/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "source_type=pdf" \
  -F "title=My Document" \
  -F "file=@document.pdf"
```

### 3. Start Learning Session

```bash
# Create session
curl -X POST http://localhost:8000/api/v1/learning/session \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_name": "Morning Study"}'

# Start viewing a chunk
curl -X POST http://localhost:8000/api/v1/learning/session/1/chunk/5 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. WebSocket Connection (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/learning/session/1/ws');

// Send attention update
ws.send(JSON.stringify({
  type: 'attention_update',
  data: {
    chunk_id: 5,
    focus_score: 85.5,
    timestamp: 120.5
  }
}));

// Receive adjustments
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Manual Testing

Use the interactive API docs at http://localhost:8000/docs

## 📊 Database Management

### View Database

```bash
# SQLite
sqlite3 data/adhd_learning.db
.tables
.schema users
SELECT * FROM users;
```

### Reset Database (Development Only)

```python
from app.core.database import reset_db
reset_db()  # WARNING: Deletes all data!
```

### Migrations (Alembic)

```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head
```

## 🐛 Troubleshooting

### Common Issues

**1. "ANTHROPIC_API_KEY not configured"**
```bash
# Add to .env file
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**2. "FFmpeg not found"**
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

**3. "Database connection error"**
```bash
# Check DATABASE_URL in .env
# For local: sqlite:///./data/adhd_learning.db
# For Azure: postgresql://user:pass@host/db
```

**4. "Module not found"**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**5. "Port 8000 already in use"**
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill
```

## 🔄 Connecting to Next.js Frontend

### Backend CORS Setup
Already configured in `main.py`:
```python
CORS_ORIGINS = ["http://localhost:3000"]
```

### Frontend API Client (Next.js)

```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = {
  async login(email: string, password: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });
    
    return res.json();
  },
  
  async uploadContent(token: string, file: File, type: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_type', type);
    
    const res = await fetch(`${API_URL}/content/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    
    return res.json();
  }
};
```

## 📈 Performance Tips

### 1. Use Connection Pooling (Production)
```python
# In config.py for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 2. Enable Caching
```bash
pip install redis
```

### 3. Use Async Workers
```bash
# Start with multiple workers
uvicorn app.main:app --workers 4
```

### 4. Background Processing
Already configured - uses BackgroundTasks for:
- Content processing
- Transcription
- AI chunking

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY .env .env

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t adhd-backend .
docker run -p 8000:8000 --env-file .env adhd-backend
```

### Azure Container Apps

```bash
# Login
az login

# Create resource group
az group create --name adhd-learning-rg --location eastus

# Deploy
az containerapp up \
  --name adhd-learning-api \
  --resource-group adhd-learning-rg \
  --location eastus \
  --source .
```

## 📝 Next Steps

1. ✅ Backend is running
2. 🎨 Connect your Next.js frontend
3. 🤖 Test AI chunking with real content
4. 📊 Build analytics dashboard
5. 🚀 Deploy to Azure for Imagine Cup

## 🆘 Support

- **Documentation**: http://localhost:8000/docs
- **GitHub Issues**: For bug reports
- **API Testing**: Use Postman or Thunder Client

---

**Ready to build something amazing! 🎓✨**