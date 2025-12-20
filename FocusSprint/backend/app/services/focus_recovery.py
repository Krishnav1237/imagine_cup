"""
Focus Recovery System for ADHD users.

Provides context recaps and gentle re-engagement when users return after breaks
or attention loss. Designed to minimize the cognitive load of "where was I?"
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.models import (
    User, ContentItem, ContentChunk, 
    LearningSession, SessionChunk
)

logger = logging.getLogger("FocusRecovery")


class FocusRecoveryService:
    """
    Helps ADHD users recover context after breaks or distractions.
    
    Features:
    - Context recap based on last session
    - Quick refresher quiz
    - Visual anchor (last viewed frame)
    - Time-decay based context depth
    """
    
    # Time thresholds for context depth
    SHORT_BREAK = 300  # 5 minutes - light recap
    MEDIUM_BREAK = 1800  # 30 minutes - moderate recap
    LONG_BREAK = 86400  # 1 day - full recap
    
    def get_recovery_context(
        self,
        user: User,
        content_id: int,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get context recovery information for a user returning to content.
        
        Returns:
            {
                "needs_recovery": bool,
                "break_type": "short" | "medium" | "long" | "none",
                "last_chunk": {...},
                "key_points_recap": [...],
                "refresher_quiz": {...},
                "encouragement": "..."
            }
        """
        # Get content
        content = db.query(ContentItem).filter(
            ContentItem.id == content_id,
            ContentItem.user_id == user.id
        ).first()
        
        if not content:
            return {"needs_recovery": False, "error": "Content not found"}
        
        # Find user's last session for this content
        last_session = db.query(LearningSession).filter(
            LearningSession.user_id == user.id,
            LearningSession.session_name.like(f"%{content.title}%")
        ).order_by(desc(LearningSession.started_at)).first()
        
        if not last_session:
            return {
                "needs_recovery": False,
                "is_first_time": True,
                "message": "Welcome! Let's start learning.",
                "content_title": content.title,
                "total_chunks": len(content.chunks) if content.chunks else 0
            }
        
        # Calculate time since last activity
        last_activity = last_session.ended_at or last_session.started_at
        time_since = datetime.utcnow() - last_activity
        seconds_since = time_since.total_seconds()
        
        # Determine break type
        if seconds_since < self.SHORT_BREAK:
            break_type = "none"
        elif seconds_since < self.MEDIUM_BREAK:
            break_type = "short"
        elif seconds_since < self.LONG_BREAK:
            break_type = "medium"
        else:
            break_type = "long"
        
        # Get last completed chunks
        completed_chunks = db.query(SessionChunk).join(
            LearningSession
        ).filter(
            LearningSession.user_id == user.id,
            SessionChunk.chunk_id.in_(
                db.query(ContentChunk.id).filter(
                    ContentChunk.content_item_id == content_id
                )
            ),
            SessionChunk.is_completed == True
        ).order_by(desc(SessionChunk.completed_at)).limit(5).all()
        
        if not completed_chunks:
            return {
                "needs_recovery": False,
                "break_type": break_type,
                "message": "Ready to start? You haven't completed any chunks yet.",
                "progress": {"completed": 0, "total": len(content.chunks) if content.chunks else 0}
            }
        
        # Get the actual chunk details
        last_chunk_ids = [sc.chunk_id for sc in completed_chunks]
        last_chunks = db.query(ContentChunk).filter(
            ContentChunk.id.in_(last_chunk_ids)
        ).all()
        
        # Build recovery context based on break type
        result = {
            "needs_recovery": break_type != "none",
            "break_type": break_type,
            "time_away": self._format_time_away(seconds_since),
            "content_title": content.title,
            "progress": {
                "completed": len(completed_chunks),
                "total": len(content.chunks) if content.chunks else 0,
                "percentage": round(len(completed_chunks) / max(len(content.chunks), 1) * 100, 1)
            }
        }
        
        # Add context based on break duration
        if break_type == "short":
            result["key_points_recap"] = self._get_quick_recap(last_chunks, 2)
            result["message"] = "Quick break? Here's where you left off."
            result["encouragement"] = self._get_encouragement("short_break")
            
        elif break_type == "medium":
            result["key_points_recap"] = self._get_quick_recap(last_chunks, 3)
            result["refresher_quiz"] = self._generate_refresher_quiz(last_chunks)
            result["message"] = "Welcome back! Let's refresh your memory."
            result["encouragement"] = self._get_encouragement("medium_break")
            
        elif break_type == "long":
            result["key_points_recap"] = self._get_full_recap(last_chunks)
            result["refresher_quiz"] = self._generate_refresher_quiz(last_chunks, 3)
            result["suggested_review"] = self._suggest_review_chunks(content, completed_chunks, db)
            result["message"] = "It's been a while! Here's a comprehensive recap."
            result["encouragement"] = self._get_encouragement("long_break")
        
        # Add last chunk info for visual anchor
        if last_chunks:
            last = last_chunks[0]
            result["last_chunk"] = {
                "id": last.id,
                "title": last.title,
                "visual_context": last.visual_context,
                "key_frame_timestamp": last.key_frame_timestamp,
                "sequence": last.sequence_number
            }
        
        # Suggest next chunk
        next_chunk = self._get_next_chunk(content, completed_chunks, db)
        if next_chunk:
            result["next_chunk"] = {
                "id": next_chunk.id,
                "title": next_chunk.title,
                "sequence": next_chunk.sequence_number
            }
        
        return result
    
    def _get_quick_recap(
        self,
        chunks: List[ContentChunk],
        num_points: int
    ) -> List[str]:
        """Get quick recap bullet points from recent chunks"""
        points = []
        for chunk in chunks[:num_points]:
            if chunk.text_content:
                # Get first meaningful sentence
                sentences = chunk.text_content.split('.')
                for s in sentences:
                    if len(s.strip()) > 20:
                        points.append(s.strip())
                        break
            elif chunk.title:
                points.append(f"Learned about: {chunk.title}")
        return points
    
    def _get_full_recap(self, chunks: List[ContentChunk]) -> List[Dict[str, str]]:
        """Get detailed recap for long breaks"""
        recap = []
        for chunk in chunks[:5]:
            recap.append({
                "title": chunk.title or "Untitled section",
                "summary": (chunk.summary or chunk.text_content or "")[:150],
                "visual_hint": chunk.visual_context
            })
        return recap
    
    def _generate_refresher_quiz(
        self,
        chunks: List[ContentChunk],
        num_questions: int = 2
    ) -> Dict[str, Any]:
        """Generate quick refresher quiz from completed content"""
        questions = []
        
        for chunk in chunks[:num_questions]:
            if chunk.quiz_questions:
                # Use existing quiz questions
                try:
                    quiz_data = chunk.quiz_questions if isinstance(chunk.quiz_questions, list) else []
                    if quiz_data:
                        questions.append(quiz_data[0])
                except Exception:
                    pass
            elif chunk.title and chunk.text_content:
                # Generate simple recall question
                questions.append({
                    "type": "recall",
                    "question": f"What do you remember about '{chunk.title}'?",
                    "hint": (chunk.text_content[:100] + "...") if chunk.text_content else None
                })
        
        return {
            "questions": questions[:num_questions],
            "purpose": "Quick refresher to activate your memory",
            "is_optional": True
        }
    
    def _suggest_review_chunks(
        self,
        content: ContentItem,
        completed: List[SessionChunk],
        db: Session
    ) -> List[Dict[str, Any]]:
        """Suggest chunks to review after long break"""
        # Find chunks with low quiz scores
        low_score_chunks = []
        for sc in completed:
            if sc.quiz_score and sc.quiz_score < 70:
                chunk = db.query(ContentChunk).filter(ContentChunk.id == sc.chunk_id).first()
                if chunk:
                    low_score_chunks.append({
                        "id": chunk.id,
                        "title": chunk.title,
                        "last_score": sc.quiz_score,
                        "reason": "Could use a quick review"
                    })
        
        return low_score_chunks[:3]
    
    def _get_next_chunk(
        self,
        content: ContentItem,
        completed: List[SessionChunk],
        db: Session
    ) -> Optional[ContentChunk]:
        """Get the next chunk to study"""
        completed_ids = {sc.chunk_id for sc in completed}
        
        for chunk in sorted(content.chunks or [], key=lambda c: c.sequence_number):
            if chunk.id not in completed_ids:
                return chunk
        
        return None
    
    def _format_time_away(self, seconds: float) -> str:
        """Format time away in human-readable format"""
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
    
    def _get_encouragement(self, break_type: str) -> str:
        """Get ADHD-friendly encouragement based on break type"""
        import random
        
        messages = {
            "short_break": [
                "Quick breaks are great for focus! Ready to dive back in? 🚀",
                "Short pauses help your brain process. Let's continue! 💪",
                "Perfect timing - your brain just got a mini-recharge! ⚡"
            ],
            "medium_break": [
                "Taking breaks is part of learning! Let's refresh and go. 🌟",
                "Your brain's been processing in the background. Ready? 🧠",
                "Welcome back! Every return builds consistency. 🔥"
            ],
            "long_break": [
                "You came back! That's the hardest part done. 🏆",
                "Starting again takes courage. You've got this! 💪",
                "Every expert was once a beginner who kept returning. 🌱"
            ]
        }
        
        return random.choice(messages.get(break_type, messages["short_break"]))


# Global service instance
focus_recovery = FocusRecoveryService()
