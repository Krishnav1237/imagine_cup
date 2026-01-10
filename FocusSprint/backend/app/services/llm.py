"""
LLM service abstraction.
Uses Ollama text generation API.
"""

import httpx
import logging
from typing import Optional
import json
from typing import Any, Dict

from app.config import settings

logger = logging.getLogger("LLM")


DEFAULT_MODEL = getattr(
    settings,
    "OLLAMA_MODEL",
    "llama3:8b-instruct-q4_K_M",
)


def generate_text(
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
) -> str:
    """
    Generate text using Ollama.

    Returns:
        Generated text (string)
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    if system_prompt:
        payload["system"] = system_prompt

    if max_tokens:
        payload["options"]["num_predict"] = max_tokens

    try:
        resp = httpx.post(
            f"{settings.OLLAMA_URL}/api/generate",
            json=payload,
            timeout=300,
        )
        resp.raise_for_status()

        data = resp.json()
        output = data.get("response")

        if not output:
            raise RuntimeError("LLM returned empty response")

        return output.strip()

    except Exception as e:
        logger.error(f"❌ LLM generation failed: {e}")
        raise RuntimeError("LLM generation failed") from e

def run_llm_json(
    prompt: str,
    system_prompt: str,
    max_retries: int = 2,
) -> Dict[str, Any]:
    """
    Run LLM and force JSON output.
    Used by RAG + video pipelines.
    """

    last_error = None

    for attempt in range(max_retries + 1):
        try:
            raw = generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.0,   # deterministic
            )

            # Try direct JSON
            return json.loads(raw)

        except Exception as e:
            last_error = e

    raise RuntimeError(
        f"LLM failed to return valid JSON after {max_retries + 1} attempts"
    ) from last_error