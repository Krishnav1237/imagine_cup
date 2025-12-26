# FocusSprint User Manual

## What is FocusSprint?

FocusSprint is an **AI-powered ADHD-focused learning platform** that transforms any content (videos, PDFs, presentations) into brain-friendly micro-sprints. It uses gamification, attention tracking, and personalized features to help ADHD users learn effectively.

---

## Getting Started

### Step 1: Create Account
1. Open FocusSprint
2. Click **"Sign Up"**
3. Enter email and password
4. You start with **500 Focus Coins** 🪙

### Step 2: Add Learning Content
You can add content in 3 ways:

| Method | How |
|--------|-----|
| **YouTube** | Paste video URL |
| **PDF** | Upload document |
| **PowerPoint** | Upload .pptx file |

The AI automatically:
- Transcribes audio/video
- Analyzes visual content
- Breaks into 2-5 minute chunks
- Generates quiz questions

---

## Core User Flows

### Flow 1: Learning a New Topic

```
┌─────────────────┐
│  Add Content    │ ← Paste URL or upload file
└────────┬────────┘
         ▼
┌─────────────────┐
│  AI Processing  │ ← Wait 1-2 minutes
└────────┬────────┘
         ▼
┌─────────────────┐
│   View Library  │ ← See all your content
└────────┬────────┘
         ▼
┌─────────────────┐
│  Start Sprint   │ ← Begin learning chunk
└────────┬────────┘
         ▼
┌─────────────────┐
│   Read/Watch    │ ← Focused 2-5 min session
└────────┬────────┘
         ▼
┌─────────────────┐
│   Take Quiz     │ ← Test comprehension
└────────┬────────┘
         ▼
┌─────────────────┐
│  Earn Coins! 🪙 │ ← Get rewards
└─────────────────┘
```

### Flow 2: Returning After Break

When you come back after being away:

```
┌─────────────────┐
│  Open Content   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Recovery Screen │ ← "Here's what you learned..."
└────────┬────────┘
         ▼
┌─────────────────┐
│ Refresher Quiz  │ ← Quick 2-question recap
└────────┬────────┘
         ▼
┌─────────────────┐
│ Continue Sprint │ ← Pick up where you left off
└─────────────────┘
```

### Flow 3: Using the Shop

```
┌─────────────────┐
│   Earn Coins    │ ← Complete sprints, ace quizzes
└────────┬────────┘
         ▼
┌─────────────────┐
│   Visit Shop    │ ← Browse items
└────────┬────────┘
         ▼
┌─────────────────┐
│   Buy Items     │ ← Avatars, pets, badges
└────────┬────────┘
         ▼
┌─────────────────┐
│ Equip in Profile│ ← Show off your style!
└─────────────────┘
```

---

## Features Explained

### 🎯 Micro-Sprints
- Content broken into 2-5 minute chunks
- Perfect for ADHD attention spans
- Each sprint = focused learning session

### 🪙 Focus Coins Economy
| Action | Coins |
|--------|-------|
| Complete sprint | 50-80 coins |
| Perfect quiz (100%) | +25 bonus |
| High focus (90%+) | +25 bonus |
| 3+ day streak | 2x multiplier |
| Milestone bonus | 50-500 coins |

### 🔥 Streaks
- Log in and complete at least 1 sprint daily
- Streak counter increases each day
- **Streak Freeze**: Pay 50 coins to protect your streak for 1 day

### 🏆 Milestones
Celebrate achievements at:
- 10 sprints: "Sprinter" 🏃
- 25 sprints: "Focused" 🎯
- 50 sprints: "Committed" 💪
- 100 sprints: "Dedicated" 🌟
- 500 sprints: "Master" 👑
- 1000 sprints: "Legend" 🏅

### 🧠 ADHD-Specific Features

#### Focus Recovery
When you return after a break:
- **Short break (5 min)**: Quick 2-point recap
- **Medium break (30 min)**: Recap + refresher quiz
- **Long break (1+ day)**: Full review + suggestions

#### Break Reminders
- **25 min**: Pomodoro break suggestion
- **45 min**: Hyperfocus warning
- **60 min**: Mandatory break recommended

#### Difficulty Adaptation
System monitors your performance:
- Scoring 90%+ → Harder content suggested
- Scoring <60% → Easier content suggested
- Keeps you in the "flow zone"

#### Progressive Disclosure
- Content revealed one bullet at a time
- Prevents information overload
- Tap to reveal next point

---

## Navigation Guide

### Library Page
Your content hub showing:
- All uploaded content
- Processing status
- Progress percentage
- Thumbnail previews

### Sprint View
The learning interface:
- Current chunk content
- Visual hints (from video)
- Timer
- Quiz button

### Dashboard
Overview showing:
- Streak status
- Coins balance
- Recent activity
- ADHD insights

### Shop
Spend your coins on:
- **Avatars**: Customize your profile
- **Pets**: Companion characters
- **Badges**: Show achievements
- **Card Packs**: Collectible knowledge cards

### Analytics
Track your progress:
- Peak focus hours
- Best performing topics
- Attention trends
- Personalized tips

---

## Tips for ADHD Users

### 🎯 Starting a Session
1. Set a timer for 25 minutes max
2. Close other browser tabs
3. Put phone on silent
4. Have water nearby

### 🧘 During a Sprint
- If you zone out, tap anywhere to refocus
- Use progressive disclosure mode
- Take notes if it helps you focus

### 🏃 After a Sprint
- Celebrate small wins!
- Take a 5-minute break
- Stand up and stretch
- Return for next sprint

### 💡 General Tips
- Learn at YOUR best focus time (check Analytics)
- Use streak freezes on tough days
- Don't aim for perfection - progress matters
- Visual content works better for most ADHD brains

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Reveal next bullet |
| `→` | Next chunk |
| `←` | Previous chunk |
| `Q` | Open quiz |
| `B` | Take break |
| `Esc` | Exit to library |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Content not processing | Wait 2-3 minutes, refresh |
| YouTube error | Check URL is valid |
| Quiz not loading | Refresh the page |
| Coins not updating | Complete another sprint |
| Streak lost | Use Streak Freeze next time |

---

## API Quick Reference

For developers integrating with FocusSprint:

```
Authentication:
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me

Content:
POST /api/v1/content/
GET  /api/v1/content/library
GET  /api/v1/content/{id}
POST /api/v1/content/{id}/chunks/{chunk_id}/complete

Gamification:
GET  /api/v1/gamification/user/coins
POST /api/v1/gamification/user/streak/freeze
GET  /api/v1/gamification/shop/items
POST /api/v1/gamification/shop/purchase/{item_id}
GET  /api/v1/gamification/user/inventory

ADHD Learning:
GET  /api/v1/adhd-learning/content/{id}/recovery
GET  /api/v1/adhd-learning/content/{id}/timestamps
POST /api/v1/adhd-learning/session/attention-alert
GET  /api/v1/adhd-learning/user/difficulty-recommendation

Analytics:
GET  /api/v1/analytics/progress
GET  /api/v1/analytics/adhd-insights
```

---

## Support

Having issues? 
- Email: support@focussprint.app
- Discord: discord.gg/focussprint
- GitHub: github.com/focussprint/app
