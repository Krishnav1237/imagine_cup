import re
from typing import List, Tuple

# Hard-ban patterns (always remove, never learning content)
ACADEMIC_NOISE_PATTERNS = [
    # Duration & timing
    r"\b(Duration|Time)\s*:\s*\d+\s*(min|hour|hr|sec|minutes|hours|seconds)",
    r"\b(Estimated\s+)?Duration\b.*?(?=\n|$)",
    
    # Credits & grades
    r"\bCredits?\s*:\s*\d+",
    r"\b(Credit\s+)?(Points?|Hours?)\s*:\s*\d+",
    
    # Course metadata
    r"\bCourse\s+(Code|ID|Number)\s*:\s*[A-Z]{1,3}\d{3,4}",
    r"\b([A-Z]{2,3}\d{3,4})\b",  # Catch course codes like AI3201, CSE305
    r"\bCourse\s+(Name|Title)\s*:",
    
    # Academic context
    r"\bSemester\s*:\s*\w+",
    r"\b(Spring|Summer|Fall|Winter)\s+\d{4}",
    r"\bBatch\s*:\s*\d{4}",
    r"\bYear\s*:\s*\d+",
    
    # People & institutions
    r"\bInstructor\s*:\s*[^\n]+",
    r"\bProfessor\s*:\s*[^\n]+",
    r"\bTeacher\s*:\s*[^\n]+",
    r"\bUniversity\s*:\s*[^\n]+",
    r"\bDepartment\s*:\s*[^\n]+",
    r"\bSchool\s*:\s*[^\n]+",
    
    # Administrative sections
    r"\bSyllabus\b.*?(?=\n\n|\n[A-Z]|$)",
    r"\bLearning\s+Objectives\b.*?(?=\n\n|\n[A-Z]|$)",
    r"\bAssessment\s+(Pattern|Criteria|Rubric)\b.*?(?=\n\n|\n[A-Z]|$)",
    r"\b(Grading|Evaluation)\s+(Criteria|Pattern)\b.*?(?=\n\n|\n[A-Z]|$)",
    r"\bPrerequisites?\b.*?(?=\n|$)",
    r"\bOffice\s+Hours\b.*?(?=\n|$)",
    r"\bContact\s+Information\b.*?(?=\n\n|\n[A-Z]|$)",
    r"\bResources?\s+(and\s+)?References?\b.*?(?=\n\n|\n[A-Z]|$)",
    
    # Slide headers that are metadata
    r"\b(Course\s+)?Overview\b",
    r"\bWelcome\b",
    r"\bIntroduction\b",
    r"\bTable\s+of\s+Contents\b",
    r"\bAgenda\b",
    r"\bOutline\b",
]

# Forbidden terms in final output (post-filter)
FORBIDDEN_OUTPUT_TERMS = [
    "duration", "credits", "semester", "batch", "year",
    "course", "university", "instructor", "professor",
    "department", "school", "office hours", "grading",
    "assessment pattern", "prerequisites", "contact",
]

def remove_academic_noise(text: str) -> str:
    """
    Remove course metadata, administrative info, and context.
    Preserves learning content.
    
    Args:
        text: Raw extracted text
    
    Returns:
        Cleaned text without academic noise
    """
    original_len = len(text)
    
    for pattern in ACADEMIC_NOISE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n+', '\n', text)  # Multiple newlines → single
    text = re.sub(r' +', ' ', text)  # Multiple spaces → single
    text = text.strip()
    
    removed_pct = ((original_len - len(text)) / original_len * 100) if original_len > 0 else 0
    return text


def contains_forbidden_terms(text: str) -> Tuple[bool, List[str]]:
    """
    Check if text contains forbidden academic noise terms.
    
    Args:
        text: Text to check
    
    Returns:
        (has_noise: bool, found_terms: List[str])
    """
    found = []
    text_lower = text.lower()
    
    for term in FORBIDDEN_OUTPUT_TERMS:
        if term in text_lower:
            found.append(term)
    
    return len(found) > 0, found


def is_academic_metadata_line(line: str) -> bool:
    """
    Determine if a single line is pure metadata (not learning content).
    
    Args:
        line: Single line of text
    
    Returns:
        True if line is metadata, False if it's content
    """
    line_lower = line.lower().strip()
    
    # Empty or too short
    if not line_lower or len(line_lower) < 5:
        return True
    
    # Explicit metadata patterns
    metadata_indicators = [
        "duration:", "credits:", "course code:", "instructor:",
        "semester:", "university:", "department:", "prerequisites:",
        "assessment pattern:", "grading:", "contact:", "office hours:",
        "syllabus", "learning objectives", "course overview",
    ]
    
    for indicator in metadata_indicators:
        if indicator in line_lower:
            return True
    
    return False


def filter_bullets(bullets: List[str]) -> List[str]:
    """
    Filter out metadata-only bullets, keep learning content.
    
    Args:
        bullets: List of bullet points
    
    Returns:
        Filtered bullet list (knowledge only)
    """
    filtered = []
    
    for bullet in bullets:
        if not is_academic_metadata_line(bullet):
            # Also apply noise removal at bullet level
            cleaned = remove_academic_noise(bullet)
            if cleaned and len(cleaned) > 5:
                filtered.append(cleaned)
    
    return filtered
