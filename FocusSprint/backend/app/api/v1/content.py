"""
Content management API routes
Handles content upload, processing, and retrieval
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.models import User, ContentItem, ContentChunk
from app.schemas.schemas import (
    ContentUpload,
    ContentItem as ContentItemSchema,
    ContentItemDetail,
    ContentChunk as ContentChunkSchema,
    ContentStatus,
    ContentSourceType
)
from app.services.storage.adapter import get_storage_adapter
from app.services.content_processor import ContentProcessor

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
    Upload new content (YouTube, PDF, or PowerPoint)
    """
    # Validate source type
    try:
        source_type_enum = ContentSourceType(source_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: {', '.join([e.value for e in ContentSourceType])}"
        )
    
    # Validate input based on source type
    if source_type_enum == ContentSourceType.YOUTUBE:
        if not source_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="source_url is required for YouTube content"
            )
    else:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file is required for PDF and PPTX content"
            )
    
    # Create content item
    content_item = ContentItem(
        user_id=current_user.id,
        title=title or f"Untitled {source_type_enum.value}",
        source_type=source_type_enum.value,
        source_url=source_url,
        status=ContentStatus.PENDING.value
    )
    
    db.add(content_item)
    db.commit()
    db.refresh(content_item)
    
    # Handle file upload if present
    if file:
        storage = get_storage_adapter()
        file_extension = file.filename.split('.')[-1] if file.filename else source_type_enum.value
        file_path = f"content/{current_user.id}/{content_item.id}/original.{file_extension}"
        
        await storage.save_uploaded_file(file, file_path)
        content_item.file_path = file_path
        db.commit()
        db.refresh(content_item)
    
    # Process content in background
    processor = ContentProcessor(db)
    background_tasks.add_task(processor.process_content, content_item.id)
    
    return content_item


@router.get("/", response_model=List[ContentItemSchema])
async def list_content(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all content items for the current user
    """
    query = db.query(ContentItem).filter(ContentItem.user_id == current_user.id)
    
    if status:
        query = query.filter(ContentItem.status == status)
    
    content_items = query.offset(skip).limit(limit).all()
    return content_items


@router.get("/{content_id}", response_model=ContentItemDetail)
async def get_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific content item
    """
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Get chunks
    chunks = db.query(ContentChunk).filter(
        ContentChunk.content_item_id == content_id
    ).order_by(ContentChunk.sequence_number).all()
    
    # Build response
    response = ContentItemDetail(
        **content_item.__dict__,
        chunk_count=len(chunks),
        chunks=chunks
    )
    
    return response


@router.get("/{content_id}/chunks", response_model=List[ContentChunkSchema])
async def get_content_chunks(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all chunks for a specific content item
    """
    # Verify content belongs to user
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    chunks = db.query(ContentChunk).filter(
        ContentChunk.content_item_id == content_id
    ).order_by(ContentChunk.sequence_number).all()
    
    return chunks


@router.get("/{content_id}/chunks/{chunk_id}", response_model=ContentChunkSchema)
async def get_chunk(
    content_id: int,
    chunk_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific chunk
    """
    # Verify content belongs to user
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    chunk = db.query(ContentChunk).filter(
        ContentChunk.id == chunk_id,
        ContentChunk.content_item_id == content_id
    ).first()
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    
    return chunk


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a content item and all its chunks
    """
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Delete files from storage
    if content_item.file_path:
        storage = get_storage_adapter()
        try:
            await storage.delete_file(content_item.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # Delete from database (cascades to chunks)
    db.delete(content_item)
    db.commit()
    
    return None


@router.post("/{content_id}/reprocess", response_model=ContentItemSchema)
async def reprocess_content(
    content_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Reprocess content (re-generate chunks)
    """
    content_item = db.query(ContentItem).filter(
        ContentItem.id == content_id,
        ContentItem.user_id == current_user.id
    ).first()
    
    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Reset status
    content_item.status = ContentStatus.PENDING.value
    content_item.error_message = None
    
    # Delete existing chunks
    db.query(ContentChunk).filter(
        ContentChunk.content_item_id == content_id
    ).delete()
    
    db.commit()
    db.refresh(content_item)
    
    # Reprocess in background
    processor = ContentProcessor(db)
    background_tasks.add_task(processor.process_content, content_item.id)
    
    return content_item