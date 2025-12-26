from typing import List
from app.services.document_extraction import extract_layout_units
from app.services.chunking.ollama_card_compiler import compile_cards
from app.services.chunking.chunk_schema import ChunkCard


async def run_document_pipeline(
    file_path: str,
    document_title: str
) -> List[ChunkCard]:
    layout_units = extract_layout_units(file_path)

    if not layout_units:
        raise RuntimeError("No layout units extracted")

    return await compile_cards(
        structured_units=layout_units,
        document_title=document_title
    )
