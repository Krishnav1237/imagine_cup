from typing import List, Dict

def select_groups_by_char_budget(
    groups: List[Dict],
    max_context_chars: int = 10_000,
    max_group_chars: int = 2_500,
) -> List[Dict]:
    """
    Selects groups dynamically based on total character budget.

    - Preserves relevance order
    - Trims oversized groups
    - Stops before exceeding total context budget
    """

    selected = []
    total_chars = 0

    for group in groups:
        text = group.get("text", "")
        if not text:
            continue

        # Trim overly large individual groups
        if len(text) > max_group_chars:
            text = text[:max_group_chars]
            group = {**group, "text": text}

        group_size = len(text)

        if total_chars + group_size > max_context_chars:
            break

        selected.append(group)
        total_chars += group_size

    return selected
