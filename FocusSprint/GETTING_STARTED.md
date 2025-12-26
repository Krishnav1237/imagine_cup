# FocusSprint - Getting Started Guide

Complete guide to run and test the platform locally.

---

## Prerequisites

- **Node.js** 18+ ([download](https://nodejs.org))
- **Python** 3.10+ ([download](https://python.org))
- **Ollama** (optional, for local LLM) ([download](https://ollama.ai))

---

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd FocusSprint/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migration (run once)
sqlite3 focussprint.db "ALTER TABLE users ADD COLUMN preferences TEXT DEFAULT '{}'; ALTER TABLE users ADD COLUMN onboarding_completed INTEGER DEFAULT 0;"

# Start backend server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`  
API docs at: `http://localhost:8000/docs`

---

### 2. Frontend Setup

```bash
# Navigate to frontend (new terminal)
cd FocusSprint

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

### 3. (Optional) Ollama for Local LLM

```bash
# Install Ollama, then:
ollama pull llama3:8b-instruct-q4_K_M

# Ollama should auto-start, or run:
ollama serve
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

**Required for full features:**
- `OPENAI_API_KEY` - For VLM visual analysis (optional)
- `SECRET_KEY` - JWT authentication (generate random string)

---

## Test Flow

### Step 1: Register/Login
1. Open http://localhost:3000
2. Click "Get Started" → Register with email/password
3. Complete onboarding (select age, style, session length)

### Step 2: Upload Content
1. Go to Dashboard → Click "Add Content"
2. Try uploading:
   - YouTube URL (any educational video)
   - PDF document
   - PowerPoint file

### Step 3: Start a Sprint
1. Click "Start Sprint" on any completed content
2. You'll see:
   - **Micro-commitment prompt** ("Quick session" vs "Full session")
   - **Visual countdown timer**
   - **Content display modes** (toggle between Text/Visual/Cards/Audio)

### Step 4: Test Focus Features
- **Hyperfocus Guard**: Work for 45+ min → forced break appears
- **Attention Overlay**: Stay inactive 5+ sec → blur overlay
- **Frustration Detection**: Click rapidly → intervention suggestion
- **Mystery Rewards**: Complete chunks → random tier rewards

### Step 5: Settings Page
1. Go to Settings (gear icon)
2. Toggle features on/off
3. Change age group → theme adapts
4. Enable/disable gamification

---

## Test Checklist

| Feature | How to Test | Expected |
|---------|-------------|----------|
| Onboarding | Register new account | 6-step flow appears |
| Age themes | Change age in Settings | Colors/style change |
| Visual modes | Toggle modes in Sprint | Text/Visual/Cards/Audio |
| Micro-commit | Start sprint | "Quick session" prompt |
| Timer | During sprint | Shrinking circle countdown |
| Rewards | Complete a chunk | Coin animation + tier reveal |
| Settings | Toggle any feature | Instant save + "Saved" indicator |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot find module" | Run `npm install` in frontend |
| Backend won't start | Check Python version, install deps |
| Database error | Delete `focussprint.db`, restart backend |
| Content stuck "Processing" | Check Ollama is running |
| No rewards showing | Ensure gamification enabled in Settings |

---

## API Endpoints (Key)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Get JWT token |
| `/api/v1/content/` | GET | List user content |
| `/api/v1/content/upload` | POST | Upload new content |
| `/api/v1/preferences` | GET/PATCH | User preferences |
| `/api/v1/gamification/stats` | GET | Coins, streaks |

Full API docs: http://localhost:8000/docs

---

## Tech Stack

- **Frontend**: Next.js 14, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **AI**: Ollama (local), OpenAI (cloud)
- **Database**: SQLite (dev), PostgreSQL (prod)

---

## Support

Having issues? Check:
1. `backend/TESTING_GUIDE.md` - Detailed API testing
2. `ADHD_FEATURES.md` - Focus feature documentation
3. `UNIVERSAL_PLATFORM.md` - Platform architecture
