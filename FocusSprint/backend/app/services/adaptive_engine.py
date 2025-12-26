"""
Adaptive Learning Engine.
Adjusts content delivery based on real-time attention tracking.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import ContentChunk, SessionChunk, LearningSession, User

logger = logging.getLogger("AdaptiveEngine")

class AdaptiveEngine:
    """Engine for adaptive learning adjustments"""
    
    # Thresholds for attention-based decisions
    LOW_ATTENTION_THRESHOLD = 40.0
    HIGH_ATTENTION_THRESHOLD = 80.0
    ATTENTION_DROP_THRESHOLD = 20.0  # Drop of 20 points triggers adjustment
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_attention_adjustment(
        self,
        current_score: float,
        average_score: float,
        chunk_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check if content adjustment is needed based on attention.
        """
        chunk = self.db.query(ContentChunk).filter(
            ContentChunk.id == chunk_id
        ).first()
        
        if not chunk:
            logger.warning(f"⚠️ Chunk {chunk_id} not found during adaptation check.")
            return None
        
        # Low attention - suggest shorter chunks or break
        if current_score < self.LOW_ATTENTION_THRESHOLD:
            if average_score < self.LOW_ATTENTION_THRESHOLD:
                logger.info(f"📉 Low attention detected (Curr: {current_score}, Avg: {average_score}). Recommending break.")
                return {
                    'type': 'break_recommended',
                    'message': 'Your attention seems low. Consider taking a short break.',
                    'new_chunk_duration': max(120, chunk.duration_seconds - 60)
                }
        
        # Sudden attention drop
        if average_score - current_score > self.ATTENTION_DROP_THRESHOLD:
            logger.info(f"📉 Sudden attention drop detected (Drop: {average_score - current_score}). Recommending quiz.")
            return {
                'type': 'engagement_drop',
                'message': 'Noticed a focus drop. Want to try a different learning mode?',
                'suggestion': 'interactive_quiz'
            }
        
        # High sustained attention - can handle longer chunks
        if current_score > self.HIGH_ATTENTION_THRESHOLD and average_score > self.HIGH_ATTENTION_THRESHOLD:
            logger.info(f"📈 High attention maintained. Suggesting challenge increase.")
            return {
                'type': 'increase_challenge',
                'message': "You're doing great! Ready for more advanced content?",
                'new_chunk_duration': min(300, chunk.duration_seconds + 60)
            }
        
        return None
    
    def get_next_chunk(
        self,
        session_id: int,
        current_chunk_id: Optional[int],
        user_id: int
    ) -> Optional[ContentChunk]:
        """
        Get the next recommended chunk based on user performance.
        """
        # Get current chunk info
        if current_chunk_id:
            current_chunk = self.db.query(ContentChunk).filter(
                ContentChunk.id == current_chunk_id
            ).first()
            
            if not current_chunk:
                return None
            
            # Get user's performance on current chunk
            session_chunk = self.db.query(SessionChunk).filter(
                SessionChunk.session_id == session_id,
                SessionChunk.chunk_id == current_chunk_id
            ).first()
            
            # Next sequential chunk from same content
            next_chunk = self.db.query(ContentChunk).filter(
                ContentChunk.content_item_id == current_chunk.content_item_id,
                ContentChunk.sequence_number == current_chunk.sequence_number + 1
            ).first()
            
            if next_chunk:
                # Adjust difficulty if needed
                if session_chunk and session_chunk.average_attention:
                    next_chunk = self._adjust_chunk_difficulty(
                        next_chunk,
                        session_chunk.average_attention,
                        session_chunk.quiz_score
                    )
                
                return next_chunk
        
        # No current chunk - recommend based on user history
        return self._recommend_new_chunk(user_id)
    
    def _adjust_chunk_difficulty(
        self,
        chunk: ContentChunk,
        attention_score: float,
        quiz_score: Optional[float]
    ) -> ContentChunk:
        """
        Adjust chunk attributes based on performance.
        (Note: This modifies recommendations, not the stored chunk)
        """
        # If struggling (low attention or quiz score), recommend easier approach
        if attention_score < 50 or (quiz_score and quiz_score < 60):
            # Could adjust duration, add hints, etc.
            pass
        
        # If excelling, can increase challenge
        elif attention_score > 80 and (not quiz_score or quiz_score > 85):
            # Could recommend harder content, skip basics, etc.
            pass
        
        return chunk
    
    def _recommend_new_chunk(self, user_id: int) -> Optional[ContentChunk]:
        """
        Recommend a new chunk for user to start.
        Priority: incomplete content > new content > review.
        """
        # Get user preferences
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Find incomplete chunks from user's content
        incomplete_chunk = self.db.query(ContentChunk).join(
            ContentChunk.content_item
        ).outerjoin(SessionChunk).filter(
            ContentChunk.content_item.has(user_id=user_id),
            ~SessionChunk.is_completed | (SessionChunk.id == None)
        ).order_by(
            ContentChunk.sequence_number
        ).first()
        
        if incomplete_chunk:
            return incomplete_chunk
        
        # If all complete, recommend newest unstarted content
        unstarted_chunk = self.db.query(ContentChunk).join(
            ContentChunk.content_item
        ).outerjoin(SessionChunk).filter(
            ContentChunk.content_item.has(user_id=user_id),
            SessionChunk.id == None
        ).order_by(
            ContentChunk.content_item_id.desc(),
            ContentChunk.sequence_number
        ).first()
        
        return unstarted_chunk
    
    def calculate_optimal_duration(
        self,
        user_id: int,
        base_duration: int = 180
    ) -> int:
        """
        Calculate optimal chunk duration for user based on history.
        """
        # Get user's average attention across recent sessions
        recent_avg = self.db.query(
            func.avg(SessionChunk.average_attention)
        ).join(LearningSession).filter(
            LearningSession.user_id == user_id,
            SessionChunk.average_attention.isnot(None)
        ).limit(10).scalar()
        
        if not recent_avg:
            return base_duration
        
        # Adjust based on attention patterns
        if recent_avg < 50:
            # Struggling - shorter chunks
            return max(120, base_duration - 60)
        elif recent_avg > 75:
            # Doing well - can handle longer
            return min(300, base_duration + 60)
        
        return base_duration
    
    def should_recommend_break(
        self,
        session_id: int,
        continuous_minutes: int = 30
    ) -> bool:
        """
        Determine if a break should be recommended.
        """
        session = self.db.query(LearningSession).filter(
            LearningSession.id == session_id
        ).first()
        
        if not session:
            return False
        
        # Recommend break after sustained learning
        if session.total_duration_seconds > continuous_minutes * 60:
            # Check if attention is dropping
            recent_chunks = self.db.query(SessionChunk).filter(
                SessionChunk.session_id == session_id
            ).order_by(SessionChunk.started_at.desc()).limit(3).all()
            
            if len(recent_chunks) >= 3:
                recent_attention = [
                    sc.average_attention for sc in recent_chunks
                    if sc.average_attention
                ]
                
                if recent_attention:
                    avg_recent = sum(recent_attention) / len(recent_attention)
                    if avg_recent < 55:
                        logger.info(f"🛌 Break recommended due to fatigue (Avg Recent Attn: {avg_recent})")
                        return True
        
        return False