"""
Content management API routes.
Handles content upload, retrieval, and sprint completion tracking.
"""
import logging
import os
import shutil
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import (
    User,
    ContentItem,
    ContentChunk,
    LearningSession,
    SessionChunk,
    VideoChapter,
)
from app.schemas.schemas import (
    ContentItem as ContentItemSchema,
    ContentItemDetail,
    ContentStatus,
    ContentSourceType,
    ChunkCompletion,
    VideoChapterSchema,
)
from app.config import settings
from app.services.content_processor import processor

logger = logging.getLogger("ContentAPI")
router = APIRouter()

@router.post("/upload", response_model=ContentItemSchema, status_code=status.HTTP_201_CREATED)
async def upload_content(
    background_tasks: BackgroundTasks,
    source_type: str = Form(...),
    source_url: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload new content (YouTube, PDF, or PowerPoint).
    """
    logger.info(f"📤 Upload request from {current_user.email} for type={source_type}")
    
    # 1. Validate Input
    if source_type not in [e.value for e in ContentSourceType]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: {', '.join([e.value for e in ContentSourceType])}"
        )
    
    # For YouTube: allow either a URL, a file, or both.
    if (
        source_type == ContentSourceType.YOUTUBE.value
        and not source_url
        and not file
    ):
        raise HTTPException(
            status_code=400,
            detail="Either source_url or file is required for YouTube content",
        )
    
    if source_type in [ContentSourceType.PDF.value, ContentSourceType.PPTX.value] and not file:
        raise HTTPException(status_code=400, detail="file is required for PDF/PPTX content")

    # 2. Create DB Entry
    new_content = ContentItem(
        user_id=current_user.id,
        title=title or f"Untitled {source_type}",
        source_type=source_type,
        source_url=source_url,
        status=ContentStatus.PENDING.value,
        stage="INITIALIZING",
        created_at=datetime.utcnow()
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)

    # 3. Save File Locally (if provided)
    if file:
        # Create directory: uploads/user_id/content_id/
        save_dir = f"{settings.UPLOAD_DIR}/{current_user.id}/{new_content.id}"
        os.makedirs(save_dir, exist_ok=True)
        
        # Save file
        file_ext = file.filename.split(".")[-1] if file.filename else source_type
        file_path = f"{save_dir}/original.{file_ext}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            new_content.file_path = file_path
            db.commit()
        except Exception as e:
            logger.error(f"❌ Failed to save file: {e}")
            db.delete(new_content)
            db.commit()
            raise HTTPException(500, f"Failed to save file: {str(e)}")

    # 4. Trigger Background Processing
    background_tasks.add_task(processor.process_content_task, new_content.id)
    logger.info(f"✅ Content {new_content.id} queued for processing")

    return new_content

@router.get("/", response_model=List[ContentItemSchema])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all content items for the current user.
    """
    query = db.query(ContentItem).filter(ContentItem.user_id == current_user.id)
    if status:
        query = query.filter(ContentItem.status == status)
    return query.order_by(ContentItem.created_at.desc()).offset(skip).limit(limit).all()

@router.get(
    "/{content_id}/chapters",
    response_model=list[VideoChapterSchema]
)
def get_video_chapters(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    chapters = (
        db.query(VideoChapter)
        .join(ContentItem, VideoChapter.content_id == ContentItem.id)
        .filter(
            VideoChapter.content_id == content_id,
            ContentItem.user_id == current_user.id,
        )
        .order_by(VideoChapter.chapter_index)
        .all()
    )

    return chapters

@router.get("/library")
async def get_library(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's content library with progress tracking.
    Returns rich data for library/dashboard display.
    """
    from sqlalchemy import func
    
    content_items = db.query(ContentItem).filter(
        ContentItem.user_id == current_user.id
    ).order_by(ContentItem.created_at.desc()).all()
    
    library = []
    for content in content_items:
        # Get chunk count
        total_chunks = db.query(func.count(ContentChunk.id)).filter(
            ContentChunk.content_item_id == content.id
        ).scalar() or 0
        
        # Get completed chunks for this user
        completed_chunks = 0
        if total_chunks > 0:
            completed_chunks = db.query(func.count(SessionChunk.id)).join(
                LearningSession
            ).filter(
                SessionChunk.chunk_id.in_(
                    db.query(ContentChunk.id).filter(ContentChunk.content_item_id == content.id)
                ),
                LearningSession.user_id == current_user.id,
                SessionChunk.is_completed == True
            ).scalar() or 0
        
        # Calculate progress
        progress_pct = (completed_chunks / total_chunks * 100) if total_chunks > 0 else 0
        
        # Estimate duration (5 min per chunk)
        estimated_duration = total_chunks * 5
        
        library.append({
            "id": content.id,
            "title": content.title,
            "source_type": content.source_type,
            "source_url": content.source_url,
            "thumbnail_url": content.thumbnail_url,
            "status": content.status,
            "error_message": content.error_message,
            "created_at": content.created_at.isoformat() if content.created_at else None,
            "processed_at": content.processed_at.isoformat() if content.processed_at else None,
            "duration_seconds": content.duration_seconds,
            "chunk_count": total_chunks,
            "completed_chunks": completed_chunks,
            "progress_percentage": round(progress_pct, 1),
            "estimated_duration_minutes": estimated_duration,
            "is_complete": completed_chunks >= total_chunks and total_chunks > 0,
            "stage": content.stage,
        })
    
    # Summary stats
    total_items = len(library)
    completed_items = len([l for l in library if l["is_complete"]])
    in_progress_items = len([l for l in library if 0 < l["progress_percentage"] < 100])
    
    return {
        "items": library,
        "summary": {
            "total": total_items,
            "completed": completed_items,
            "in_progress": in_progress_items,
            "not_started": total_items - completed_items - in_progress_items
        }
    }

@router.get("/{content_id}", response_model=ContentItemDetail)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific content item + chunks.
    """
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Explicitly fetch chunks
    chunks = db.query(ContentChunk).filter(
        ContentChunk.content_item_id == content_id
    ).order_by(ContentChunk.sequence_number).all()
    
    return {
        "id": content_item.id,
        "title": content_item.title,
        "source_type": content_item.source_type,
        "source_url": content_item.source_url,
        "status": content_item.status,
        "stage": content_item.stage,
        "created_at": content_item.created_at,
        "processed_at": content_item.processed_at,
        "error_message": content_item.error_message,
        "chunks": chunks,
        "chunk_count": len(chunks),
    }


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a content item.
    """
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db.delete(content_item)
    db.commit()
    logger.info(f"🗑️ Content {content_id} deleted by user {current_user.id}")
    return None

@router.post("/{content_id}/chunks/{chunk_id}/complete")
async def complete_chunk(
    content_id: int,
    chunk_id: int,
    completion_data: ChunkCompletion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark a sprint (chunk) as completed and track progress.
    
    Uses ADHD-optimized reward system with:
    - Dopamine-friendly variable rewards
    - Streak tracking and protection
    - Milestone celebrations
    - Break suggestions
    """
    from app.services.adhd_features import adhd_features
    
    logger.info(f"🏁 Completing chunk {chunk_id} for content {content_id} by user {current_user.id}")

    # 1. Verify Ownership
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id, 
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 2. Find or Create Learning Session
    session_name = f"Session for {content.title}"
    session = db.query(LearningSession).filter(
        LearningSession.user_id == current_user.id, 
        LearningSession.session_name == session_name
    ).first()

    if not session:
        session = LearningSession(
            user_id=current_user.id,
            session_name=session_name,
            started_at=datetime.utcnow(),
            total_chunks_viewed=0,
            total_duration_seconds=0,
            average_attention_score=0.0
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 3. Check for existing completion (prevent double counting)
    existing = db.query(SessionChunk).filter(
        SessionChunk.session_id == session.id,
        SessionChunk.chunk_id == chunk_id
    ).first()
    
    if existing:
        logger.info(f"ℹ️ Chunk {chunk_id} already completed.")
        return {
            "status": "already_completed", 
            "coins_earned": 0,
            "message": "This sprint was already completed!"
        }

    # 4. Record Completion
    session_chunk = SessionChunk(
        session_id=session.id,
        chunk_id=chunk_id,
        started_at=datetime.utcnow() - timedelta(seconds=completion_data.time_spent_seconds), 
        completed_at=datetime.utcnow(),
        is_completed=True,
        quiz_score=completion_data.quiz_score,
        average_attention=completion_data.average_attention
    )
    db.add(session_chunk)
    chunk = db.query(ContentChunk).filter(
        ContentChunk.id == chunk_id,
        ContentChunk.content_item_id == content_id
    ).first()
    if chunk:
        chunk.view_count = (chunk.view_count or 0) + 1

    
    # 5. Update Session Stats
    session.total_chunks_viewed += 1
    session.total_duration_seconds += completion_data.time_spent_seconds
    
    # Update session average attention
    if session.average_attention_score:
        # Running average
        n = session.total_chunks_viewed
        session.average_attention_score = (
            (session.average_attention_score * (n - 1) + completion_data.average_attention) / n
        )
    else:
        session.average_attention_score = completion_data.average_attention
    
    # 6. Calculate ADHD-Optimized Rewards
    reward = adhd_features.calculate_reward(
        focus_percentage=completion_data.average_attention,
        current_streak=current_user.current_streak,
        quiz_score=completion_data.quiz_score,
        time_spent_seconds=completion_data.time_spent_seconds
    )
    
    # 7. Update User's Focus Coins (ACTUALLY PERSIST!)
    current_user.focus_coins = (current_user.focus_coins or 0) + reward["total_coins"]
    current_user.total_sprints_completed = (current_user.total_sprints_completed or 0) + 1
    
    # 8. Update User's Streak
    streak_update = adhd_features.update_streak(
        last_activity_date=current_user.last_activity_date,
        current_streak=current_user.current_streak or 0,
        longest_streak=current_user.longest_streak or 0
    )
    current_user.current_streak = streak_update["new_streak"]
    current_user.longest_streak = streak_update["new_longest_streak"]
    current_user.last_activity_date = streak_update["last_activity_date"]
    
    # 9. Check for Milestone Celebration
    milestone = adhd_features.get_milestone_celebration(current_user.total_sprints_completed)
    if milestone:
        # Add milestone bonus coins
        current_user.focus_coins += milestone["coins"]
        reward["messages"].append(f"🎉 MILESTONE: {milestone['message']}")
        logger.info(f"🎉 User {current_user.id} hit milestone: {milestone['milestone']} sprints!")
    
    # 10. Check for Break Suggestion
    break_suggestion = adhd_features.should_suggest_break(session.total_duration_seconds)
    
    # 11. Get Encouragement Message
    encouragement = adhd_features.get_encouragement_message(
        completion_data.average_attention,
        current_user.current_streak
    )
    
    db.commit()
    
    # 12. Calculate Mystery Reward Tier (for frontend celebration)
    from app.services.mystery_rewards import calculate_mystery_reward, to_api_response
    
    mystery_reward = calculate_mystery_reward(
        base_coins=reward["base_coins"],
        streak_bonus=reward.get("streak_bonus", 0) / 100,  # Convert percentage to decimal
        difficulty_multiplier=1.0,
        is_quiz_correct=completion_data.quiz_score >= 80
    )
    mystery_response = to_api_response(mystery_reward)
    
    logger.info(f"✅ Chunk {chunk_id} complete. Coins: +{reward['total_coins']}, Total Balance: {current_user.focus_coins}, Streak: {current_user.current_streak}")
    
    return {
        "status": "success",
        "coins_earned": mystery_reward.final_coins,
        "base_coins": reward["base_coins"],
        "multiplier": mystery_reward.multiplier,
        "reward_tier": mystery_reward.tier.value,
        "reward_breakdown": reward,
        "new_balance": current_user.focus_coins,
        "streak": {
            "current": current_user.current_streak,
            "longest": current_user.longest_streak,
            "increased": streak_update.get("streak_increased", False)
        },
        "milestone": milestone,
        "break_suggestion": break_suggestion if break_suggestion["should_break"] else None,
        "encouragement": encouragement,
        "session_stats": {
            "chunks_completed": session.total_chunks_viewed,
            "total_time_seconds": session.total_duration_seconds,
            "average_attention": round(session.average_attention_score, 2) if session.average_attention_score else None
        },
        # Mystery reward data for frontend celebration
        "mystery_reward": mystery_response,
        "message": mystery_reward.message,
        "bonus_item": mystery_reward.bonus_item,
        "celebration_level": mystery_reward.celebration_level,
        "is_jackpot": mystery_reward.tier.value == "legendary",
    }