"""
Analytics API routes.
Provides insights into user progress and content performance.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import User, ContentItem, ContentChunk, LearningSession, SessionChunk
from app.schemas.schemas import UserProgress, ContentAnalytics

logger = logging.getLogger("AnalyticsAPI")
router = APIRouter()

@router.get("/progress", response_model=UserProgress)
async def get_user_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get overall progress statistics for the current user.
    """
    logger.debug(f"📊 Fetching progress for {current_user.email}")
    
    # Total content items
    total_content = db.query(func.count(ContentItem.id)).filter(
        ContentItem.user_id == current_user.id
    ).scalar() or 0
    
    # Completed content items (all chunks viewed)
    completed_content_ids = db.query(ContentItem.id).filter(
        ContentItem.user_id == current_user.id,
        ContentItem.status == 'completed'
    ).all()
    
    completed_items = 0
    for (content_id,) in completed_content_ids:
        total_chunks = db.query(func.count(ContentChunk.id)).filter(
            ContentChunk.content_item_id == content_id
        ).scalar() or 0
        
        viewed_chunks = db.query(func.count(SessionChunk.id.distinct())).join(
            LearningSession
        ).filter(
            SessionChunk.chunk_id.in_(
                db.query(ContentChunk.id).filter(
                    ContentChunk.content_item_id == content_id
                )
            ),
            LearningSession.user_id == current_user.id,
            SessionChunk.is_completed == True
        ).scalar() or 0
        
        if total_chunks > 0 and viewed_chunks >= total_chunks:
            completed_items += 1
    
    # Total learning time
    total_time = db.query(func.sum(LearningSession.total_duration_seconds)).filter(
        LearningSession.user_id == current_user.id
    ).scalar() or 0
    
    total_time_minutes = int(total_time / 60)
    
    # Average attention score
    avg_attention = db.query(func.avg(LearningSession.average_attention_score)).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.average_attention_score.isnot(None)
    ).scalar() or 0.0
    
    # Calculate streak
    streak_days = calculate_streak(current_user.id, db)
    
    return UserProgress(
        total_content_items=total_content,
        completed_items=completed_items,
        total_learning_time_minutes=total_time_minutes,
        average_attention_score=round(avg_attention, 2),
        streak_days=streak_days
    )

@router.get("/content/{content_id}", response_model=ContentAnalytics)
async def get_content_analytics(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific content item.
    """
    # Verify content belongs to user
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get all chunks for this content
    chunk_ids = [c.id for c in db.query(ContentChunk.id).filter(
        ContentChunk.content_item_id == content_id
    ).all()]
    
    if not chunk_ids:
        return ContentAnalytics(
            content_id=content_id,
            title=content.title,
            total_views=0,
            completion_rate=0.0,
            average_quiz_score=0.0,
            average_attention=0.0
        )
    
    # Total views (unique sessions)
    total_views = db.query(func.count(LearningSession.id.distinct())).join(
        SessionChunk
    ).filter(
        SessionChunk.chunk_id.in_(chunk_ids),
        LearningSession.user_id == current_user.id
    ).scalar() or 0
    
    # Completion rate
    total_chunks = len(chunk_ids)
    completed_chunks = db.query(func.count(SessionChunk.id)).filter(
        SessionChunk.chunk_id.in_(chunk_ids),
        SessionChunk.is_completed == True
    ).scalar() or 0
    
    completion_rate = (completed_chunks / (total_chunks * max(1, total_views))) * 100 if total_views > 0 else 0.0
    
    # Average quiz score
    avg_quiz = db.query(func.avg(SessionChunk.quiz_score)).filter(
        SessionChunk.chunk_id.in_(chunk_ids),
        SessionChunk.quiz_score.isnot(None)
    ).scalar() or 0.0
    
    # Average attention
    avg_attention = db.query(func.avg(SessionChunk.average_attention)).filter(
        SessionChunk.chunk_id.in_(chunk_ids),
        SessionChunk.average_attention.isnot(None)
    ).scalar() or 0.0
    
    return ContentAnalytics(
        content_id=content_id,
        title=content.title,
        total_views=total_views,
        completion_rate=round(completion_rate, 2),
        average_quiz_score=round(avg_quiz, 2),
        average_attention=round(avg_attention, 2)
    )

@router.get("/overview")
async def get_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive overview of user's learning analytics.
    """
    # Recent sessions (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.started_at >= seven_days_ago
    ).count()
    
    # Learning time by day (last 7 days)
    daily_time = []
    for i in range(7):
        day_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        time_spent = db.query(func.sum(LearningSession.total_duration_seconds)).filter(
            LearningSession.user_id == current_user.id,
            LearningSession.started_at >= day_start,
            LearningSession.started_at < day_end
        ).scalar() or 0
        
        daily_time.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'minutes': int(time_spent / 60)
        })
    
    # Top performing content
    content_performance = []
    content_items = db.query(ContentItem).filter(
        ContentItem.user_id == current_user.id,
        ContentItem.status == 'completed'
    ).limit(5).all()
    
    for content in content_items:
        chunk_ids = [c.id for c in db.query(ContentChunk.id).filter(
            ContentChunk.content_item_id == content.id
        ).all()]
        
        if chunk_ids:
            avg_attention = db.query(func.avg(SessionChunk.average_attention)).filter(
                SessionChunk.chunk_id.in_(chunk_ids),
                SessionChunk.average_attention.isnot(None)
            ).scalar() or 0.0
            
            content_performance.append({
                'id': content.id,
                'title': content.title,
                'average_attention': round(avg_attention, 2)
            })
    
    # Attention trends
    attention_over_time = []
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id,
        LearningSession.average_attention_score.isnot(None)
    ).order_by(LearningSession.started_at.desc()).limit(10).all()
    
    for session in reversed(sessions):
        attention_over_time.append({
            'session_id': session.id,
            'date': session.started_at.strftime('%Y-%m-%d'),
            'score': round(session.average_attention_score, 2)
        })
    
    return {
        'recent_activity': {
            'sessions_last_7_days': recent_sessions,
            'daily_learning_time': daily_time
        },
        'content_performance': content_performance,
        'attention_trends': attention_over_time
    }

@router.get("/session/{session_id}/details")
async def get_session_analytics(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific session.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get session chunks with details
    session_chunks = db.query(SessionChunk).filter(
        SessionChunk.session_id == session_id
    ).all()
    
    chunk_details = []
    for sc in session_chunks:
        chunk = db.query(ContentChunk).filter(
            ContentChunk.id == sc.chunk_id
        ).first()
        
        if chunk:
            chunk_details.append({
                'chunk_id': chunk.id,
                'title': chunk.title,
                'completed': sc.is_completed,
                'average_attention': sc.average_attention,
                'quiz_score': sc.quiz_score,
                'time_spent': (sc.completed_at - sc.started_at).total_seconds() if sc.completed_at else None
            })
    
    return {
        'session': {
            'id': session.id,
            'name': session.session_name,
            'started_at': session.started_at,
            'ended_at': session.ended_at,
            'duration_minutes': session.total_duration_seconds / 60 if session.total_duration_seconds else 0,
            'average_attention': session.average_attention_score
        },
        'chunks': chunk_details
    }

def calculate_streak(user_id: int, db: Session) -> int:
    """
    Calculate the user's current learning streak in days.
    """
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    streak = 0
    
    for i in range(365):  # Check up to 1 year
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        # Check if user had any activity this day
        activity = db.query(LearningSession).filter(
            LearningSession.user_id == user_id,
            LearningSession.started_at >= day,
            LearningSession.started_at < next_day
        ).first()
        
        if activity:
            streak += 1
        else:
            # Streak broken
            break
    
    return streak


@router.get("/adhd-insights")
async def get_adhd_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized ADHD-focused insights and recommendations.
    
    Analyzes user's attention patterns and provides actionable tips
    specifically designed for ADHD learning optimization.
    """
    from app.services.adhd_features import adhd_features
    
    # Get user's sessions for analysis
    sessions = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id
    ).order_by(LearningSession.started_at.desc()).limit(30).all()
    
    if not sessions:
        return {
            "has_data": False,
            "message": "Complete some sprints to get personalized insights!",
            "recommendations": [
                "🎯 Start with short 5-minute sprints to build momentum",
                "🌅 Try learning at different times to find your peak focus",
                "🎮 Use the reward system to stay motivated!"
            ]
        }
    
    # Analyze attention patterns
    attention_scores = [s.average_attention_score for s in sessions if s.average_attention_score]
    avg_attention = sum(attention_scores) / len(attention_scores) if attention_scores else 0
    
    # Analyze session durations
    durations = [s.total_duration_seconds for s in sessions if s.total_duration_seconds]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Find best focus times (by hour of day)
    hour_attention = {}
    for session in sessions:
        if session.started_at and session.average_attention_score:
            hour = session.started_at.hour
            if hour not in hour_attention:
                hour_attention[hour] = []
            hour_attention[hour].append(session.average_attention_score)
    
    best_hours = []
    for hour, scores in hour_attention.items():
        avg = sum(scores) / len(scores)
        best_hours.append((hour, avg))
    
    best_hours.sort(key=lambda x: x[1], reverse=True)
    peak_hours = [h[0] for h in best_hours[:3]]
    
    # Generate personalized recommendations
    recommendations = []
    
    # Attention-based recommendations
    if avg_attention >= 80:
        recommendations.append("🎯 Amazing focus! You're in the top tier. Keep up the great work!")
    elif avg_attention >= 60:
        recommendations.append("💪 Good focus levels! Try the Pomodoro technique for even better results.")
    else:
        recommendations.append("🧘 Consider trying breathing exercises before sprints to improve focus.")
        recommendations.append("🎧 Background music or white noise might help you concentrate.")
    
    # Duration-based recommendations
    if avg_duration > 1800:  # 30+ minutes
        recommendations.append("⚠️ Long sessions detected. Break them into smaller sprints for better retention!")
    elif avg_duration < 300:  # Less than 5 minutes
        recommendations.append("📈 Try gradually increasing sprint length as your focus improves.")
    
    # Time-based recommendations
    if peak_hours:
        peak_hour = peak_hours[0]
        if 5 <= peak_hour <= 11:
            recommendations.append(f"🌅 Morning person detected! Your peak focus is around {peak_hour}:00.")
        elif 12 <= peak_hour <= 17:
            recommendations.append(f"☀️ Afternoon learner! Try scheduling important sprints around {peak_hour}:00.")
        else:
            recommendations.append(f"🌙 Night owl detected! Your focus peaks around {peak_hour}:00.")
    
    # Streak-based encouragement
    streak = current_user.current_streak or 0
    if streak >= 7:
        recommendations.append(f"🔥 {streak}-day streak! You're building an incredible habit!")
    elif streak >= 3:
        recommendations.append(f"⭐ {streak}-day streak! Keep going - habits form around day 21!")
    else:
        recommendations.append("🌱 Building consistency is key. Aim for a small daily goal!")
    
    # Calculate focus trend
    if len(attention_scores) >= 5:
        recent = sum(attention_scores[:5]) / 5
        older = sum(attention_scores[-5:]) / 5

        if recent > older:
            trend = "improving"
            trend_emoji = "📈"
        elif recent < older:
            trend = "declining"
            trend_emoji = "📉"
        else:
            trend = "stable"
            trend_emoji = "📊"
    else:
        trend = "not_enough_data"
        trend_emoji = "📊"
    
    return {
        "has_data": True,
        "summary": {
            "average_attention": round(avg_attention, 1),
            "average_session_minutes": round(avg_duration / 60, 1),
            "total_sessions": len(sessions),
            "focus_trend": trend,
            "trend_emoji": trend_emoji
        },
        "peak_focus_hours": peak_hours,
        "recommendations": recommendations,
        "adhd_tips": [
            "🎯 Use visual timers - seeing time helps ADHD brains stay on track",
            "📱 Enable Do Not Disturb during sprints to avoid distractions",
            "🎮 Celebrate small wins! Every sprint completed is an achievement",
            "🧠 Movement breaks help reset focus - try a quick stretch!",
            "📝 Keep a focus journal to identify what works for you"
        ]
    }