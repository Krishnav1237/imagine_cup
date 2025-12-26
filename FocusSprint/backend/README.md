# ADHD Learning Platform - Backend

FastAPI backend for the ADHD Learning Platform with hybrid local/Azure deployment support.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip or poetry
- (Optional) Azure account for production deployment

### Installation

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run database migrations** (first time only)
```bash
python -c "from app.core.database import init_db; init_db()"
```

5. **Start the server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── content.py       # Content management
│   │       ├── learning.py      # Learning sessions
│   │       └── analytics.py     # Progress analytics
│   ├── core/
│   │   ├── database.py          # Database connection
│   │   └── auth.py              # Auth utilities
│   ├── models/
│   │   └── models.py            # SQLAlchemy models
│   ├── schemas/
│   │   └── schemas.py           # Pydantic schemas
│   ├── services/
│   │   ├── storage/             # Storage adapters
│   │   ├── transcription/       # Audio transcription
│   │   ├── chunking/            # AI chunking service
│   │   └── queue/               # Task queue
│   ├── config.py                # Configuration
│   └── main.py                  # FastAPI app
├── tests/                       # Test files
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🔧 Configuration

### Deployment Modes

#### Local Mode (Development)
- SQLite database
- Local file storage
- Whisper for transcription
- Synchronous processing

```bash
DEPLOYMENT_MODE=local
ANTHROPIC_API_KEY=your-key-here
```

#### Azure Mode (Production)
- PostgreSQL database
- Azure Blob Storage
- Azure Speech Services
- Async processing with Azure Functions

```bash
DEPLOYMENT_MODE=azure
ANTHROPIC_API_KEY=your-key
AZURE_DB_SERVER=your-server.postgres.database.azure.com
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_SPEECH_KEY=...
```

## 🎯 Key Features

### 1. Authentication
- JWT-based authentication
- User registration and login
- Secure password hashing
- Token refresh

### 2. Content Processing
- YouTube video upload
- PDF document processing
- PowerPoint presentation processing
- Automatic transcription
- AI-powered chunking

### 3. Adaptive Learning
- Real-time attention tracking
- Dynamic chunk adjustment
- Personalized difficulty
- Progress analytics

### 4. Storage Abstraction
- Adapter pattern for storage
- Easy switch between local/Azure
- No business logic changes needed

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me/preferences` - Update preferences

### Content
- `POST /api/v1/content/upload` - Upload content
- `GET /api/v1/content/` - List user's content
- `GET /api/v1/content/{id}` - Get content details
- `DELETE /api/v1/content/{id}` - Delete content

### Learning
- `POST /api/v1/learning/session` - Start learning session
- `GET /api/v1/learning/session/{id}` - Get session details
- `WS /api/v1/learning/session/{id}/ws` - WebSocket for real-time updates
- `POST /api/v1/learning/session/{id}/complete` - Complete session

### Analytics
- `GET /api/v1/analytics/progress` - User progress
- `GET /api/v1/analytics/content/{id}` - Content analytics

## 🧪 Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## 🐳 Docker Deployment

```bash
docker build -t adhd-learning-backend .
docker run -p 8000:8000 --env-file .env adhd-learning-backend
```

## 🚢 Azure Deployment

1. **Set up Azure resources**
   - PostgreSQL database
   - Blob Storage account
   - Speech Services
   - Container Apps

2. **Configure environment**
```bash
DEPLOYMENT_MODE=azure
# Add all Azure credentials
```

3. **Deploy**
```bash
az containerapp up --name adhd-learning-api --source .
```

## 🔐 Security

- All passwords are hashed with bcrypt
- JWT tokens for authentication
- CORS configured for frontend
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy ORM

## 📊 Database Schema

- **users** - User accounts and preferences
- **content_items** - Uploaded content
- **content_chunks** - AI-generated chunks
- **learning_sessions** - Learning session tracking
- **session_chunks** - Individual chunk progress

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request

## 📝 License

Microsoft Imagine Cup Entry

## 🆘 Support

For issues or questions:
- GitHub Issues
- Documentation: http://localhost:8000/docs