# FocusSprint 🚀

> An AI-powered ADHD-focused learning platform that transforms passive content into active micro-sprints with eye-tracking accountability and gamification.

[![Next.js](https://img.shields.io/badge/Next.js-15.3.6-black)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0.0-blue)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)

---

## 🎯 What is FocusSprint?

FocusSprint is a productivity app designed for people with ADHD/ADD that converts long-form educational content (YouTube videos, PDFs, presentations) into bite-sized 5-minute learning "sprints" with built-in accountability and rewards.

### Core Features

- **🧠 AI Content Metabolizer**: Automatically chunks any learning content into concept-based micro-sprints
- **👁️ Digital Body Double**: Camera-based eye-tracking that pauses content when you look away (privacy-first, local processing)
- **🎨 Visual Lock-In**: AI-generated infographic cards after each sprint for better memory retention
- **🎮 Dopamine Economy**: Earn Focus Coins, collect pets that evolve based on what you study, and build a knowledge card collection
- **📊 Progress Tracking**: GitHub-style activity heatmap, streak tracking, and detailed analytics

---

## 🏗️ Architecture

### Frontend (Next.js)
```
src/
├── app/                    # Next.js 15 App Router
│   ├── page.tsx            # Landing page
│   ├── dashboard/          # Main user hub
│   ├── upload/             # Content upload
│   ├── sprint/             # Active learning session
│   ├── session-end/        # Post-sprint summary
│   ├── shop/               # Focus Coins marketplace
│   ├── profile/            # User stats
│   ├── knowledge-bank/     # Saved infographics
│   └── [other pages]/
├── components/             # Reusable components
│   └── ui/                 # shadcn/ui components (53 total)
└── lib/                    # Utilities & context
```

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py             # FastAPI application
│   ├── api/v1/             # API endpoints
│   │   ├── auth.py         # Authentication
│   │   ├── content.py      # Content processing
│   │   └── analytics.py    # User analytics
│   ├── services/           # Business logic
│   │   ├── content_processor.py
│   │   ├── youtube_downloader.py
│   │   ├── pdf_processor.py
│   │   ├── adaptive_engine.py
│   │   └── chunking/       # AI chunking service
│   └── models/             # Database models
└── requirements.txt
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+ and npm
- Python 3.9+
- (Optional) Anthropic API key for AI features

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:3000
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy .env.example to .env and add your API keys)
cp .env.example .env

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

---

## 📦 Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router) with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: Radix UI + shadcn/ui
- **Animations**: Framer Motion
- **State Management**: React Context API
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLAlchemy
- **AI Services**:
  - Anthropic Claude (content chunking)
  - OpenAI Whisper (transcription)
  - Image generation APIs (infographics)
- **Content Processing**:
  - yt-dlp (YouTube downloads)
  - pdfplumber (PDF parsing)
  - python-pptx (PowerPoint processing)

---

## 🎮 How It Works

### The Focus Loop

1. **📥 Input**: Upload YouTube URL, PDF, or presentation
2. **🤖 AI Processing**: Content is chunked into 5-minute semantic sprints
3. **🎯 Sprint**: Start learning with eye-tracking accountability
4. **🎨 Lock-In**: View AI-generated infographic + quick quiz
5. **🪙 Reward**: Earn Focus Coins, build streaks, evolve pets

### Eye-Tracking Accountability

- Camera activates locally (no video sent to server)
- Look away for 5+ seconds → content pauses and blurs
- Gentle nudge back to focus without judgment
- Privacy-first: only boolean "looking/not looking" state transmitted

### Gamification System

**Focus Coins Economy:**
- Base: 50 coins per sprint
- Perfect focus (90%+): +25 bonus
- Streak multiplier (3+ days): 2x
- Quiz correct: +10 bonus

**Spend coins on:**
- Avatars (200-500 coins)
- Pet eggs (300-800 coins)
- Card packs (100-250 coins)
- Badges (150-400 coins)

**Pet Evolution:**
- Pets evolve based on what you study
- Biology → Bio-Luminescent Turtle
- Coding → Pixel Glitch Cat
- Physics → Quantum Orb

---

## 📊 Current Status

### ✅ Completed
- [x] Full frontend UI (15 pages)
- [x] Component library (53 UI components)
- [x] Landing page with animations
- [x] Dashboard with activity tracking
- [x] Sprint session UI with timer
- [x] Shop and inventory system
- [x] Knowledge bank interface
- [x] Mock data flows

### 🚧 In Progress
- [ ] Backend API implementation
- [ ] Database integration
- [ ] AI content chunking
- [ ] Eye-tracking with MediaPipe
- [ ] Infographic generation

### 📋 Planned
- [ ] Real authentication (JWT)
- [ ] WebSocket for real-time updates
- [ ] Mobile app (React Native)
- [ ] Social features (leaderboards)
- [ ] Spaced repetition system

---

## 🔐 Security & Privacy

- **Eye-tracking**: 100% local processing, no video frames stored or transmitted
- **Data**: Minimal collection, GDPR-compliant
- **Authentication**: JWT tokens with secure password hashing
- **API**: CORS configured, input validation with Pydantic

---

## 📚 Documentation

- **[Complete Code Explanation](/.gemini/antigravity/brain/7ecec822-b551-4b48-8279-625f3485182b/code_explanation.md)**: Detailed technical documentation
- **[Backend Implementation Guide](/BACKEND_IMPLEMENTATION_GUIDE.md)**: API specifications and database schema
- **[System Architecture](/FocusFlow_System_Architecture.md)**: High-level architecture overview
- **[Backend README](/backend/README.md)**: Backend-specific documentation

---

## 🛠️ Development

### Available Scripts

**Frontend:**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

**Backend:**
```bash
uvicorn app.main:app --reload    # Development server
pytest                            # Run tests
alembic upgrade head              # Run migrations
```

### Project Structure

- **`/src`**: Frontend source code
- **`/backend`**: FastAPI backend
- **`/public`**: Static assets
- **`/components.json`**: shadcn/ui configuration

---

## 🤝 Contributing

This is a Microsoft Imagine Cup entry project. Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Microsoft Imagine Cup Entry - Educational Project

---

## 🆘 Support

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **Issues**: GitHub Issues
- **Email**: [Your contact email]

---

## 🎯 Design Philosophy

1. **ADHD-First**: Every feature designed to work with distracted minds, not against them
2. **Micro-Wins**: Break everything into tiny, achievable goals
3. **External Accountability**: Camera as "digital body double" without social anxiety
4. **Visual Memory**: Dual-coding theory with AI-generated infographics
5. **Dopamine-Friendly**: Gamification that motivates without manipulation
6. **Privacy-First**: Local processing, minimal data collection, user control

---

**Built with ❤️ for the ADHD community**

*Turn overwhelm into micro-wins. One sprint at a time.*
