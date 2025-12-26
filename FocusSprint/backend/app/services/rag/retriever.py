from typing import List, Dict
import numpy as np

from .embedder import embed_texts
from .vector_store import VectorStore


def retrieve_relevant_units(
    structured_units: List[Dict],
    top_k: int = 6,
    max_groups: int = 20,
) -> List[Dict]:
    """
    Groups layout-extracted units into semantically coherent chunks.
    """

    if not structured_units:
        return []

    # ─────────────────────────────────────────────
    # 1. Extract text payloads
    # ─────────────────────────────────────────────
    texts = [u["text"] for u in structured_units if u.get("text")]

    if not texts:
        return []

    # ─────────────────────────────────────────────
    # 2. Embed ONCE (singleton embedder)
    # ─────────────────────────────────────────────
    embeddings = embed_texts(texts)

    dim = embeddings.shape[1]
    store = VectorStore(dim)

    # Store original units as payloads
    store.add(embeddings, structured_units)

    used_indices = set()
    groups: List[Dict] = []

    # ─────────────────────────────────────────────
    # 3. Greedy semantic grouping
    # ─────────────────────────────────────────────
    for idx in range(len(structured_units)):
        if idx in used_indices:
            continue

        query_vec = embeddings[idx : idx + 1]
        neighbors = store.search(query_vec, top_k=top_k)

        group_units = []
        for unit in neighbors:
            unit_idx = structured_units.index(unit)
            if unit_idx not in used_indices:
                used_indices.add(unit_idx)
                group_units.append(unit)

        if group_units:
            groups.append({
                "text": "\n".join(u["text"] for u in group_units),
                "source": group_units[0].get("source"),
            })

        if len(groups) >= max_groups:
            break

    return groups
