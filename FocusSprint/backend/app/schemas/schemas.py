"""
Pydantic schemas for data validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from enum import Enum

# =======================
# AUTHENTICATION SCHEMAS
# =======================

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Schema for the data embedded in the JWT token.
    """
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    full_name: Optional[str] = None

class UserLogin(UserBase):
    password: str

class UserPreferences(BaseModel):
    default_chunk_length: int = 5
    preferred_difficulty: str = "medium"

class User(UserBase):
    id: int
    full_name: Optional[str] = None
    is_active: bool
    
    # Preferences
    default_chunk_length: int = 5
    preferred_difficulty: str = "medium"
    
    class Config:
        from_attributes = True

# =======================
# CONTENT SCHEMAS
# =======================

class ContentSourceType(str, Enum):
    PDF = "pdf"
    PPTX = "pptx"
    YOUTUBE = "youtube"


class ContentStatus(str, Enum):
    PENDING = "pending"        # created, not yet processed
    PROCESSING = "processing"  # currently running pipeline
    COMPLETED = "completed"    # finished successfully
    FAILED = "failed"          # terminal error

class ContentChunk(BaseModel):
    id: int
    sequence_number: int
    title: str
    summary: Optional[str] = None
    text_content: Optional[str] = None
    duration_seconds: int
    difficulty_level: Optional[str] = None
    
    # Quiz Data
    key_concepts: Optional[List[str]] = []
    quiz_questions: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        from_attributes = True

class ContentItem(BaseModel):
    id: int
    title: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ContentItemDetail(ContentItem):
    chunks: List[ContentChunk] = []
    chunk_count: int = 0

class ChunkCompletion(BaseModel):
    """
    Schema for completing a learning chunk with performance data.
    """
    quiz_score: float = Field(..., ge=0, le=100, description="Score achieved on the quiz (0-100)")
    average_attention: float = Field(..., ge=0, le=100, description="Average attention score detected (0-100)")
    time_spent_seconds: int = Field(..., ge=0, description="Time spent on the chunk in seconds")

# =======================
# ANALYTICS SCHEMAS
# =======================

class UserProgress(BaseModel):
    total_content_items: int
    completed_items: int
    total_learning_time_minutes: int
    average_attention_score: float
    streak_days: int

class ContentAnalytics(BaseModel):
    content_id: int
    title: str
    total_views: int
    completion_rate: float
    average_quiz_score: float
    average_attention: float