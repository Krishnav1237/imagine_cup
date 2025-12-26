# FocusSprint Backend Testing Guide

## Quick Start

### 1. Prerequisites
```bash
# macOS dependencies
brew install python@3.11 ffmpeg

# Navigate to backend
cd /Users/HP/imagine_cup/FocusSprint/backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup
Create `.env` file in backend folder:
```bash
# Required
SECRET_KEY="your-secret-key-here-make-it-long"

# Optional: VLM for visual context (GPT-4V)
OPENAI_API_KEY="sk-..."

# Optional: Azure OpenAI
AZURE_OPENAI_API_KEY="..."
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
```

### 3. Initialize Database
```bash
python3 -c "from app.core.database import init_db; init_db()"
```

### 4. Start Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

---

## Testing Each Feature

### Authentication

#### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

#### Login & Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

Save the access_token:
```bash
export TOKEN="eyJ..."
```

#### Get Profile
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

### Content Management

#### Upload PDF
```bash
curl -X POST http://localhost:8000/api/v1/content/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=My Learning Document"
```

#### Upload YouTube URL
```bash
curl -X POST http://localhost:8000/api/v1/content/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "youtube",
    "source_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "title": "My YouTube Video"
  }'
```

#### List Content (Library)
```bash
curl http://localhost:8000/api/v1/content/library \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Content Details
```bash
curl http://localhost:8000/api/v1/content/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### Delete Content
```bash
curl -X DELETE http://localhost:8000/api/v1/content/1 \
  -H "Authorization: Bearer $TOKEN"
```

---

### Chunk Completion (Sprint)

#### Complete a Chunk
```bash
curl -X POST http://localhost:8000/api/v1/content/1/chunks/1/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quiz_score": 85,
    "average_attention": 78,
    "time_spent_seconds": 300
  }'
```

Expected response includes:
- `coins_earned` with reward breakdown
- `streak` info (current, longest)
- `milestone` if achieved
- `break_suggestion` if needed
- `encouragement` message

---

### Gamification

#### Get User Coins & Streak
```bash
curl http://localhost:8000/api/v1/gamification/user/coins \
  -H "Authorization: Bearer $TOKEN"
```

#### Freeze Streak (50 coins)
```bash
curl -X POST http://localhost:8000/api/v1/gamification/user/streak/freeze \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Milestones
```bash
curl http://localhost:8000/api/v1/gamification/user/milestones \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Shop Items
```bash
curl http://localhost:8000/api/v1/gamification/shop/items \
  -H "Authorization: Bearer $TOKEN"
```

#### Purchase Item
```bash
curl -X POST http://localhost:8000/api/v1/gamification/shop/purchase/avatar_cosmic \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Inventory
```bash
curl http://localhost:8000/api/v1/gamification/user/inventory \
  -H "Authorization: Bearer $TOKEN"
```

#### Equip Item
```bash
curl -X POST http://localhost:8000/api/v1/gamification/user/inventory/1/equip \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Leaderboard
```bash
curl http://localhost:8000/api/v1/gamification/leaderboard \
  -H "Authorization: Bearer $TOKEN"
```

---

### ADHD Learning Features

#### Focus Recovery Context
```bash
curl http://localhost:8000/api/v1/adhd-learning/content/1/recovery \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Context recap, refresher quiz, encouragement based on time away.

#### Smart Timestamps (Jump Points)
```bash
curl http://localhost:8000/api/v1/adhd-learning/content/1/timestamps \
  -H "Authorization: Bearer $TOKEN"
```

Expected: List of chunks with timestamps, visual hints, completion status.

#### Report Attention Loss
```bash
curl -X POST http://localhost:8000/api/v1/adhd-learning/session/attention-alert \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": 1,
    "chunk_id": 1,
    "attention_level": 30,
    "time_distracted_seconds": 45,
    "session_duration_seconds": 1500
  }'
```

Expected: Welcome back message, break suggestion, quick recap.

#### Difficulty Recommendation
```bash
curl http://localhost:8000/api/v1/adhd-learning/user/difficulty-recommendation \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Recommended difficulty, reasoning, performance analysis.

#### Submit Difficulty Feedback
```bash
curl -X POST http://localhost:8000/api/v1/adhd-learning/user/difficulty-feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content_id": 1, "was_too_hard": true}'
```

#### Progressive Disclosure Content
```bash
curl "http://localhost:8000/api/v1/adhd-learning/content/1/progressive-disclosure?chunk_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Content split into revealable units with timing info.

---

### Analytics

#### Get User Progress
```bash
curl http://localhost:8000/api/v1/analytics/progress \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Content Analytics
```bash
curl http://localhost:8000/api/v1/analytics/content/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### Get ADHD Insights
```bash
curl http://localhost:8000/api/v1/analytics/adhd-insights \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Peak focus hours, trends, personalized recommendations.

---

## Automated Test Flow

### Full User Journey Script
```bash
#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

# 1. Register
echo "=== Registering user ==="
curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@test.com","password":"demo123","full_name":"Demo User"}'

# 2. Login
echo "\n=== Logging in ==="
RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@test.com&password=demo123")
TOKEN=$(echo $RESPONSE | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. Check coins
echo "\n=== Initial coins ==="
curl -s $BASE_URL/gamification/user/coins -H "Authorization: Bearer $TOKEN"

# 4. Upload content
echo "\n=== Adding YouTube content ==="
curl -s -X POST $BASE_URL/content/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_type":"youtube","source_url":"https://youtu.be/test","title":"Test Video"}'

# 5. Get library
echo "\n=== Library ==="
curl -s $BASE_URL/content/library -H "Authorization: Bearer $TOKEN"

echo "\n=== Tests complete ==="
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Database errors | Delete `focussprint.db` and reinitialize |
| Token expired | Login again to get new token |
| ffmpeg not found | Install: `brew install ffmpeg` |
| VLM not working | Check OPENAI_API_KEY is set correctly |

---

## Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```
