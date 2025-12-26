import re
from collections import Counter


def extract_key_concepts(bullets: list[str], limit: int = 5) -> list[str]:
    words = []
    for b in bullets:
        tokens = re.findall(r"[A-Za-z][A-Za-z\-]{2,}", b)
        words.extend(tokens)

    blacklist = {"using", "based", "used", "value", "values", "data"}
    freq = Counter(w for w in words if w.lower() not in blacklist)

    return [w for w, _ in freq.most_common(limit)]


def generate_one_liner(title: str, bullets: list[str]) -> str:
    if not bullets:
        return title

    core = bullets[0]
    sentence = core.rstrip(".")
    return f"{sentence}."
