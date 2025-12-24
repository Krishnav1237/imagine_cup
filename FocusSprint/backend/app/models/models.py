"""
SQLAlchemy Database Models.
"""
from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Preferences
    default_chunk_length = Column(Integer, default=5)
    preferred_difficulty = Column(String, default="medium")
    
    # Gamification - Focus Coins Economy
    focus_coins = Column(Integer, default=500)  # Starting coins for new users
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity_date = Column(DateTime, nullable=True)  # For streak calculation
    total_sprints_completed = Column(Integer, default=0)

    content_items = relationship("ContentItem", back_populates="owner")
    sessions = relationship("LearningSession", back_populates="user")
    inventory = relationship("UserInventory", back_populates="user")

class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    source_type = Column(String) # youtube, pdf, pptx
    source_url = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    
    # Video/Media metadata
    thumbnail_url = Column(String, nullable=True)  # Video thumbnail
    video_url = Column(String, nullable=True)  # Playable video URL
    
    status = Column(String, default="pending") # pending, processing, completed, failed
    error_message = Column(String, nullable=True)
    # Processing diagnostics
    stage = Column(String, nullable=True)          # e.g. DOCUMENT_PIPELINE, RAG, LLM, VIDEO_PIPELINE
    retry_count = Column(Integer, default=0)       # For controlled retries

    # Metadata
    duration_seconds = Column(Integer, nullable=True)
    transcript_text = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Semantic metadata (future use)
    language = Column(String(32), nullable=True)
    estimated_reading_time = Column(Integer, nullable=True)  # seconds

    owner = relationship("User", back_populates="content_items")
    chunks = relationship("ContentChunk", back_populates="content_item", cascade="all, delete-orphan")

class ContentChunk(Base):
    __tablename__ = "content_chunks"
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    sequence_number = Column(Integer, nullable=False, default=0)
    title = Column(String(512), nullable=True)
    summary = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    key_concepts = Column(JSON, nullable=True)
    quiz_questions = Column(JSON, nullable=True)
    difficulty_level = Column(String(32), nullable=True)
    # Generation provenance
    generation_model = Column(String(128), nullable=True)  # e.g. llama3:8b-instruct-q4_K_M
    generation_strategy = Column(String(64), nullable=True)  # RAG, VLM, TRANSCRIPT_ONLY

    # Chunk-card support
    card_json = Column(Text, nullable=True)         # full chunk-card JSON payload
    source_file = Column(String(512), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_slide = Column(Integer, nullable=True)
    # RAG traceability
    source_confidence = Column(Float, nullable=True)   # similarity / confidence score
    rag_group_id = Column(Integer, nullable=True)      # which semantic group produced this chunk

    # VLM Visual Context (NEW)
    visual_context = Column(Text, nullable=True)    # Description of what's shown visually
    key_visual_elements = Column(JSON, nullable=True)  # List of visual elements
    key_frame_timestamp = Column(Float, nullable=True)  # Timestamp of key frame in seconds

    content_item = relationship("ContentItem", back_populates="chunks")
    # Quality & usage signals
    view_count = Column(Integer, default=0)
    avg_rating = Column(Float, nullable=True)


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    session_name = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    total_duration_seconds = Column(Integer, default=0)
    total_chunks_viewed = Column(Integer, default=0)
    average_attention_score = Column(Float, nullable=True)  # ADHD attention tracking
    # Session-level control signals
    focus_mode_enabled = Column(Boolean, default=False)
    adaptive_pacing = Column(Boolean, default=True)

    
    user = relationship("User", back_populates="sessions")
    chunk_progress = relationship("SessionChunk", back_populates="session")

class SessionChunk(Base):
    __tablename__ = "session_chunks"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"))
    chunk_id = Column(Integer, ForeignKey("content_chunks.id"))
    
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    
    quiz_score = Column(Float, nullable=True)
    average_attention = Column(Float, nullable=True)
    attention_drops = Column(Integer, default=0)  # number of detected attention losses

    
    session = relationship("LearningSession", back_populates="chunk_progress")


class UserInventory(Base):
    """Stores items purchased from the shop by users."""
    __tablename__ = "user_inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(String, nullable=False)  # e.g., "avatar_cosmic"
    item_type = Column(String, nullable=False)  # avatar, pet, badge, card_pack
    item_name = Column(String, nullable=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)
    is_equipped = Column(Boolean, default=False)  # For avatars/pets that can be equipped
    
    user = relationship("User", back_populates="inventory")