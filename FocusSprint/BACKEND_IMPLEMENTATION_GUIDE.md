# FocusSprint Backend Implementation Guide

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [Current Frontend Implementation](#current-frontend-implementation)
3. [Backend Architecture Requirements](#backend-architecture-requirements)
4. [API Endpoints Specification](#api-endpoints-specification)
5. [Database Schema](#database-schema)
6. [AI/ML Integration Requirements](#aiml-integration-requirements)
7. [API Integration Points in Frontend](#api-integration-points-in-frontend)
8. [Security & Privacy Considerations](#security--privacy-considerations)
9. [Implementation Timeline](#implementation-timeline)

---

## Executive Summary

**FocusSprint** is an AI-powered productivity app that transforms passive learning content into active, bite-sized "sprints" designed to combat executive dysfunction, particularly for users with ADHD/ADD.

### Core Value Proposition
- **Input Agnostic**: Accepts YouTube URLs, PDFs, PowerPoints, and other learning content
- **AI-Powered Chunking**: Breaks content into 5-minute semantic "micro-sprints"
- **Computer Vision Accountability**: Uses front-camera eye tracking to maintain focus
- **Gamified Economy**: "Focus Coins" system with pets, avatars, and collectibles
- **Visual Memory Anchors**: AI-generated infographics after each sprint

---

## Current Frontend Implementation

### ✅ What's Already Built

#### 1. **Pages & Routes**
| Route | Purpose | Status |
|-------|---------|--------|
| `/` | Landing page with concept explanation | ✅ Complete |
| `/signup` | User registration | ✅ UI Complete |
| `/signin` | User authentication | ✅ UI Complete |
| `/dashboard` | Main hub with activity tracking | ✅ Complete |
| `/upload` | Content upload interface | ✅ UI Complete |
| `/sprint` | Active learning session | ✅ Complete |
| `/session-end` | Post-session summary | ✅ Complete |
| `/shop` | Focus Coins marketplace | ✅ Complete |
| `/profile` | User profile & stats | ✅ UI Complete |
| `/knowledge-bank` | Saved infographics collection | ✅ UI Complete |

#### 2. **Core Features Implemented**
- ✅ **User Context Management**: Client-side state with localStorage
- ✅ **Sprint Timer System**: 5-minute countdown with pause/resume
- ✅ **Mock Eye Tracking UI**: Visual feedback for "looking/not looking" states
- ✅ **Infographic Display**: UI for showing AI-generated summary cards
- ✅ **Quiz System**: Multiple-choice questions after each sprint
- ✅ **Focus Coins Economy**: Earning, spending, purchasing items
- ✅ **Inventory System**: Avatars, pets, badges, card collections
- ✅ **Streak Tracking**: Multiplier system for consecutive sprints
- ✅ **GitHub-Style Activity Heatmap**: Visual progress tracking

#### 3. **Technology Stack**
```json
{
  "frontend": "Next.js 15 (React 19)",
  "ui_library": "Radix UI + shadcn/ui",
  "styling": "Tailwind CSS",
  "animations": "Framer Motion",
  "state_management": "React Context API",
  "data_persistence": "localStorage (temporary)"
}
```

### ❌ What's Missing (Needs Backend)

1. **Real Authentication**: Currently mock-based
2. **Content Processing**: Mock data instead of actual AI chunking
3. **Eye Tracking**: UI exists but no actual MediaPipe integration
4. **Infographic Generation**: Placeholder images instead of AI-generated
5. **Database Persistence**: Everything is localStorage-based
6. **Real-time Syncing**: No cloud backup of user progress
7. **API Layer**: No backend communication

---

## Backend Architecture Requirements

### Recommended Stack

```yaml
Runtime: Node.js (Express/Fastify) OR Python (FastAPI/Django)
Database: PostgreSQL + Redis (caching)
File Storage: AWS S3 / Google Cloud Storage
AI Services: 
  - OpenAI GPT-4o (content chunking)
  - Whisper API (video transcription)
  - Vertex AI Imagen / Nano Banana (infographic generation)
Real-time: Socket.io OR Server-Sent Events
Auth: JWT + OAuth2 (Google/GitHub)
Deployment: Docker + Kubernetes OR Serverless (AWS Lambda/Cloud Functions)
```

### System Architecture Diagram

```
┌─────────────────┐
│   Next.js App   │
│   (Frontend)    │
└────────┬────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
┌────────▼────────┐                     ┌──────────▼──────────┐
│   API Gateway   │                     │  WebSocket Server   │
│  (REST/GraphQL) │                     │  (Real-time focus)  │
└────────┬────────┘                     └──────────┬──────────┘
         │                                         │
         ├──────────┬──────────┬──────────────────┤
         │          │          │                  │
┌────────▼────┐ ┌──▼──────┐ ┌─▼────────────┐  ┌──▼──────────┐
│   Auth      │ │ Content │ │  Gamification│  │   User      │
│   Service   │ │ Service │ │   Service    │  │   Service   │
└─────────────┘ └────┬────┘ └──────────────┘  └─────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌────▼────┐ ┌───▼──────┐
    │ OpenAI  │ │ Whisper │ │  Imagen  │
    │  GPT-4  │ │   API   │ │   API    │
    └─────────┘ └─────────┘ └──────────┘
         
         ┌────────────────────────────┐
         │     PostgreSQL Database    │
         │  ┌──────────┬────────────┐ │
         │  │  Users   │  Content   │ │
         │  ├──────────┼────────────┤ │
         │  │ Sprints  │ Inventory  │ │
         │  └──────────┴────────────┘ │
         └────────────────────────────┘
```

---

## API Endpoints Specification

### 1. Authentication Service

#### `POST /api/auth/register`
**Purpose**: Create new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "FocusedLearner",
  "preferences": {
    "targetDailyMinutes": 60,
    "notificationsEnabled": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "user": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "username": "FocusedLearner",
    "focusCoins": 500,
    "createdAt": "2025-12-15T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### `POST /api/auth/login`
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response**: Same as register

#### `GET /api/auth/me`
**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "username": "FocusedLearner",
  "focusCoins": 1250,
  "streak": 7,
  "totalSprintsCompleted": 42,
  "inventory": [...],
  "currentProgress": {...}
}
```

---

### 2. Content Processing Service

#### `POST /api/content/process`
**Purpose**: Upload and chunk content into sprints

**Request Body** (YouTube):
```json
{
  "type": "youtube",
  "url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
  "userId": "usr_abc123",
  "targetSprintDuration": 300
}
```

**Request Body** (PDF):
```json
{
  "type": "pdf",
  "fileUpload": "<multipart/form-data>",
  "userId": "usr_abc123",
  "targetSprintDuration": 300
}
```

**Backend Processing Steps**:
1. **YouTube**: 
   - Extract video using `yt-dlp` or YouTube API
   - Transcribe audio using OpenAI Whisper
   - Extract metadata (title, duration, thumbnail)

2. **PDF**: 
   - Parse PDF using `PyPDF2` or `pdfplumber`
   - Extract text and images
   - Chunk by pages/sections

3. **AI Chunking**:
   ```python
   # Pseudo-code for GPT-4 chunking
   prompt = f"""
   You are an ADHD-friendly content analyzer. Break this transcript into semantic "micro-sprints."
   
   Rules:
   - Each sprint = 5 minutes of content
   - Focus on ONE core concept per sprint
   - Create engaging titles (not just "Part 1")
   - Include 3-5 key points per sprint
   - End with a natural pause point
   
   Transcript:
   {transcript_text}
   
   Output JSON format:
   {{
     "sprints": [
       {{
         "sprintNumber": 1,
         "concept": "Variables & Data Types",
         "startTime": 0,
         "endTime": 300,
         "keyPoints": ["...", "...", "..."],
         "summary": "..."
       }}
     ]
   }}
   """
   ```

**Response**:
```json
{
  "success": true,
  "contentId": "cnt_xyz789",
  "totalSprints": 12,
  "estimatedTime": 3600,
  "metadata": {
    "title": "Introduction to Python Programming",
    "source": "YouTube",
    "thumbnail": "https://img.youtube.com/vi/...",
    "contentType": "youtube"
  },
  "sprints": [
    {
      "id": "spr_001",
      "sprintNumber": 1,
      "concept": "Variables & Data Types",
      "duration": 300,
      "startTimestamp": 0,
      "endTimestamp": 300,
      "summary": "Learn about Python's core data types...",
      "keyPoints": [
        "Integers and floats",
        "String manipulation",
        "Type conversion"
      ],
      "videoSegmentUrl": "https://cdn.focussprint.app/segments/xyz_001.mp4",
      "transcript": "Welcome to Python! Today we'll..."
    }
  ]
}
```

**Database Storage**:
```sql
INSERT INTO content (user_id, title, type, source_url, total_sprints, created_at)
VALUES ('usr_abc123', 'Intro to Python', 'youtube', 'https://...', 12, NOW());

INSERT INTO sprints (content_id, sprint_number, concept, duration, ...)
VALUES ('cnt_xyz789', 1, 'Variables & Data Types', 300, ...);
```

---

### 3. Sprint Session Service

#### `POST /api/sessions/start`
**Purpose**: Begin a sprint session

**Request Body**:
```json
{
  "userId": "usr_abc123",
  "sprintId": "spr_001",
  "contentId": "cnt_xyz789"
}
```

**Response**:
```json
{
  "sessionId": "ses_456",
  "sprint": {
    "id": "spr_001",
    "concept": "Variables & Data Types",
    "videoUrl": "https://cdn.focussprint.app/segments/xyz_001.mp4",
    "duration": 300
  },
  "websocketUrl": "wss://api.focussprint.app/sessions/ses_456"
}
```

#### WebSocket Events (`wss://api.focussprint.app/sessions/{sessionId}`)

**Client → Server**:
```json
// Focus state updates (from eye tracking)
{
  "event": "focus_update",
  "isLooking": true,
  "timestamp": 1702645200000
}

// Pause request
{
  "event": "pause",
  "timeElapsed": 150
}
```

**Server → Client**:
```json
// Real-time focus stats
{
  "event": "stats_update",
  "focusPercentage": 87.5,
  "distractionCount": 2,
  "timeRemaining": 150
}

// Session complete trigger
{
  "event": "session_complete",
  "focusTime": 262,
  "totalTime": 300
}
```

#### `POST /api/sessions/complete`
**Purpose**: Finalize sprint and calculate rewards

**Request Body**:
```json
{
  "sessionId": "ses_456",
  "focusTime": 262,
  "totalTime": 300,
  "distractionCount": 2,
  "completed": true
}
```

**Backend Calculation**:
```python
focus_percentage = (focus_time / total_time) * 100
base_coins = 50

# Bonus for high focus
if focus_percentage >= 90:
    base_coins += 25

# Streak multiplier
if user.current_streak >= 2:
    base_coins *= 2

# Quiz bonus (if answered correctly)
if quiz_correct:
    base_coins += 10
```

**Response**:
```json
{
  "success": true,
  "coinsEarned": 100,
  "streakIncremented": true,
  "newStreak": 3,
  "newBalance": 1350,
  "nextSprintAvailable": true,
  "infographic": {
    "id": "inf_789",
    "imageUrl": "https://cdn.focussprint.app/infographics/inf_789.png",
    "concept": "Variables & Data Types",
    "keyPoints": [...],
    "quiz": {
      "question": "Which data type is mutable in Python?",
      "options": ["String", "List", "Integer", "Float"],
      "correctAnswer": 1
    }
  }
}
```

---

### 4. Infographic Generation Service

#### `POST /api/infographics/generate`
**Purpose**: Create visual summary of sprint content

**Request Body**:
```json
{
  "sprintId": "spr_001",
  "transcript": "Full sprint transcript...",
  "concept": "Variables & Data Types",
  "keyPoints": ["Integers and floats", "String manipulation", "Type conversion"]
}
```

**Backend Processing**:
```python
# Step 1: Create text layout using GPT-4
layout_prompt = f"""
Create an infographic layout for this concept: {concept}

Key Points:
{keyPoints}

Generate a structured layout with:
1. Main title (short, catchy)
2. 3-4 visual sections
3. Icons/symbols for each section
4. Color scheme recommendation

Output JSON with exact text and positioning.
"""

# Step 2: Generate image using Imagen/Nano Banana
image_prompt = f"""
Modern, minimalist educational infographic about "{concept}".
Layout: {layout_from_gpt}
Style: Clean, high contrast, ADHD-friendly
Colors: Dark background, neon accents
Text: Large, legible font, maximum 3 colors
"""

# Step 3: Add text overlay (if API doesn't support text)
# Use Pillow/ImageMagick to composite text on generated image
```

**Response**:
```json
{
  "infographicId": "inf_789",
  "imageUrl": "https://cdn.focussprint.app/infographics/inf_789.png",
  "thumbnailUrl": "https://cdn.focussprint.app/infographics/inf_789_thumb.png",
  "generatedAt": "2025-12-15T10:30:00Z",
  "metadata": {
    "concept": "Variables & Data Types",
    "style": "minimalist",
    "colorScheme": ["#ff6b4a", "#7c3aed", "#f59e0b"]
  }
}
```

---

### 5. Gamification Service

#### `GET /api/shop/items`
**Response**:
```json
{
  "items": [
    {
      "id": "itm_pet_001",
      "name": "Phoenix Egg",
      "type": "pet",
      "rarity": "Epic",
      "price": 300,
      "imageUrl": "https://cdn.focussprint.app/shop/phoenix_egg.png",
      "description": "Hatches after completing 10 sprints",
      "requirements": {
        "minSprints": 5
      }
    }
  ]
}
```

#### `POST /api/shop/purchase`
**Request**:
```json
{
  "userId": "usr_abc123",
  "itemId": "itm_pet_001"
}
```

**Response**:
```json
{
  "success": true,
  "newBalance": 1050,
  "item": {
    "id": "inv_123",
    "itemId": "itm_pet_001",
    "purchasedAt": "2025-12-15T11:00:00Z",
    "status": "egg",
    "hatchProgress": 0
  }
}
```

#### `GET /api/user/inventory`
**Response**:
```json
{
  "inventory": [
    {
      "id": "inv_123",
      "itemId": "itm_pet_001",
      "name": "Phoenix Egg",
      "type": "pet",
      "status": "egg",
      "hatchProgress": 3,
      "hatchRequirement": 10,
      "evolution": null
    }
  ]
}
```

#### Pet Evolution Logic (Backend)
```python
def evolve_pet(user_id, pet_id, completed_sprint):
    pet = get_pet(pet_id)
    sprint = get_sprint(completed_sprint.id)
    
    # Contextual evolution based on content studied
    if 'biology' in sprint.concept.lower():
        pet.evolution_path = 'bio-luminescent-turtle'
    elif 'code' in sprint.concept.lower() or 'programming' in sprint.concept.lower():
        pet.evolution_path = 'pixel-glitch-cat'
    elif 'physics' in sprint.concept.lower():
        pet.evolution_path = 'quantum-orb'
    
    pet.hatch_progress += 1
    
    if pet.hatch_progress >= 10 and pet.status == 'egg':
        pet.status = 'hatched'
        pet.current_form = get_evolution_stage_1(pet.evolution_path)
        notify_user(user_id, f"Your {pet.name} has hatched!")
    
    save_pet(pet)
```

---

### 6. Knowledge Bank Service

#### `GET /api/knowledge-bank`
**Purpose**: Retrieve user's collection of infographics

**Response**:
```json
{
  "cards": [
    {
      "id": "inf_789",
      "concept": "Variables & Data Types",
      "imageUrl": "https://cdn.focussprint.app/infographics/inf_789.png",
      "contentTitle": "Intro to Python",
      "completedAt": "2025-12-15T10:30:00Z",
      "category": "Programming",
      "rarity": "Common"
    }
  ],
  "stats": {
    "totalCards": 42,
    "uniqueConcepts": 35,
    "rarityBreakdown": {
      "Common": 20,
      "Rare": 15,
      "Epic": 5,
      "Legendary": 2
    }
  }
}
```

---

### 7. Analytics Service

#### `GET /api/analytics/dashboard`
**Response**:
```json
{
  "activityHeatmap": {
    "2025-12-01": 3,
    "2025-12-02": 5,
    "2025-12-15": 2
  },
  "stats": {
    "totalFocusMinutes": 1260,
    "averageFocusPercentage": 85.7,
    "longestStreak": 12,
    "currentStreak": 7,
    "totalSprintsCompleted": 252,
    "favoriteCategory": "Programming"
  },
  "recentActivity": [...]
}
```

---

## Database Schema

### PostgreSQL Tables

```sql
-- Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  focus_coins INTEGER DEFAULT 500,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  total_sprints_completed INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Content Table
CREATE TABLE content (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  content_type VARCHAR(20) NOT NULL, -- 'youtube', 'pdf', 'ppt'
  source_url TEXT,
  thumbnail_url TEXT,
  total_sprints INTEGER NOT NULL,
  total_duration INTEGER, -- in seconds
  processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB -- store extra info like video description, author, etc.
);

-- Sprints Table
CREATE TABLE sprints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_id UUID REFERENCES content(id) ON DELETE CASCADE,
  sprint_number INTEGER NOT NULL,
  concept VARCHAR(255) NOT NULL,
  duration INTEGER DEFAULT 300,
  start_timestamp INTEGER, -- video timestamp in seconds
  end_timestamp INTEGER,
  summary TEXT,
  key_points JSONB, -- array of strings
  video_segment_url TEXT,
  transcript TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(content_id, sprint_number)
);

-- Sessions Table (track individual sprint attempts)
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  sprint_id UUID REFERENCES sprints(id) ON DELETE CASCADE,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  focus_time INTEGER, -- seconds actually focused
  total_time INTEGER, -- total session duration
  distraction_count INTEGER DEFAULT 0,
  coins_earned INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  focus_data JSONB -- detailed focus timestamps for analysis
);

-- Infographics Table
CREATE TABLE infographics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id UUID REFERENCES sprints(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  thumbnail_url TEXT,
  concept VARCHAR(255),
  key_points JSONB,
  rarity VARCHAR(20) DEFAULT 'Common', -- gamification element
  generated_at TIMESTAMP DEFAULT NOW(),
  generation_prompt TEXT, -- for debugging/retraining
  metadata JSONB
);

-- Quizzes Table
CREATE TABLE quizzes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sprint_id UUID REFERENCES sprints(id) ON DELETE CASCADE,
  question TEXT NOT NULL,
  options JSONB NOT NULL, -- array of strings
  correct_answer INTEGER NOT NULL, -- index of correct option
  explanation TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Quiz Attempts Table
CREATE TABLE quiz_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  quiz_id UUID REFERENCES quizzes(id) ON DELETE CASCADE,
  user_answer INTEGER,
  is_correct BOOLEAN,
  attempted_at TIMESTAMP DEFAULT NOW()
);

-- Shop Items Table
CREATE TABLE shop_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL,
  type VARCHAR(20) NOT NULL, -- 'avatar', 'pet', 'card', 'badge'
  rarity VARCHAR(20) NOT NULL,
  price INTEGER NOT NULL,
  image_url TEXT NOT NULL,
  description TEXT,
  requirements JSONB, -- e.g., {"minSprints": 10}
  available BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- User Inventory Table
CREATE TABLE user_inventory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  shop_item_id UUID REFERENCES shop_items(id) ON DELETE CASCADE,
  purchased_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'owned', -- 'owned', 'egg', 'hatched', 'evolved'
  hatch_progress INTEGER DEFAULT 0,
  evolution_path VARCHAR(50),
  metadata JSONB, -- custom properties like pet level, evolution stage
  UNIQUE(user_id, shop_item_id)
);

-- User Progress Table (current active content)
CREATE TABLE user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  content_id UUID REFERENCES content(id) ON DELETE SET NULL,
  current_sprint_index INTEGER DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_sprint_id ON sessions(sprint_id);
CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_sprints_content_id ON sprints(content_id);
CREATE INDEX idx_user_inventory_user_id ON user_inventory(user_id);
```

### Redis Cache Strategy

```yaml
# User session data
key: "session:{userId}"
ttl: 3600 # 1 hour
value: { focusCoins, streak, currentProgress }

# Content processing queue
key: "queue:content:processing"
type: list
value: [contentId1, contentId2, ...]

# Real-time sprint stats
key: "sprint:stats:{sessionId}"
ttl: 600 # 10 minutes
value: { focusTime, distractionCount, isActive }

# Shop items cache
key: "shop:items"
ttl: 86400 # 24 hours
value: [all shop items JSON]
```

---

## AI/ML Integration Requirements

### 1. OpenAI GPT-4o Integration

**Purpose**: Content chunking and concept extraction

**System Prompt** (for semantic sprint creation):
```
You are an ADHD-specialized learning architect. Your task is to break down educational content into "micro-sprints" optimized for executive function challenges.

ADHD-Friendly Principles:
1. ONE concept per sprint (no multitasking)
2. Clear start and end points (no ambiguous transitions)
3. Immediate context (no "as we discussed earlier")
4. Action-oriented language (verbs over nouns)
5. Progress milestones every 5 minutes

Input: Full transcript or document text
Output: JSON array of semantic chunks

Each sprint must have:
- Concept: A specific, achievable learning goal (not "Introduction to X")
- Summary: 2-3 sentences explaining what the user will LEARN (not just topics covered)
- KeyPoints: 3-5 bullet points with concrete examples
- StartTime/EndTime: Precise video timestamps OR page numbers
- EngagementHook: One sentence to spark curiosity

Example Good Concept: "Creating Your First Python Variable"
Example Bad Concept: "Python Basics Part 1"

Avoid:
- Vague titles like "Overview" or "Introduction"
- Sprints longer than 6 minutes
- Concept overflow (multiple ideas in one sprint)
```

**API Call Example**:
```python
import openai

def chunk_content(transcript: str, target_duration: int = 300):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Transcript:\n{transcript}"}
        ],
        response_format={"type": "json_object"}
    )
    
    sprints = json.loads(response.choices[0].message.content)
    return sprints
```

---

### 2. OpenAI Whisper Integration

**Purpose**: YouTube video transcription

**API Call**:
```python
import openai

def transcribe_video(audio_file_path: str):
    with open(audio_file_path, "rb") as audio:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio,
            response_format="verbose_json",
            timestamp_granularities=["word"]  # For precise chunking
        )
    return transcript
```

**Output Structure**:
```json
{
  "text": "Full transcript here...",
  "words": [
    {"word": "Welcome", "start": 0.0, "end": 0.5},
    {"word": "to", "start": 0.5, "end": 0.7},
    ...
  ]
}
```

---

### 3. Infographic Generation (Vertex AI Imagen / Nano Banana)

**Option A: Vertex AI Imagen**
```python
from google.cloud import aiplatform

def generate_infographic(concept: str, key_points: list):
    prompt = f"""
    Educational infographic design:
    
    Title: {concept}
    Style: Modern, minimalist, dark mode
    Layout: Vertical 800x1200px
    
    Sections:
    {chr(10).join(f"• {point}" for point in key_points)}
    
    Design Requirements:
    - Large, legible sans-serif font (minimum 24pt)
    - Dark background (#0a0a12)
    - Neon accent colors (#ff6b4a, #7c3aed, #f59e0b)
    - Icons or symbols for each section
    - High contrast for ADHD accessibility
    - Maximum 3 colors + white
    - Clean spacing, no clutter
    """
    
    response = aiplatform.ImageGenerationModel("imagen-3.0").predict(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="9:16"
    )
    
    return response.images[0]  # Base64 or URL
```

**Option B: Nano Banana API** (if using their text-in-image capability)
```python
import requests

def generate_nano_banana_infographic(concept: str, key_points: list):
    payload = {
        "prompt": f"Minimalist educational infographic about {concept}",
        "text_elements": [
            {"content": concept, "position": "top", "size": "large"},
            *[{"content": point, "position": "auto", "size": "medium"} 
              for point in key_points]
        ],
        "style": "dark_modern",
        "aspect_ratio": "9:16"
    }
    
    response = requests.post(
        "https://api.nanobanana.ai/v1/generate",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload
    )
    
    return response.json()["image_url"]
```

---

### 4. Eye Tracking (Google MediaPipe)

**Frontend Implementation** (already has UI, needs actual tracking):

**Where to Add** (`sprint/page.tsx`):
```typescript
import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

useEffect(() => {
  const initializeEyeTracking = async () => {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
    );
    
    const faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath: "face_landmarker.task",
        delegate: "GPU"
      },
      runningMode: "VIDEO",
      numFaces: 1
    });

    // Start video stream
    const video = videoRef.current;
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;

    // Analyze every frame
    const analyzeFrame = () => {
      const landmarks = faceLandmarker.detectForVideo(video, Date.now());
      
      if (landmarks.faceLandmarks.length > 0) {
        const eyeGaze = calculateGazeDirection(landmarks.faceLandmarks[0]);
        const isLookingAtScreen = isGazeWithinBounds(eyeGaze);
        
        setIsLooking(isLookingAtScreen);
        
        // Send to backend via WebSocket
        wsRef.current.send(JSON.stringify({
          event: "focus_update",
          isLooking: isLookingAtScreen,
          timestamp: Date.now()
        }));
      }
      
      requestAnimationFrame(analyzeFrame);
    };
    
    analyzeFrame();
  };

  initializeEyeTracking();
}, []);

function calculateGazeDirection(landmarks) {
  // MediaPipe provides 478 face landmarks
  // Eyes are landmarks 33, 133, 362, 263
  const leftEye = landmarks[33];
  const rightEye = landmarks[263];
  const noseTip = landmarks[1];
  
  // Calculate gaze vector based on pupil position relative to nose
  // (This is simplified - production would use iris landmarks)
  const gazeX = (leftEye.x + rightEye.x) / 2 - noseTip.x;
  const gazeY = (leftEye.y + rightEye.y) / 2 - noseTip.y;
  
  return { x: gazeX, y: gazeY };
}

function isGazeWithinBounds(gaze, threshold = 0.15) {
  // If gaze is within ±15% of center, consider it "looking at screen"
  return Math.abs(gaze.x) < threshold && Math.abs(gaze.y) < threshold;
}
```

**Backend WebSocket Handler**:
```python
# websocket_server.py
async def handle_focus_update(websocket, data):
    session_id = data['sessionId']
    is_looking = data['isLooking']
    
    # Update Redis cache
    await redis.hincrby(f"session:{session_id}", "focusTime" if is_looking else "distractionTime", 1)
    
    # Check for distraction threshold
    distraction_count = await redis.hget(f"session:{session_id}", "distractionCount")
    if distraction_count >= 3:
        await websocket.send(json.dumps({
            "event": "trigger_micro_recap",
            "message": "You've looked away 3 times. Let's refocus!"
        }))
```

---

## API Integration Points in Frontend

### Files to Modify

#### 1. `src/app/signup/page.tsx`
**Current**: Mock signup  
**Change**: 
```typescript
const handleSignup = async (e: FormEvent) => {
  e.preventDefault();
  setLoading(true);

  try {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, username })
    });

    const data = await response.json();
    
    if (data.success) {
      localStorage.setItem('focussprint_token', data.token);
      router.push('/onboarding');
    } else {
      setError(data.message);
    }
  } catch (err) {
    setError('Signup failed. Please try again.');
  } finally {
    setLoading(false);
  }
};
```

---

#### 2. `src/app/upload/page.tsx`
**Current**: Mock content processing (line 17-60)  
**Change**:
```typescript
const handleProcess = async () => {
  if (!input && !file) return;
  setProcessing(true);

  try {
    let response;
    
    if (activeTab === 'youtube') {
      response = await fetch('/api/content/process', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('focussprint_token')}`
        },
        body: JSON.stringify({
          type: 'youtube',
          url: input,
          targetSprintDuration: 300
        })
      });
    } else {
      const formData = new FormData();
      formData.append('file', file!);
      formData.append('type', activeTab);
      
      response = await fetch('/api/content/process', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('focussprint_token')}`
        },
        body: formData
      });
    }

    const data = await response.json();
    
    if (data.success) {
      setProgress({
        currentContentId: data.contentId,
        currentSprintIndex: 0,
        sprints: data.sprints,
        totalSprints: data.totalSprints,
        contentTitle: data.metadata.title,
        contentType: activeTab,
        contentUrl: input || file?.name
      });
      
      router.push('/sprint');
    }
  } catch (error) {
    console.error('Processing failed:', error);
  } finally {
    setProcessing(false);
  }
};
```

---

#### 3. `src/app/sprint/page.tsx`
**Current**: Local timer, mock infographics  
**Changes**:

**A. Session Start (line 45-55)**:
```typescript
useEffect(() => {
  const startSession = async () => {
    const response = await fetch('/api/sessions/start', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('focussprint_token')}`
      },
      body: JSON.stringify({
        sprintId: currentSprint.id,
        contentId: currentProgress.currentContentId
      })
    });
    
    const data = await response.json();
    setSessionId(data.sessionId);
    
    // Connect to WebSocket
    const ws = new WebSocket(data.websocketUrl);
    ws.onmessage = handleWebSocketMessage;
    wsRef.current = ws;
  };
  
  startSession();
}, [currentSprint]);
```

**B. Sprint Complete (line 91-103)**:
```typescript
const handleSprintComplete = async () => {
  setSprintPhase('infographic');
  
  // Close WebSocket
  wsRef.current?.close();
  
  // Finalize session
  const response = await fetch('/api/sessions/complete', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('focussprint_token')}`
    },
    body: JSON.stringify({
      sessionId: sessionId,
      focusTime: focusTime,
      totalTime: sprintDuration,
      distractionCount: distractionCount,
      completed: true
    })
  });
  
  const data = await response.json();
  
  setEarnedCoins(data.coinsEarned);
  setInfographicData(data.infographic); // Use real AI-generated infographic
};
```

---

#### 4. `src/lib/user-context.tsx`
**Current**: localStorage only  
**Change**: Sync with backend

```typescript
// Add API calls to sync state
useEffect(() => {
  const syncWithBackend = async () => {
    const token = localStorage.getItem('focussprint_token');
    if (!token) return;
    
    try {
      const response = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      
      setFocusCoins(data.focusCoins);
      setStreak(data.streak);
      setInventory(data.inventory);
      setCompletedSprints(data.completedSprints);
      setCurrentProgress(data.currentProgress);
    } catch (err) {
      console.error('Sync failed:', err);
    }
  };
  
  syncWithBackend();
}, []);

const addCoins = async (amount: number) => {
  // Optimistic update
  setFocusCoins(prev => prev + amount);
  
  // Sync with backend (happens in session/complete endpoint)
};
```

---

#### 5. `src/app/shop/page.tsx`
**Current**: Mock purchases  
**Change** (line 80-90):
```typescript
const handlePurchase = async (item: typeof SHOP_ITEMS[0]) => {
  if (purchasedItems.has(item.id)) return;
  
  try {
    const response = await fetch('/api/shop/purchase', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('focussprint_token')}`
      },
      body: JSON.stringify({ itemId: item.id })
    });
    
    const data = await response.json();
    
    if (data.success) {
      setFocusCoins(data.newBalance);
      setPurchasedItems(new Set([...purchasedItems, item.id]));
      // Show success toast
    }
  } catch (err) {
    // Show error toast
  }
};
```

---

## Security & Privacy Considerations

### 1. Eye Tracking Privacy
```yaml
Privacy Requirements:
  - All video processing MUST happen client-side (browser)
  - Never upload raw video frames to backend
  - Only send binary focus/distraction events (true/false)
  - MediaPipe models run locally in WebAssembly
  - No facial recognition or identity tracking
  - User must explicitly consent before camera access
```

**Privacy Notice** (add to `/sprint` page):
```
⚠️ Your camera is only used for attention tracking. 
All processing happens locally on your device. 
No images are ever uploaded or stored.
```

### 2. Authentication Security
```yaml
JWT Token:
  - Expiry: 7 days
  - Refresh token: 30 days
  - HttpOnly cookies for refresh tokens
  - CORS: Whitelist only production domain

Rate Limiting:
  - Auth endpoints: 5 requests/minute
  - Content processing: 10 requests/hour
  - Shop purchases: 20 requests/minute
```

### 3. Content Storage
```yaml
User Uploaded Files:
  - Scan for malware (ClamAV or VirusTotal API)
  - Maximum file size: 50MB
  - Allowed types: .pdf, .pptx, .mp4
  - Store in isolated S3 bucket with signed URLs
  - Delete after 30 days of inactivity
```

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up backend server (Node.js/Python)
- [ ] PostgreSQL database + migrations
- [ ] Authentication API (`/auth/*`)
- [ ] User service (`/api/auth/me`)
- [ ] Deploy development environment

### Phase 2: Content Processing (Weeks 3-4)
- [ ] YouTube downloader integration
- [ ] Whisper API transcription
- [ ] GPT-4o content chunking
- [ ] File upload handling (PDF/PPT)
- [ ] S3/Cloud Storage setup
- [ ] `/api/content/process` endpoint

### Phase 3: Sprint Sessions (Week 5)
- [ ] WebSocket server for real-time tracking
- [ ] Session management (`/api/sessions/*`)
- [ ] Redis cache for live session data
- [ ] Focus metrics calculation

### Phase 4: AI Visual Generation (Week 6)
- [ ] Infographic generation (Imagen/Nano Banana)
- [ ] Quiz generation from sprint content
- [ ] `/api/infographics/generate` endpoint
- [ ] CDN setup for image delivery

### Phase 5: Gamification (Week 7)
- [ ] Shop system (`/api/shop/*`)
- [ ] Inventory management
- [ ] Pet evolution logic
- [ ] Achievements/badges system

### Phase 6: Frontend Integration (Week 8)
- [ ] Replace all mock data with API calls
- [ ] Add MediaPipe eye tracking
- [ ] WebSocket client implementation
- [ ] Error handling & loading states

### Phase 7: Testing & Launch (Week 9-10)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security audit
- [ ] Production deployment

---

## Environment Variables

### Backend `.env` File
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/focussprint
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRY=7d
REFRESH_TOKEN_EXPIRY=30d

# OpenAI
OPENAI_API_KEY=sk-...

# Google Cloud (for Imagen)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=focussprint-prod

# Nano Banana (if using)
NANO_BANANA_API_KEY=nb_...

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=focussprint-content
S3_REGION=us-east-1

# Application
NODE_ENV=production
PORT=8080
FRONTEND_URL=https://focussprint.app

# Rate Limiting
RATE_LIMIT_WINDOW=60000  # 1 minute
RATE_LIMIT_MAX_REQUESTS=100
```

### Frontend `.env.local`
```bash
NEXT_PUBLIC_API_URL=https://api.focussprint.app
NEXT_PUBLIC_WS_URL=wss://api.focussprint.app
NEXT_PUBLIC_CDN_URL=https://cdn.focussprint.app
```

---

## API Response Standards

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_COINS",
    "message": "You need 300 Focus Coins to purchase this item",
    "details": {
      "required": 300,
      "current": 250
    }
  }
}
```

### Error Codes
```typescript
enum ErrorCode {
  // Auth
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  USER_NOT_FOUND = 'USER_NOT_FOUND',
  
  // Content
  INVALID_URL = 'INVALID_URL',
  PROCESSING_FAILED = 'PROCESSING_FAILED',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  
  // Sessions
  SESSION_NOT_FOUND = 'SESSION_NOT_FOUND',
  SESSION_ALREADY_COMPLETED = 'SESSION_ALREADY_COMPLETED',
  
  // Shop
  INSUFFICIENT_COINS = 'INSUFFICIENT_COINS',
  ITEM_ALREADY_OWNED = 'ITEM_ALREADY_OWNED',
  ITEM_NOT_FOUND = 'ITEM_NOT_FOUND'
}
```

---

## Testing Checklist

### Backend API Tests
```bash
# Authentication
- [ ] User registration with valid data
- [ ] Duplicate email rejection
- [ ] Password strength validation
- [ ] Login with correct credentials
- [ ] Login with wrong password
- [ ] JWT token validation
- [ ] Token expiry handling

# Content Processing
- [ ] YouTube URL validation
- [ ] Video transcription accuracy
- [ ] Content chunking into 5-min sprints
- [ ] PDF upload and parsing
- [ ] PPT upload and parsing
- [ ] Invalid file type rejection
- [ ] File size limit enforcement

# Sessions
- [ ] Session start creates DB record
- [ ] WebSocket connection establishment
- [ ] Real-time focus updates
- [ ] Session completion calculates correct coins
- [ ] Streak increment on completion
- [ ] Streak reset on skip

# Infographics
- [ ] Image generation from transcript
- [ ] Text legibility in generated images
- [ ] CDN upload and URL return
- [ ] Quiz generation accuracy

# Shop
- [ ] Purchase with sufficient coins
- [ ] Purchase rejection with insufficient coins
- [ ] Duplicate purchase prevention
- [ ] Pet evolution logic
- [ ] Inventory retrieval
```

### Frontend Integration Tests
```bash
- [ ] Signup flow end-to-end
- [ ] Login persists across page refresh
- [ ] Content upload shows loading state
- [ ] Sprint video plays correctly
- [ ] Eye tracking detects look-away
- [ ] Timer pauses on distraction
- [ ] Infographic displays after sprint
- [ ] Quiz submission awards coins
- [ ] Shop purchase updates balance
- [ ] Inventory shows purchased items
```

---

## Deployment Architecture

### Production Stack
```yaml
Frontend:
  Platform: Vercel / Netlify
  Domain: focussprint.app
  CDN: Cloudflare
  
Backend:
  Platform: AWS ECS / Google Cloud Run
  Domain: api.focussprint.app
  Load Balancer: ALB / Cloud Load Balancing
  
Database:
  Primary: AWS RDS PostgreSQL / Cloud SQL
  Cache: AWS ElastiCache Redis / Cloud Memorystore
  
Storage:
  Media: AWS S3 / Google Cloud Storage
  CDN: CloudFront / Cloud CDN
  
Monitoring:
  APM: Datadog / New Relic
  Logs: CloudWatch / Cloud Logging
  Errors: Sentry
```

---

## Contact & Support

For backend implementation questions:
- **Technical Spec Questions**: Refer to this document
- **API Endpoint Clarifications**: Check Postman collection (to be created)
- **Database Schema Changes**: Submit PR with migration script
- **AI Prompt Engineering**: Consult LLM fine-tuning guide (to be created)

---

## Appendix: Sample API Request/Response Flows

### Full User Journey Example

```mermaid
sequenceDiagram
    User->>Frontend: Sign Up
    Frontend->>Backend: POST /api/auth/register
    Backend->>Database: Create user record
    Backend-->>Frontend: { token, user }
    Frontend->>Frontend: Store token
    
    User->>Frontend: Upload YouTube URL
    Frontend->>Backend: POST /api/content/process
    Backend->>YouTube: Download video
    Backend->>Whisper: Transcribe audio
    Backend->>GPT-4: Chunk into sprints
    Backend->>Database: Store content + sprints
    Backend-->>Frontend: { contentId, sprints[] }
    
    User->>Frontend: Start Sprint
    Frontend->>Backend: POST /api/sessions/start
    Backend->>Database: Create session record
    Backend-->>Frontend: { sessionId, websocketUrl }
    Frontend->>WebSocket: Connect
    
    loop Every Second
        Frontend->>WebSocket: { isLooking: true }
        WebSocket->>Redis: Update focus stats
    end
    
    Frontend->>Backend: POST /api/sessions/complete
    Backend->>GPT-4: Generate quiz
    Backend->>Imagen: Generate infographic
    Backend->>S3: Upload image
    Backend->>Database: Update session, add coins
    Backend-->>Frontend: { coinsEarned, infographic }
    
    User->>Frontend: Visit Shop
    Frontend->>Backend: GET /api/shop/items
    Backend->>Database: Fetch shop items
    Backend-->>Frontend: { items[] }
    
    User->>Frontend: Purchase Pet Egg
    Frontend->>Backend: POST /api/shop/purchase
    Backend->>Database: Deduct coins, add to inventory
    Backend-->>Frontend: { success, newBalance, item }
```

---

**Document Version**: 1.0  
**Last Updated**: December 15, 2025  
**Status**: Ready for Backend Team Review
