"""
AI-powered content chunking using Azure OpenAI.
Generates optimal learning chunks with titles, concepts, and quizzes.
Falls back to offline logic if Azure is not configured or fails.
"""
import json
import logging
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("AIChunker")

class AIChunker:
    """AI-powered content chunker using Azure OpenAI"""
    
    def __init__(self):
        self.client = None
        self.deployment_name = None
        
        # safely get settings (handle if config.py isn't updated yet)
        api_key = getattr(settings, "AZURE_OPENAI_API_KEY", None)
        endpoint = getattr(settings, "AZURE_OPENAI_ENDPOINT", None)
        deployment = getattr(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        
        if api_key and endpoint:
            try:
                from openai import AsyncAzureOpenAI
                self.client = AsyncAzureOpenAI(
                    api_key=api_key,
                    api_version="2023-05-15",
                    azure_endpoint=endpoint
                )
                self.deployment_name = deployment
                logger.info(f"✅ Azure OpenAI configured (Deployment: {self.deployment_name})")
            except ImportError:
                logger.error("❌ 'openai' library not installed. Install it with: pip install openai")
        else:
            logger.warning("⚠️ Azure OpenAI settings not found. Chunker will run in OFFLINE mode.")

    async def generate_chunks(
        self,
        transcript: str,
        title: str,
        duration: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate learning chunks.
        Uses Azure OpenAI if configured, otherwise falls back to offline splitting.
        """
        if self.client:
            return await self._generate_with_azure(transcript, title, duration)
        
        return self._create_fallback_chunks(transcript)

    async def _generate_with_azure(
        self,
        transcript: str,
        title: str,
        duration: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Generate chunks using Azure OpenAI"""
        prompt = self._build_chunking_prompt(transcript, title, duration)
        
        try:
            logger.info(f"🧠 Sending request to Azure OpenAI (Transcript length: {len(transcript)})")
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert instructional designer. You strictly output valid JSON arrays."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4096,
                # response_format={"type": "json_object"} # Uncomment if using GPT-4-1106-preview or later
            )
            
            response_text = response.choices[0].message.content
            chunks = self._parse_chunks_response(response_text)
            
            if not chunks:
                raise ValueError("Parsed content resulted in empty chunks")

            logger.info(f"✅ Generated {len(chunks)} chunks via Azure OpenAI")
            return chunks
        
        except Exception as e:
            logger.error(f"❌ Azure OpenAI generation failed: {e}")
            logger.info("🔄 Falling back to offline chunking strategy.")
            return self._create_fallback_chunks(transcript)
    
    def _build_chunking_prompt(
        self,
        transcript: str,
        title: str,
        duration: Optional[int]
    ) -> str:
        """Build the prompt for Azure OpenAI"""
        
        duration_info = f"The total content duration is {duration} seconds." if duration else ""
        
        prompt = f"""You are an expert learning designer specializing in ADHD-friendly education. 
Your task is to break down educational content into optimal learning chunks.

Content Title: {title}
{duration_info}

Transcript:
{transcript[:12000]}  # Truncated to fit context window

Instructions:
1. Divide this content into 2-5 minute learning chunks.
2. Each chunk should focus on ONE main concept.
3. Make chunks engaging (clear structure, varied pacing).
4. Create a descriptive title for each chunk.
5. Write a brief summary (2-3 sentences).
6. Extract 3-5 key concepts per chunk.
7. Generate 2-3 multiple choice quiz questions per chunk.
8. Assess difficulty level (easy/medium/hard).

OUTPUT FORMAT:
Return ONLY a raw JSON array. Do not wrap it in markdown code blocks.
Example structure:
[
  {{
    "title": "Introduction to Concept",
    "summary": "This section covers...",
    "content": "Full text of this section...",
    "duration": 180,
    "key_concepts": ["Concept A", "Concept B"],
    "quiz_questions": [
      {{
        "question": "What is...?",
        "options": ["A) X", "B) Y", "C) Z"],
        "correct_answer": 0,
        "explanation": "Because..."
      }}
    ],
    "difficulty": "easy"
  }}
]
"""
        return prompt
    
    def _parse_chunks_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse JSON response with cleanup"""
        try:
            # Clean markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Find array brackets
            start_idx = cleaned_response.find('[')
            end_idx = cleaned_response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = cleaned_response[start_idx:end_idx]
                chunks = json.loads(json_str)
                
                # Validate
                validated_chunks = []
                for chunk in chunks:
                    if self._validate_chunk(chunk):
                        validated_chunks.append(chunk)
                return validated_chunks
            
            logger.warning("⚠️ No JSON array found in response")
            return []
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON Parse Error: {e}")
            logger.debug(f"Failed Content: {response[:100]}...")
            return []
    
    def _validate_chunk(self, chunk: Dict[str, Any]) -> bool:
        """Validate chunk structure"""
        required_fields = ['title', 'content', 'summary']
        for field in required_fields:
            if field not in chunk or not chunk[field]:
                return False
        
        # Ensure defaults
        chunk.setdefault('key_concepts', [])
        chunk.setdefault('quiz_questions', [])
        chunk.setdefault('duration', 180)
        chunk.setdefault('difficulty', 'medium')
        return True
    
    def _create_fallback_chunks(self, transcript: str) -> List[Dict[str, Any]]:
        """
        Offline Fallback: Splits text into reasonable sized chunks based on paragraphs.
        Used when Azure is not configured or fails.
        """
        logger.info("🔌 Running offline chunking logic...")
        
        # Split by double newlines to find paragraphs
        paragraphs = [p.strip() for p in transcript.split('\n\n') if p.strip()]
        if not paragraphs:
             # Fallback for dense text without double newlines
             paragraphs = [p.strip() for p in transcript.split('. ') if p.strip()]

        chunks = []
        current_chunk = []
        word_count = 0
        TARGET_WORDS_PER_CHUNK = 400  # Approx 2-3 mins reading
        
        for para in paragraphs:
            para_words = len(para.split())
            
            if word_count + para_words > TARGET_WORDS_PER_CHUNK and current_chunk:
                # Seal the chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append({
                    'title': f"Part {len(chunks) + 1}",
                    'summary': chunk_text[:150] + "...", # Simple truncation summary
                    'content': chunk_text,
                    'duration': int(word_count / 2.5), # Approx 150 wpm reading speed
                    'key_concepts': ["Offline Mode - Concepts Unavailable"],
                    'quiz_questions': [], # No AI to generate quizzes
                    'difficulty': 'medium'
                })
                current_chunk = []
                word_count = 0
            
            current_chunk.append(para)
            word_count += para_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                'title': f"Part {len(chunks) + 1}",
                'summary': chunk_text[:150] + "...",
                'content': chunk_text,
                'duration': int(word_count / 2.5),
                'key_concepts': ["Offline Mode - Concepts Unavailable"],
                'quiz_questions': [],
                'difficulty': 'medium'
            })
        
        return chunks