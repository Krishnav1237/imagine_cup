"""
AI-powered content chunking using Claude API
Generates optimal learning chunks with titles, concepts, and quizzes
"""
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

from app.config import settings


class AIChunker:
    """AI-powered content chunker using Claude"""
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_chunks(
        self,
        transcript: str,
        title: str,
        duration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate learning chunks from transcript using Claude
        
        Args:
            transcript: Full text transcript
            title: Content title
            duration: Total duration in seconds (if available)
        
        Returns:
            List of chunk dictionaries with structure:
            {
                'title': str,
                'summary': str,
                'content': str,
                'duration': int,
                'key_concepts': List[str],
                'quiz_questions': List[dict],
                'difficulty': str
            }
        """
        
        # Build prompt for Claude
        prompt = self._build_chunking_prompt(transcript, title, duration)
        
        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            chunks = self._parse_chunks_response(response_text)
            
            return chunks
        
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            # Fallback: create simple chunks
            return self._create_fallback_chunks(transcript)
    
    def _build_chunking_prompt(
        self,
        transcript: str,
        title: str,
        duration: Optional[int]
    ) -> str:
        """Build the prompt for Claude"""
        
        duration_info = f"The total content duration is {duration} seconds." if duration else ""
        
        prompt = f"""You are an expert learning designer specializing in ADHD-friendly education. 
Your task is to break down educational content into optimal learning chunks.

Content Title: {title}
{duration_info}

Transcript:
{transcript[:8000]}  # Limit to avoid token limits

Instructions:
1. Divide this content into 2-5 minute learning chunks
2. Each chunk should focus on ONE main concept
3. Make chunks engaging for learners with ADHD (clear structure, varied pacing)
4. Create a descriptive title for each chunk
5. Write a brief summary (2-3 sentences)
6. Extract 3-5 key concepts per chunk
7. Generate 2-3 multiple choice quiz questions per chunk
8. Assess difficulty level (easy/medium/hard)

Return your response as a JSON array with this structure:
[
  {{
    "title": "Clear, engaging title",
    "summary": "Brief 2-3 sentence summary",
    "content": "The actual text content for this chunk",
    "duration": 180,
    "key_concepts": ["concept1", "concept2", "concept3"],
    "quiz_questions": [
      {{
        "question": "Question text?",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "correct_answer": 0,
        "explanation": "Why this is correct"
      }}
    ],
    "difficulty": "medium"
  }}
]

IMPORTANT: 
- Return ONLY valid JSON, no additional text
- Each chunk should be 2-5 minutes of content
- Make quiz questions relevant and educational
- Ensure key concepts are actionable takeaways"""
        
        return prompt
    
    def _parse_chunks_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse Claude's JSON response"""
        try:
            # Try to find JSON in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                chunks = json.loads(json_str)
                
                # Validate and clean chunks
                validated_chunks = []
                for chunk in chunks:
                    if self._validate_chunk(chunk):
                        validated_chunks.append(chunk)
                
                return validated_chunks
            
            return []
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
    
    def _validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Validate chunk structure"""
        required_fields = ['title', 'content', 'summary']
        
        for field in required_fields:
            if field not in chunk or not chunk[field]:
                return False
        
        # Ensure lists exist
        if 'key_concepts' not in chunk:
            chunk['key_concepts'] = []
        if 'quiz_questions' not in chunk:
            chunk['quiz_questions'] = []
        if 'duration' not in chunk:
            chunk['duration'] = 180
        if 'difficulty' not in chunk:
            chunk['difficulty'] = 'medium'
        
        return True
    
    def _create_fallback_chunks(self, transcript: str) -> List[Dict[str, Any]]:
        """Create simple chunks as fallback"""
        # Split transcript into paragraphs
        paragraphs = [p.strip() for p in transcript.split('\n\n') if p.strip()]
        
        # Group into chunks of ~500 words
        chunks = []
        current_chunk = []
        word_count = 0
        
        for para in paragraphs:
            para_words = len(para.split())
            
            if word_count + para_words > 500 and current_chunk:
                # Create chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'title': f"Section {len(chunks) + 1}",
                    'summary': chunk_text[:200] + "...",
                    'content': chunk_text,
                    'duration': 180,
                    'key_concepts': [],
                    'quiz_questions': [],
                    'difficulty': 'medium'
                })
                current_chunk = []
                word_count = 0
            
            current_chunk.append(para)
            word_count += para_words
        
        # Add remaining content
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'title': f"Section {len(chunks) + 1}",
                'summary': chunk_text[:200] + "...",
                'content': chunk_text,
                'duration': 180,
                'key_concepts': [],
                'quiz_questions': [],
                'difficulty': 'medium'
            })
        
        return chunks