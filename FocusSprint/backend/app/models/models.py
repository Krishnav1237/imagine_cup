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
    
    # Metadata
    duration_seconds = Column(Integer, nullable=True)
    transcript_text = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

    # Chunk-card support
    card_json = Column(Text, nullable=True)         # full chunk-card JSON payload
    source_file = Column(String(512), nullable=True)
    source_page = Column(Integer, nullable=True)
    source_slide = Column(Integer, nullable=True)
    
    # VLM Visual Context (NEW)
    visual_context = Column(Text, nullable=True)    # Description of what's shown visually
    key_visual_elements = Column(JSON, nullable=True)  # List of visual elements
    key_frame_timestamp = Column(Float, nullable=True)  # Timestamp of key frame in seconds

    content_item = relationship("ContentItem", back_populates="chunks")

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