"""
Vision Language Model (VLM) Processor.
Provides real visual analysis using OpenAI Vision API with graceful fallback.
"""
import base64
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger("VLMProcessor")


class VLMProcessor:
    """
    Vision Language Model processor using OpenAI GPT-4V or Azure OpenAI.
    Falls back to rule-based analysis when API unavailable.
    """
    
    def __init__(self):
        self.client = None
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize OpenAI client based on available configuration."""
        try:
            # Check for Azure OpenAI first
            azure_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            
            if azure_key and azure_endpoint:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=azure_key,
                    api_version="2024-02-15-preview",
                    azure_endpoint=azure_endpoint
                )
                self.model = azure_deployment
                logger.info("✅ VLM initialized with Azure OpenAI")
                return
            
            # Fall back to standard OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=openai_key)
                self.model = os.getenv("VLM_MODEL", "gpt-4o")
                logger.info(f"✅ VLM initialized with OpenAI ({self.model})")
                return
            
            logger.warning("⚠️ No VLM API keys found. Using fallback analysis.")
            
        except ImportError:
            logger.warning("⚠️ OpenAI SDK not installed. Using fallback analysis.")
        except Exception as e:
            logger.error(f"❌ VLM initialization failed: {e}")
    
    @property
    def is_available(self) -> bool:
        """Check if VLM API is available."""
        return self.client is not None
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for API request."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.warning(f"Image not found: {image_path}")
                return None
            
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            return None
    
    def _get_image_media_type(self, image_path: str) -> str:
        """Get media type for image."""
        ext = Path(image_path).suffix.lower()
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }
        return media_types.get(ext, "image/jpeg")

    async def analyze_frames(self, frames: List[str]) -> Dict[str, Any]:
        """
        Analyze video frames using Vision LLM.
        
        Args:
            frames: List of paths to frame images
            
        Returns:
            Dictionary with visual analysis results
        """
        if not frames:
            return self._fallback_analysis("No frames provided")
        
        if not self.is_available:
            return self._fallback_analysis("VLM not configured")
        
        try:
            # Select key frames (first, middle, last) to reduce API costs
            selected_frames = self._select_key_frames(frames)
            
            # Build message with images
            content = [
                {
                    "type": "text",
                    "text": """Analyze these video frames and provide:
1. A concise title (max 10 words) describing the main topic
2. A brief summary (2-3 sentences) of what's being shown
3. 3-5 bullet points of key visual concepts
4. 3-5 focus words for learning

Respond in JSON format:
{
    "title": "...",
    "summary": "...",
    "bullets": ["...", "..."],
    "focus_words": ["...", "..."],
    "visual_context": "Brief description of visual elements",
    "key_elements": ["element1", "element2"]
}"""
                }
            ]
            
            # Add images
            for frame_path in selected_frames:
                base64_image = self._encode_image(frame_path)
                if base64_image:
                    media_type = self._get_image_media_type(frame_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{base64_image}",
                            "detail": "low"  # Use low detail to reduce costs
                        }
                    })
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": content}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            # Try to parse as JSON
            import json
            try:
                # Clean up response if wrapped in markdown code block
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0]
                
                result = json.loads(result_text.strip())
                logger.info(f"✅ VLM analysis complete: {result.get('title', 'Untitled')}")
                return result
            except json.JSONDecodeError:
                logger.warning("VLM response not valid JSON, using text extraction")
                return {
                    "title": "Visual Analysis",
                    "summary": result_text[:200],
                    "bullets": [result_text[:100]],
                    "focus_words": ["visual", "content", "analysis"],
                    "visual_context": result_text[:300],
                    "key_elements": []
                }
                
        except Exception as e:
            logger.error(f"❌ VLM analysis failed: {e}")
            return self._fallback_analysis(str(e))
    
    def _select_key_frames(self, frames: List[str], max_frames: int = 3) -> List[str]:
        """Select key frames from a list (first, middle, last)."""
        if len(frames) <= max_frames:
            return frames
        
        indices = [0, len(frames) // 2, len(frames) - 1]
        return [frames[i] for i in indices if i < len(frames)]
    
    def _fallback_analysis(self, reason: str = "") -> Dict[str, Any]:
        """
        Provide fallback analysis when VLM is unavailable.
        Uses generic but accurate descriptions.
        """
        logger.info(f"Using fallback VLM analysis. Reason: {reason}")
        
        return {
            "title": "Video Content Segment",
            "summary": "This segment contains educational content. Visual analysis requires API configuration.",
            "bullets": [
                "Content segment identified",
                "Visual elements present",
                "Requires VLM API for detailed analysis"
            ],
            "focus_words": ["learning", "content", "segment"],
            "visual_context": "Visual context analysis requires VLM API configuration (OPENAI_API_KEY or AZURE_OPENAI_* environment variables)",
            "key_elements": [],
            "fallback": True,
            "fallback_reason": reason
        }


# Global singleton
vlm_processor = VLMProcessor()


# Backwards-compatible function for existing imports
async def analyze_frames(frames: List) -> Dict:
    """
    Analyze video frames using VLM.
    Backwards-compatible wrapper for vlm_processor.
    """
    return await vlm_processor.analyze_frames(frames)
