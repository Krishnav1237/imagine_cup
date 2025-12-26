"""
ADHD Learning API routes.
Specialized endpoints for focus recovery, difficulty adaptation, and distraction handling.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import User, ContentItem, LearningSession
from app.services.focus_recovery import focus_recovery
from app.services.adhd_features import adhd_features

logger = logging.getLogger("ADHDLearningAPI")
router = APIRouter()


class AttentionAlertData(BaseModel):
    content_id: int
    chunk_id: int
    attention_level: float  # 0-100
    time_distracted_seconds: int
    session_duration_seconds: int


class DifficultyFeedback(BaseModel):
    content_id: int
    was_too_hard: bool = False
    was_too_easy: bool = False


@router.get("/content/{content_id}/recovery")
async def get_focus_recovery_context(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get focus recovery context when user returns to content.
    
    Provides:
    - Time-based context recap
    - Key points from last session
    - Refresher quiz if needed
    - Encouragement message
    - Next chunk suggestion
    
    Returns recovery context based on how long user was away.
    """
    recovery = focus_recovery.get_recovery_context(
        user=current_user,
        content_id=content_id,
        db=db
    )
    
    return recovery


@router.get("/content/{content_id}/timestamps")
async def get_smart_timestamps(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get smart timestamps (jump points) for video content.
    
    Returns key moments with:
    - Timestamp
    - Topic title
    - Visual context description
    - User's completion status
    """
    from app.models.models import ContentChunk, SessionChunk
    from sqlalchemy import func
    
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Get all chunks with their timestamps
    chunks = db.query(ContentChunk).filter(
        ContentChunk.content_item_id == content_id
    ).order_by(ContentChunk.sequence_number).all()
    
    # Get user's completed chunks
    completed_chunk_ids = set()
    completed_chunks = db.query(SessionChunk.chunk_id).join(
        LearningSession
    ).filter(
        LearningSession.user_id == current_user.id,
        SessionChunk.is_completed == True
    ).all()
    completed_chunk_ids = {c[0] for c in completed_chunks}
    
    timestamps = []
    for chunk in chunks:
        timestamps.append({
            "chunk_id": chunk.id,
            "sequence": chunk.sequence_number,
            "timestamp_seconds": chunk.key_frame_timestamp,
            "title": chunk.title,
            "topic": chunk.summary[:50] if chunk.summary else None,
            "visual_context": chunk.visual_context,
            "is_completed": chunk.id in completed_chunk_ids,
            "difficulty": chunk.difficulty_level
        })
    
    return {
        "content_id": content_id,
        "content_title": content.title,
        "total_duration": content.duration_seconds,
        "timestamps": timestamps,
        "completed_count": len(completed_chunk_ids),
        "total_count": len(chunks)
    }


@router.post("/session/attention-alert")
async def report_attention_loss(
    data: AttentionAlertData,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Report attention loss detected by frontend (e.g., eye-tracking).
    
    Returns:
    - Gentle welcome back message
    - Break suggestion if pattern detected
    - Quick recap of current chunk
    """
    import random
    
    # Determine response based on distraction severity
    if data.time_distracted_seconds > 60:
        severity = "long"
    elif data.time_distracted_seconds > 30:
        severity = "medium"
    else:
        severity = "short"
    
    # Get current chunk for context
    from app.models.models import ContentChunk
    chunk = db.query(ContentChunk).filter(
        ContentChunk.id == data.chunk_id
    ).first()
    
    # Check if break might help
    break_suggestion = adhd_features.should_suggest_break(data.session_duration_seconds)
    
    # Select appropriate welcome back message
    messages = {
        "short": [
            "Mind wandered? Totally normal! Here's where we were...",
            "Hey, welcome back! Let's pick up right here.",
            "Quick mental detour? No worries, here's the context."
        ],
        "medium": [
            "Taking a moment? That's okay. Here's a quick recap.",
            "Welcome back! Your brain needed a breather. Let's refocus.",
            "Lost in thought? Here's where you left off."
        ],
        "long": [
            "Extended break? No judgment! Here's what we were covering.",
            "You're back! That took courage. Here's the recap.",
            "Long pause? ADHD happens. Let's gently re-engage."
        ]
    }
    
    welcome_message = random.choice(messages[severity])
    
    response = {
        "welcome_message": welcome_message,
        "severity": severity,
        "chunk_title": chunk.title if chunk else None,
        "chunk_visual_hint": chunk.visual_context if chunk else None,
        "should_suggest_break": break_suggestion["should_break"]
    }
    
    if break_suggestion["should_break"]:
        response["break_suggestion"] = {
            "message": break_suggestion["message"],
            "suggested_minutes": break_suggestion["suggested_break_minutes"],
            "break_type": break_suggestion["break_type"]
        }
    
    # If long distraction, add recap
    if severity in ["medium", "long"] and chunk and chunk.text_content:
        # Get first 2 bullet points as recap
        content = chunk.text_content.split('\n')
        response["quick_recap"] = content[:2]
    
    logger.info(f"👁️ Attention alert: user {current_user.id}, {severity} distraction ({data.time_distracted_seconds}s)")
    
    return response


@router.get("/user/difficulty-recommendation")
async def get_difficulty_recommendation(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized difficulty recommendation based on user's performance.
    
    Analyzes:
    - Recent quiz scores
    - Attention patterns
    - Completion rates
    - Time spent per chunk
    
    Returns optimal difficulty and reasoning.
    """
    from app.models.models import SessionChunk
    from sqlalchemy import func
    
    # Get recent quiz scores
    recent_scores = db.query(SessionChunk.quiz_score).join(
        LearningSession
    ).filter(
        LearningSession.user_id == current_user.id,
        SessionChunk.quiz_score.isnot(None)
    ).order_by(SessionChunk.completed_at.desc()).limit(10).all()
    
    scores = [s[0] for s in recent_scores if s[0] is not None]
    
    # Get recent attention scores
    recent_attention = db.query(SessionChunk.average_attention).join(
        LearningSession
    ).filter(
        LearningSession.user_id == current_user.id,
        SessionChunk.average_attention.isnot(None)
    ).order_by(SessionChunk.completed_at.desc()).limit(10).all()
    
    attention_scores = [a[0] for a in recent_attention if a[0] is not None]
    
    # Calculate averages
    avg_quiz = sum(scores) / len(scores) if scores else 75
    avg_attention = sum(attention_scores) / len(attention_scores) if attention_scores else 70
    
    # Determine optimal difficulty
    if avg_quiz >= 90 and avg_attention >= 80:
        difficulty = "hard"
        reasoning = "You're acing quizzes with great focus! Time for a challenge."
        adjustment = "increase"
    elif avg_quiz < 60 or avg_attention < 50:
        difficulty = "easy"
        reasoning = "Let's build confidence with easier content first."
        adjustment = "decrease"
    elif avg_quiz >= 80:
        difficulty = "medium-hard"
        reasoning = "Strong performance! Slight difficulty increase recommended."
        adjustment = "slight_increase"
    elif avg_quiz < 70:
        difficulty = "easy-medium"
        reasoning = "Solid effort! Let's reinforce with slightly easier content."
        adjustment = "slight_decrease"
    else:
        difficulty = "medium"
        reasoning = "You're in the flow zone! Current difficulty is perfect."
        adjustment = "maintain"
    
    return {
        "recommended_difficulty": difficulty,
        "reasoning": reasoning,
        "adjustment": adjustment,
        "analysis": {
            "average_quiz_score": round(avg_quiz, 1),
            "average_attention": round(avg_attention, 1),
            "sessions_analyzed": len(scores)
        },
        "current_preference": current_user.preferred_difficulty,
        "adhd_tip": "ADHD brains thrive in the 'flow zone' - not too easy, not too hard!"
    }


@router.post("/user/difficulty-feedback")
async def submit_difficulty_feedback(
    feedback: DifficultyFeedback,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit user feedback about content difficulty.
    Used to improve personalization.
    """
    # Update user preference if consistent feedback
    if feedback.was_too_hard:
        # Lower difficulty preference
        difficulty_map = {"hard": "medium", "medium": "easy", "easy": "easy"}
        new_difficulty = difficulty_map.get(current_user.preferred_difficulty, "medium")
        current_user.preferred_difficulty = new_difficulty
        message = f"Got it! Adjusting to {new_difficulty} difficulty."
    elif feedback.was_too_easy:
        # Increase difficulty preference
        difficulty_map = {"easy": "medium", "medium": "hard", "hard": "hard"}
        new_difficulty = difficulty_map.get(current_user.preferred_difficulty, "medium")
        current_user.preferred_difficulty = new_difficulty
        message = f"Challenge accepted! Adjusting to {new_difficulty} difficulty."
    else:
        message = "Thanks for the feedback!"
    
    db.commit()
    
    return {
        "success": True,
        "message": message,
        "new_difficulty": current_user.preferred_difficulty
    }


@router.get("/content/{content_id}/progressive-disclosure")
async def get_progressive_disclosure_content(
    content_id: int,
    chunk_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get content formatted for progressive disclosure mode.
    
    Returns content split into revealable units for ADHD-friendly consumption.
    """
    from app.models.models import ContentChunk
    
    chunk = db.query(ContentChunk).filter(
        ContentChunk.id == chunk_id,
        ContentChunk.content_item_id == content_id
    ).first()
    
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    # Split content into progressive units
    units = []
    
    # Title first
    if chunk.title:
        units.append({
            "type": "title",
            "content": chunk.title,
            "delay_ms": 0
        })
    
    # Visual context hint
    if chunk.visual_context:
        units.append({
            "type": "visual_hint",
            "content": f"📺 {chunk.visual_context}",
            "delay_ms": 500
        })
    
    # Content bullets one by one
    if chunk.text_content:
        bullets = chunk.text_content.split('\n')
        for i, bullet in enumerate(bullets):
            if bullet.strip():
                units.append({
                    "type": "bullet",
                    "content": bullet.strip(),
                    "delay_ms": 800 + (i * 300),  # Staggered reveal
                    "index": i
                })
    
    return {
        "chunk_id": chunk_id,
        "total_units": len(units),
        "units": units,
        "reveal_mode": "tap_to_reveal",  # or "auto_reveal"
        "suggested_pace_ms": 2000  # 2 seconds between auto-reveals
    }
