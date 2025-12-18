import re
from collections import Counter
from typing import List

# English stopwords (expanded)
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
    'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
    'as', 'by', 'from', 'with', 'about', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'etc', 'than', 'if',
    'not', 'no', 'yes', 'so', 'such', 'all', 'each', 'every', 'both', 'few',
    'more', 'most', 'other', 'some', 'any', 'many', 'much', 'your', 'their',
    'also', 'just', 'been', 'very', 'should', 'would', 'could', 'must',
    'use', 'used', 'uses', 'using', 'example', 'examples', 'etc',
}

# Junk placeholder terms (never concepts)
JUNK_CONCEPTS = {
    'focus', 'attention', 'dopamine', 'motivation', 'engagement',
    'learning', 'understanding', 'knowledge', 'skill', 'ability',
    'important', 'key', 'main', 'thing', 'stuff', 'point',
    'overall', 'general', 'basic', 'advanced', 'level',
}


def extract_key_concepts(bullets: List[str], max_concepts: int = 5) -> List[str]:
    """
    Extract REAL key concepts (domain-specific nouns + repeated terms).
    Deterministic, rule-based — no AI guessing.

    Args:
        bullets: List of bullet point strings
        max_concepts: Maximum number of concepts to return

    Returns:
        List of real domain concepts
    """
    if not bullets:
        return []

    # Strategy: extract all noun phrases and multi-word terms
    phrase_counter = Counter()
    word_counter = Counter()

    for bullet in bullets:
        # Extract capitalized terms (likely nouns)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', bullet)
        for term in capitalized:
            if term not in JUNK_CONCEPTS and len(term) > 2:
                phrase_counter[term] += 1

        # Extract domain-specific patterns (algorithms, methods, terms)
        # e.g., "Binary Search", "Quick Sort", "Machine Learning"
        technical = re.findall(r'\b(?:[A-Z][a-z]+\s+)+[A-Z][a-z]+\b', bullet)
        for term in technical:
            if term not in JUNK_CONCEPTS and len(term) > 4:
                phrase_counter[term] += 1

        # Extract regular words (fallback)
        words = re.findall(r'\b[a-z]+\b', bullet.lower())
        for word in words:
            if word not in STOPWORDS and word not in JUNK_CONCEPTS and len(word) > 3:
                word_counter[word] += 1

    # Combine: prefer multi-word phrases, then single words
    concepts = []

    # Add top capitalized/technical phrases first
    for phrase, count in phrase_counter.most_common(max_concepts * 2):
        if count >= 1:  # Appears at least once
            concepts.append(phrase)

    # Fill gaps with single words if needed
    if len(concepts) < max_concepts:
        for word, count in word_counter.most_common(max_concepts * 3):
            if count >= 1 and word not in str(concepts).lower():
                concepts.append(word.capitalize())

    return concepts[:max_concepts]


def generate_one_liner(title: str, bullets: List[str]) -> str:
    """
    Generate a strict one-line summary: ≤ 20 words, no metadata.

    Args:
        title: Slide title (usually the topic)
        bullets: Bullet points (the content)

    Returns:
        One-line summary string
    """
    if not title and not bullets:
        return "No content."

    # Prefer a compound summary from title + first bullet
    if title and bullets:
        # Combine title + first bullet idea
        combined = f"{title}. {bullets[0]}"
    elif title:
        combined = title
    else:
        combined = bullets[0]

    # Enforce ≤ 20 words
    words = combined.split()[:20]
    summary = " ".join(words)

    # Ensure proper ending
    if not summary.endswith(('.', '!', '?')):
        summary += "."

    return summary
