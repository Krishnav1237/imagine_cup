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
from app.models.models import User, ContentItem, ContentChunk, LearningSession, SessionChunk
from app.schemas.schemas import (
    ContentItem as ContentItemSchema,
    ContentItemDetail,
    ContentStatus,
    ContentSourceType,
    ChunkCompletion
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
    
    if source_type == ContentSourceType.YOUTUBE.value and not source_url:
        raise HTTPException(status_code=400, detail="source_url is required for YouTube content")
    
    if source_type in [ContentSourceType.PDF.value, ContentSourceType.PPTX.value] and not file:
        raise HTTPException(status_code=400, detail="file is required for PDF/PPTX content")

    # 2. Create DB Entry
    new_content = ContentItem(
        user_id=current_user.id,
        title=title or f"Untitled {source_type}",
        source_type=source_type,
        source_url=source_url,
        status=ContentStatus.PENDING.value,
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
    return query.offset(skip).limit(limit).all()

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
        **content_item.__dict__,
        "chunks": chunks,
        "chunk_count": len(chunks)
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
    Mark a sprint (chunk) as completed and track progress using real data.
    """
    logger.info(f"🏁 Completing chunk {chunk_id} for content {content_id}")

    # 1. Verify Ownership
    content = db.query(ContentItem).filter(
        ContentItem.id == content_id, 
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # 2. Find or Create Learning Session
    # We group sprints into a "Session" for analytics
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
            total_duration_seconds=0
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
        return {"status": "already_completed", "coins_earned": 0}

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
    
    # 5. Update Session Stats
    session.total_chunks_viewed += 1
    session.total_duration_seconds += completion_data.time_spent_seconds
    
    # 6. Calculate Coins (e.g. 10 base + bonus for good quiz score)
    coins_earned = 10 + int(completion_data.quiz_score / 10)
    
    db.commit()
    logger.info(f"✅ Chunk {chunk_id} complete. Score: {completion_data.quiz_score}, Attn: {completion_data.average_attention}")
    
    return {
        "status": "success", 
        "coins_earned": coins_earned
    }