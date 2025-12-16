"""
Database models for ADHD Learning Platform
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # User preferences
    default_chunk_length = Column(Integer, default=180)  # 3 minutes
    preferred_difficulty = Column(String(50), default="medium")
    
    # Relationships
    content_items = relationship("ContentItem", back_populates="user", cascade="all, delete-orphan")
    learning_sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")


class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content metadata
    title = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)  # youtube, pdf, pptx
    source_url = Column(String(1000))
    file_path = Column(String(500))
    duration_seconds = Column(Integer)  # For video content
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Transcription
    transcript_path = Column(String(500))
    transcript_text = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="content_items")
    chunks = relationship("ContentChunk", back_populates="content_item", cascade="all, delete-orphan")


class ContentChunk(Base):
    __tablename__ = "content_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    content_item_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    
    # Chunk metadata
    sequence_number = Column(Integer, nullable=False)  # Order in content
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    duration_seconds = Column(Integer)
    
    # Chunk content
    text_content = Column(Text, nullable=False)
    
    # Learning metadata
    key_concepts = Column(JSON)  # List of key concepts
    difficulty_level = Column(String(50))  # easy, medium, hard
    
    # Quiz questions (stored as JSON)
    quiz_questions = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_item = relationship("ContentItem", back_populates="chunks")
    session_chunks = relationship("SessionChunk", back_populates="chunk")


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    session_name = Column(String(500))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    # Session stats
    total_chunks_viewed = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    average_attention_score = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="learning_sessions")
    session_chunks = relationship("SessionChunk", back_populates="session", cascade="all, delete-orphan")


class SessionChunk(Base):
    __tablename__ = "session_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("content_chunks.id"), nullable=False)
    
    # Viewing metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    # Attention tracking
    attention_scores = Column(JSON)  # Time-series attention data
    average_attention = Column(Float)
    
    # Quiz performance
    quiz_score = Column(Float)
    quiz_attempts = Column(Integer, default=0)
    
    # Adaptive adjustments
    adjusted_duration = Column(Integer)  # If duration was adjusted
    
    # Relationships
    session = relationship("LearningSession", back_populates="session_chunks")
    chunk = relationship("ContentChunk", back_populates="session_chunks")