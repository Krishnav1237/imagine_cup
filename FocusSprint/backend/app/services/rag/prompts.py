SYSTEM_PROMPT = """
You are a knowledge distillation engine.

Rules:
- Extract ONLY real, transferable knowledge
- Remove academic framing and instructional language
- Merge fragmented ideas into coherent concepts
- Ignore layout unless conceptually relevant
- No references to slides, pages, lectures, or courses
- Output STRICT JSON only
"""

CHUNK_PROMPT = """
Using ONLY the context below, generate learning chunks.

Context:
{context}

Return JSON in this schema:

{{
  "chunks": [
    {{
      "title": "string",
      "summary": "string",
      "bullets": ["string"],
      "focus_words": ["string"]
    }}
  ]
}}
"""
