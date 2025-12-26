# ADHD Features Changelog

> **Date:** December 25, 2025  
> **Focus:** ADHD-first features for mass adoption

---

## 🎯 Features Implemented

### 1. Micro-Commitment ("Just 30 Seconds")
**File:** `src/components/micro-commitment.tsx`

- "Just 30 seconds" option before full sprint
- After completion: "Ready for 30 more?" prompt
- Lowers activation energy for ADHD users

---

### 2. Variable Mystery Rewards
**File:** `backend/app/services/mystery_rewards.py`

- 5 tiers: Common (60%), Uncommon (25%), Rare (10%), Epic (4%), Legendary (1%)
- Random multipliers: 1x → 10x
- Bonus items at higher tiers
- Celebration messages + animations

---

### 3. Visual Timer
**File:** `src/components/ui/visual-timer.tsx`

- Shrinking circle countdown
- Color transitions: green → yellow → red
- Time comparisons: "Like 1 song"
- Pulse animation near end

---

### 4. Hyperfocus Protection
**File:** `src/components/hyperfocus-guard.tsx`

- Forced break after 45 minutes
- 60-second countdown before dismiss
- Activity suggestions (hydration, stretching)
- Encouraging messages

---

### 5. Attention Overlay
**File:** `src/components/attention-overlay.tsx`

- Blurs content when user inactive 5+ seconds
- "Welcome back 👋" toast on return
- Activity-based (mouse/keyboard) detection
- Non-judgmental messaging

---

### 6. Frustration Detection
**File:** `src/hooks/use-frustration-detector.ts`

- Tracks rapid clicking, erratic scrolling
- Monitors tab switches
- Offers interventions: breaks, easier content
- Score-based triggering

---

### 7. Reward Reveal Animations
**File:** `src/components/reward-reveal.tsx`

- Mystery box opening animation
- Tier-based celebrations (confetti for rare+)
- Multiplier display
- Bonus item reveals

---

## 📁 New Files Created

| File | Purpose |
|------|---------|
| `backend/app/services/mystery_rewards.py` | Variable reward calculations |
| `src/components/micro-commitment.tsx` | Just 30s prompts |
| `src/components/ui/visual-timer.tsx` | Circular countdown |
| `src/components/hyperfocus-guard.tsx` | Break enforcement |
| `src/components/attention-overlay.tsx` | Focus detection |
| `src/components/reward-reveal.tsx` | Celebration animations |
| `src/hooks/use-frustration-detector.ts` | Pattern detection |

---

## 🔧 Files Modified

| File | Changes |
|------|---------|
| `src/app/sprint/page.tsx` | Integrated all ADHD components |
| `backend/app/api/v1/content.py` | Mystery reward API response |

---

## 🧪 How to Test

```bash
# Start backend
cd backend && uvicorn app.main:app --reload

# Start frontend
npm run dev

# Test flow:
# 1. Login and navigate to a completed content
# 2. Click "Resume Sprint"
# 3. See "Just 30 seconds" prompt
# 4. Complete sprint, see mystery reward reveal
# 5. Stay 45+ min to trigger hyperfocus break
```
