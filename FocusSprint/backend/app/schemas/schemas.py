"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ContentSourceType(str, Enum):
    YOUTUBE = "youtube"
    PDF = "pdf"
    PPTX = "pptx"


class ContentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPreferences(BaseModel):
    default_chunk_length: int = Field(default=180, ge=60, le=600)
    preferred_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    default_chunk_length: int
    preferred_difficulty: str
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ============================================================================
# Content Schemas
# ============================================================================

class ContentUpload(BaseModel):
    source_type: ContentSourceType
    source_url: Optional[str] = None
    title: Optional[str] = None
    
    @validator('source_url')
    def validate_youtube_url(cls, v, values):
        if values.get('source_type') == ContentSourceType.YOUTUBE and not v:
            raise ValueError('source_url required for YouTube content')
        return v


class ContentItemBase(BaseModel):
    title: str
    source_type: ContentSourceType
    source_url: Optional[str] = None


class ContentItem(ContentItemBase):
    id: int
    user_id: int
    status: ContentStatus
    duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentItemDetail(ContentItem):
    chunk_count: int = 0
    chunks: List['ContentChunk'] = []


# ============================================================================
# Chunk Schemas
# ============================================================================

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option
    explanation: Optional[str] = None


class ContentChunkBase(BaseModel):
    title: str
    summary: Optional[str] = None
    text_content: str
    duration_seconds: Optional[int] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM


class ContentChunkCreate(ContentChunkBase):
    content_item_id: int
    sequence_number: int
    key_concepts: List[str] = []
    quiz_questions: List[QuizQuestion] = []


class ContentChunk(ContentChunkBase):
    id: int
    content_item_id: int
    sequence_number: int
    key_concepts: List[str]
    quiz_questions: List[QuizQuestion]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Learning Session Schemas
# ============================================================================

class LearningSessionCreate(BaseModel):
    session_name: Optional[str] = None


class LearningSession(BaseModel):
    id: int
    user_id: int
    session_name: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    total_chunks_viewed: int
    total_duration_seconds: int
    average_attention_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class AttentionDataPoint(BaseModel):
    timestamp: float  # Seconds since chunk start
    score: float = Field(..., ge=0, le=100)


class SessionChunkProgress(BaseModel):
    chunk_id: int
    is_completed: bool = False
    attention_scores: List[AttentionDataPoint] = []
    quiz_score: Optional[float] = None


class SessionChunk(BaseModel):
    id: int
    session_id: int
    chunk_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool
    average_attention: Optional[float] = None
    quiz_score: Optional[float] = None
    quiz_attempts: int
    adjusted_duration: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# WebSocket Messages
# ============================================================================

class WSMessageType(str, Enum):
    ATTENTION_UPDATE = "attention_update"
    CHUNK_COMPLETE = "chunk_complete"
    REQUEST_NEXT = "request_next"
    SESSION_UPDATE = "session_update"


class WSMessage(BaseModel):
    type: WSMessageType
    data: Dict[str, Any]


class AttentionUpdate(BaseModel):
    focus_score: float = Field(..., ge=0, le=100)
    timestamp: float


class ChunkAdjustment(BaseModel):
    chunk_id: int
    new_duration: Optional[int] = None
    recommended_break: bool = False


# ============================================================================
# Analytics Schemas
# ============================================================================

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


# Update forward references
ContentItemDetail.model_rebuild()