# FocusSprint Full Stack Testing Guide

## Quick Start - Run Both Frontend & Backend

### Terminal 1: Start Backend
```bash
cd /Users/HP/imagine_cup/FocusSprint/backend

# First time setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -c "from app.core.database import init_db; init_db()"

# Start server
uvicorn app.main:app --reload --port 8000
```
Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Terminal 2: Start Frontend
```bash
cd /Users/HP/imagine_cup/FocusSprint

# First time setup
npm install

# Start dev server
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## Full Stack Test Flow

### 1. Registration & Login

1. Open `http://localhost:3000` in browser
2. Click **Sign Up**
3. Enter:
   - Email: `test@example.com`
   - Password: `testpass123`
   - Name: `Test User`
4. Click Register
5. Login with same credentials
6. ✅ Should see dashboard with 500 Focus Coins

### 2. Content Upload

#### PDF Upload:
1. Navigate to Library/Dashboard
2. Click "Add Content" or "Upload"
3. Select a PDF file
4. Enter title
5. Click Upload
6. ✅ Content should appear with "Processing" status
7. Wait 30-60 seconds
8. ✅ Status should change to "Ready"

#### YouTube Video:
1. Click "Add YouTube"
2. Paste URL: `https://www.youtube.com/watch?v=jNQXAC9IVRw`
3. Enter title: "Test Video"
4. Click Add
5. ✅ Content should appear in library

### 3. Learning Sprint

1. Click on any "Ready" content in library
2. You should see chunk cards
3. Read through the content
4. Click "Take Quiz" or complete the chunk
5. ✅ Should see:
   - Coins earned notification
   - Streak update
   - Encouragement message

### 4. Gamification

#### Check Balance:
1. Look at dashboard header
2. ✅ Focus Coins and streak should be visible

#### Visit Shop:
1. Navigate to Shop
2. ✅ Should see items with prices
3. ✅ Items you can afford should be highlighted

#### Purchase Item:
1. Click on an affordable item
2. Click "Purchase"
3. ✅ Coins should deduct
4. ✅ Item should appear in inventory

### 5. Recovery Flow

1. Complete at least one chunk
2. Close the browser
3. Wait 5+ minutes (or manually set)
4. Open the content again
5. ✅ Should see "Welcome back" recovery screen with:
   - Key points recap
   - Refresher quiz (if long break)
   - "Continue" button

---

## API Testing (Backend Only)

For comprehensive backend testing, see `/backend/TESTING_GUIDE.md`

Quick test after backend is running:
```bash
# Health check
curl http://localhost:8000/health

# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"cli@test.com","password":"test123","full_name":"CLI User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=cli@test.com&password=test123"
```

---

## Frontend Component Testing

### Key Files to Test:

| Component | Path | Test |
|-----------|------|------|
| Login | `/app/(auth)/login` | Form submission |
| Register | `/app/(auth)/register` | Form validation |
| Library | `/app/library` | Content list loads |
| Sprint | `/app/sprint/[id]` | Chunk cards display |
| Shop | `/app/shop` | Items load, purchase works |
| Dashboard | `/app/dashboard` | Stats display |

### Browser DevTools Check:
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "XHR" or "Fetch"
4. ✅ All API calls should return 200
5. ❌ Any 401 = auth issue, 500 = backend error

---

## Environment Variables

### Frontend `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Backend `.env`:
```bash
SECRET_KEY=your-secret-key-make-it-long-and-random
OPENAI_API_KEY=sk-...  # Optional, for VLM
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| CORS error in browser | Backend CORS is configured for localhost:3000 |
| "Failed to fetch" | Make sure backend is running on port 8000 |
| Login fails | Check backend logs for errors |
| Content stuck "Processing" | Check backend logs, may need ffmpeg |
| Coins not updating | Hard refresh (Ctrl+Shift+R) |
| TypeScript errors | Run `npm install` then restart |

---

## Full Test Checklist

### User Journey:
- [ ] Register new account
- [ ] Login
- [ ] View empty library
- [ ] Upload PDF content
- [ ] Add YouTube URL
- [ ] See processing status
- [ ] View completed content
- [ ] Read chunk cards
- [ ] Complete quiz
- [ ] Earn Focus Coins
- [ ] Check streak incremented
- [ ] Visit shop
- [ ] Purchase item
- [ ] View inventory
- [ ] Check leaderboard
- [ ] View analytics
- [ ] Logout
- [ ] Login again (recovery flow)

### Technical Checks:
- [ ] Backend health endpoint works
- [ ] API docs load at /docs
- [ ] Frontend builds without errors
- [ ] No console errors in browser
- [ ] API calls return correct data
- [ ] Database persists after restart

---

## Production Readiness

Before deploying:
1. Change `SECRET_KEY` in backend
2. Set `NEXT_PUBLIC_API_URL` to production API
3. Configure PostgreSQL instead of SQLite
4. Set up Azure Storage instead of local
5. Enable HTTPS
6. Run `npm run build` to check for build errors
