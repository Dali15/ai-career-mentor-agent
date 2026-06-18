"""
Intent Normalization Layer
==========================
Converts messy, informal, multilingual, or abbreviated user input into
structured skill signals before they reach the vector scoring engine.

Pipeline position:
  User Input (raw)
      ↓
  normalize_user_profile()        ← this module
      ↓
  Vector Builder (_build_user_vector)
      ↓
  Scoring Engine
      ↓
  Explanation Engine
"""

from __future__ import annotations

import re
from typing import Dict, List, Any

from .career_profiles import SKILL_VECTORS
from .domain_classifier import classify_domains

# ─────────────────────────────────────────────────────────────────────────────
# 1. NOISE WORDS — stripped before any processing
# ─────────────────────────────────────────────────────────────────────────────
NOISE_WORDS = frozenset({
    "idk", "maybe", "stuff", "etc", "things", "some", "a bit", "kind of",
    "sort of", "kinda", "dunno", "like", "umm", "uh", "hmm", "well",
    "i guess", "i think", "not sure", "whatever", "anything", "everything",
    "nothing", "something", "generally", "basically", "mostly",
    # French filler
    "peut-être", "je sais pas", "des trucs", "etc.", "bof", "ouais", "bon",
    # Arabic filler (transliterated)
    "msh", "yimkin", "shi", "ay shi",
})

# ─────────────────────────────────────────────────────────────────────────────
# 2. SYNONYM / EXPANSION MAP
#    Maps surface-form phrases → canonical skill tokens (matching SKILL_VECTORS)
# ─────────────────────────────────────────────────────────────────────────────
SYNONYM_MAP: Dict[str, List[str]] = {
    # ── English slang / abbreviations ───────────────────────────────────────
    "web dev":              ["react", "node", "apis"],
    "web development":      ["react", "node", "apis"],
    "web app":              ["react", "node", "apis"],
    "web apps":             ["react", "node", "apis"],
    "full stack":           ["react", "node", "sql", "apis"],
    "fullstack":            ["react", "node", "sql", "apis"],
    "frontend":             ["react", "javascript", "html", "css"],
    "front end":            ["react", "javascript", "html", "css"],
    "backend":              ["node", "apis", "sql"],
    "back end":             ["node", "apis", "sql"],
    "ai stuff":             ["machine learning", "python", "data analysis"],
    "ai":                   ["machine learning", "python"],
    "ml":                   ["machine learning", "python"],
    "machine learning":     ["machine learning", "python"],
    "deep learning":        ["machine learning", "python"],
    "data science":         ["data analysis", "python", "sql"],
    "data analysis":        ["data analysis", "sql", "python"],
    "data analytics":       ["data analysis", "sql"],
    "data stuff":           ["data analysis", "sql", "python"],
    "data":                 ["data analysis", "sql"],
    "sql db":               ["sql"],
    "database":             ["sql"],
    "databases":            ["sql"],
    "automation":           ["docker", "kubernetes"],
    "scripting":            ["python"],
    "devops":               ["docker", "kubernetes", "aws"],
    "cloud":                ["aws", "azure"],
    "cloud stuff":          ["aws", "azure"],
    "networking":           ["aws", "azure", "kubernetes"],
    "security":             ["aws", "azure"],
    "mobile":               ["flutter"],
    "mobile dev":           ["flutter"],
    "mobile development":   ["flutter"],
    "apps":                 ["react", "node", "flutter"],
    "app dev":              ["react", "node", "flutter"],
    "app development":      ["react", "node", "flutter"],
    "software dev":         ["python", "node", "apis"],
    "software development": ["python", "node", "apis"],
    "programming":          ["python"],
    "coding":               ["python"],
    "analytics":            ["data analysis", "sql"],
    # excel is intentionally NOT mapped — too weak a signal to drive career scoring
    "ui/ux":                ["react", "css"],
    "ui ux":                ["react", "css"],
    "design":               ["css", "html"],
    "system design":        ["system design"],
    "api":                  ["apis"],
    "apis":                 ["apis"],
    "rest api":             ["apis"],
    "restful":              ["apis"],

    # ── Natural-language intent phrases ─────────────────────────────────────
    "i build websites":     ["react", "node", "html", "css"],
    "i like data":          ["data analysis", "sql"],
    "i love data":          ["data analysis", "sql", "python"],
    "i work with data":     ["data analysis", "sql"],
    "i do data":            ["data analysis", "sql"],
    "i analyze data":       ["data analysis", "sql", "python"],
    "i build apps":         ["react", "node", "flutter"],
    "i make apps":          ["react", "node", "flutter"],
    "i develop apps":       ["react", "node", "flutter"],
    "i do automation":      ["docker", "kubernetes"],
    "i work in cloud":      ["aws", "azure"],
    "i use cloud":          ["aws", "azure"],
    "i like cloud":         ["aws", "azure"],
    "i love ai":            ["machine learning", "python"],
    "i like ai":            ["machine learning", "python"],
    "i work with ai":       ["machine learning", "python"],
    "i build models":       ["machine learning", "python"],
    "i code":               ["python"],
    "i program":            ["python"],
    "i do programming":     ["python"],
    "building apps":        ["react", "node", "apis"],
    "building websites":    ["react", "html", "css"],
    "building models":      ["machine learning", "python"],

    # ── French ──────────────────────────────────────────────────────────────
    "développement web":    ["react", "node", "apis"],
    "developpement web":    ["react", "node", "apis"],
    "dev web":              ["react", "node", "apis"],
    "analyse de données":   ["data analysis", "sql", "python"],
    "analyse de donnees":   ["data analysis", "sql", "python"],
    "intelligence artificielle": ["machine learning", "python"],
    "apprentissage automatique": ["machine learning", "python"],
    "science des données":  ["data analysis", "sql", "python"],
    "programmation":        ["python"],
    "sécurité informatique":["aws", "azure"],
    "securite informatique":["aws", "azure"],
    "cloud computing":      ["aws", "azure", "docker"],
    "applications mobiles": ["flutter"],
    "je fais du dev web":   ["react", "node", "html", "css"],
    "je fais du web":       ["react", "node", "html", "css"],
    "je fais de la data":   ["data analysis", "sql", "python"],
    "je fais de l'ia":      ["machine learning", "python"],
    "je code":              ["python"],
    "développeur web":      ["react", "node", "apis"],
    "développeur front":    ["react", "javascript", "css"],
    "développeur back":     ["node", "apis", "sql"],
    "data engineer":        ["sql", "python", "data analysis"],
    "data analyst":         ["data analysis", "sql"],
    "ingénieur devops":     ["docker", "kubernetes", "aws"],

    # ── Arabic (romanized / Unicode) ─────────────────────────────────────────
    "برمجة":                ["python"],
    "ويب":                  ["react", "node"],
    "تطوير ويب":            ["react", "node", "html"],
    "تعلم الآلة":           ["machine learning", "python"],
    "ذكاء اصطناعي":         ["machine learning", "python"],
    "تحليل بيانات":         ["data analysis", "sql"],
    "قواعد بيانات":         ["sql"],
    "تطبيقات":              ["react", "flutter"],
    "تطبيقات موبايل":       ["flutter"],
    "سحابة":                ["aws", "azure"],
    "امن المعلومات":        ["aws", "azure"],
    "شبكات":                ["aws", "kubernetes"],

    # Arabic romanized
    "barmagha":             ["python"],
    "web":                  ["react", "node"],
    "data":                 ["data analysis", "sql"],
    "zaka2 isnaa3i":        ["machine learning", "python"],
    "ta3lim ala":           ["machine learning", "python"],
    "dawkar":               ["docker"],
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. INTEREST → INTENT MAP (for the interests field)
# ─────────────────────────────────────────────────────────────────────────────
INTEREST_MAP: Dict[str, List[str]] = {
    "building apps":    ["software_development", "mobile"],
    "building websites":["web", "frontend"],
    "data":             ["data", "analytics"],
    "ai":               ["ai", "machine_learning"],
    "machine learning": ["ai", "machine_learning"],
    "cloud":            ["cloud", "devops"],
    "security":         ["security", "cloud"],
    "mobile":           ["mobile"],
    "automation":       ["devops"],
    "gaming":           ["mobile", "frontend"],
    "startups":         ["software_development", "web"],
    # French
    "intelligence artificielle": ["ai", "machine_learning"],
    "données":          ["data", "analytics"],
    "sécurité":         ["security"],
    "développement":    ["software_development"],
    # Arabic
    "برمجة":            ["software_development"],
    "بيانات":           ["data"],
    "ذكاء":             ["ai"],
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. CONFIDENCE WEIGHTS
#    How confident we are that an expansion is signal vs noise
# ─────────────────────────────────────────────────────────────────────────────
_HIGH   = 0.9
_MEDIUM = 0.75
_LOW    = 0.55

CONFIDENCE_WEIGHTS: Dict[str, float] = {
    # exact known SKILL_VECTORS keys → high confidence
    "python":           _HIGH,
    "sql":              _HIGH,
    "react":            _HIGH,
    "docker":           _HIGH,
    "kubernetes":       _HIGH,
    "aws":              _HIGH,
    "azure":            _HIGH,
    "javascript":       _HIGH,
    "html":             _HIGH,
    "css":              _HIGH,
    "flutter":          _HIGH,
    "machine learning": _HIGH,
    "node":             _HIGH,
    "node.js":          _HIGH,
    "apis":             _HIGH,
    "system design":    _HIGH,
    "data analysis":    _HIGH,
    "linux":            _HIGH,
    "cybersecurity":    _HIGH,
    "security":         _HIGH,
    "java":             _HIGH,
    "c++":              _HIGH,
    "c#":               _HIGH,
    # expanded / inferred
    "web apps":         _MEDIUM,
    "web dev":          _MEDIUM,
    "automation":       _MEDIUM,
    "cloud":            _MEDIUM,
    "data":             _MEDIUM,
    "analytics":        _MEDIUM,
    "programming":      _MEDIUM,
    "scripting":        _MEDIUM,
    "ai":               _MEDIUM,
    "ml":               _MEDIUM,
    # intent phrases → lower (more uncertain)
    "i build websites": _LOW,
    "i like data":      _LOW,
    "building apps":    _LOW,
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    """Split into canonical skill phrases, preserving multi-word terms."""
    chunks = [t.strip().lower() for t in re.split(r"[,;/|\n]+", text) if t.strip()]
    tokens: List[str] = []

    known_phrases = sorted(set(SYNONYM_MAP) | set(SKILL_VECTORS), key=len, reverse=True)

    for chunk in chunks:
        words = chunk.split()
        i = 0
        while i < len(words):
            matched = None
            for phrase in known_phrases:
                phrase_words = phrase.split()
                if words[i:i + len(phrase_words)] == phrase_words:
                    matched = phrase
                    break

            if matched:
                tokens.append(matched)
                i += len(matched.split())
            else:
                tokens.append(words[i])
                i += 1

    return [t for t in tokens if t.strip()]


def _remove_noise(tokens: List[str]) -> List[str]:
    """Drop tokens that are pure noise words or contain only noise."""
    cleaned = []
    for token in tokens:
        # Remove if the entire token is a noise word
        if token in NOISE_WORDS:
            continue
        # Remove very short standalone alphabetic tokens
        if len(token) <= 2 and token.isalpha():
            continue
        # Remove tokens whose every sub-word is a noise word
        sub_words = token.split()
        if sub_words and all(w in NOISE_WORDS for w in sub_words):
            continue
        cleaned.append(token)
    return cleaned


def _expand_token(token: str) -> List[str]:
    """
    Try to expand a token through the synonym map.
    Uses exact match first, then whole-word boundary matching.
    Returns the expanded list, or [token] if no mapping found.
    """
    # 1. Exact match first (fastest, most precise)
    if token in SYNONYM_MAP:
        return SYNONYM_MAP[token]

    # 2. Whole-word substring match: key must appear as a complete word/phrase
    # Sort by length descending to prefer more specific matches
    for key in sorted(SYNONYM_MAP.keys(), key=len, reverse=True):
        # Use word boundary matching to avoid 'data' in 'education', 'cooking' etc.
        try:
            pattern = r'(?<![\w\u0600-\u06FF])' + re.escape(key) + r'(?![\w\u0600-\u06FF])'
            if re.search(pattern, token):
                return SYNONYM_MAP[key]
        except re.error:
            continue

    # 3. Return the original token — vector builder will try it directly
    return [token]


def _score_confidence(raw_token: str, expanded: List[str]) -> float:
    """Return a confidence score for the expansion."""
    # Check direct confidence weight table
    if raw_token in CONFIDENCE_WEIGHTS:
        return CONFIDENCE_WEIGHTS[raw_token]
    # If expansion succeeded (token changed), use medium confidence
    if expanded != [raw_token]:
        return _MEDIUM
    # Unknown token that wasn't expanded
    return _LOW


def _extract_intents(skills_text: str, interests_text: str) -> List[str]:
    """
    Detect high-level career intents from combined free-text phrases.
    Used to surface intent labels for the UI/explanation layer.
    """
    combined = (skills_text + " " + interests_text).lower()
    intents = []

    intent_patterns = [
        (r"\b(web|frontend|front.end|html|css|react|vue|angular)\b",  "web_development"),
        (r"\b(backend|back.end|server|api|node|flask|django|spring)\b","backend_development"),
        (r"\b(data|sql|analytics|pandas|tableau|power bi)\b",   "data_analytics"),
        (r"\b(machine.learning|ml|ai|deep.learning|neural|nlp|gpt)\b","artificial_intelligence"),
        (r"\b(cloud|aws|azure|gcp|kubernetes|terraform|serverless)\b", "cloud_devops"),
        (r"\b(docker|ci.cd|pipeline|devops|jenkins|ansible)\b",       "devops"),
        (r"\b(mobile|flutter|swift|kotlin|android|ios|react.native)\b","mobile_development"),
        (r"\b(security|cybersecurity|pentest|firewall|siem)\b",       "cybersecurity"),
        # French
        (r"\b(développement|programmation|logiciel|données|intelligence)\b", "software_development"),
        # Arabic
        (r"(برمجة|ويب|بيانات|ذكاء)", "software_development"),
    ]

    seen = set()
    for pattern, intent in intent_patterns:
        if re.search(pattern, combined) and intent not in seen:
            intents.append(intent)
            seen.add(intent)

    return intents


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def normalize_user_profile(
    education: str,
    skills: str,
    interests: str,
) -> Dict[str, Any]:
    """
    Normalize raw user input into structured skill signals.

    Parameters
    ----------
    education  : raw education string (e.g. "CS Degree")
    skills     : raw skills string   (e.g. "sql python maybe data stuff")
    interests  : raw interests string (e.g. "i like ai and web apps")

    Returns
    -------
    {
        "clean_skills"     : List[str],   # canonical skill tokens for vector builder
        "clean_interests"  : List[str],   # intent labels for interest boost
        "detected_intents" : List[str],   # high-level career intents
        "confidence_map"   : Dict[str, float],  # confidence per skill token
        "normalized_skills_text"   : str, # comma-joined, ready for vector builder
        "normalized_interests_text": str, # comma-joined, ready for interest boost
    }
    """
    # ── Input validation: Enforce maximum field lengths ──────────────────
    MAX_FIELD_LENGTH = 5000
    education = str(education)[:MAX_FIELD_LENGTH].strip()
    skills = str(skills)[:MAX_FIELD_LENGTH].strip()
    interests = str(interests)[:MAX_FIELD_LENGTH].strip()
    
    # ── 1. Education hints → extra skill signals ──────────────────────────
    edu_lower = education.lower()
    edu_skills: List[str] = []
    if any(w in edu_lower for w in ["computer science", "cs", "informatique", "علوم الحاسب"]):
        edu_skills += ["python", "sql", "apis"]
    elif any(w in edu_lower for w in ["data", "statistics", "maths"]):
        edu_skills += ["python", "data analysis", "sql"]
    elif any(w in edu_lower for w in ["design", "ux", "ui"]):
        edu_skills += ["css", "html", "react"]
    elif any(w in edu_lower for w in ["electrical", "hardware", "network"]):
        edu_skills += ["aws", "kubernetes"]

    # ── 2. Tokenize + remove noise ────────────────────────────────────────
    raw_skill_tokens    = _remove_noise(_tokenize(skills))
    raw_interest_tokens = _remove_noise(_tokenize(interests))

    # ── 3. Expand tokens through synonym map ──────────────────────────────
    clean_skills: List[str] = []
    confidence_map: Dict[str, float] = {}

    # Add education-derived signals first (high confidence)
    for skill in edu_skills:
        if skill not in clean_skills:
            clean_skills.append(skill)
            confidence_map[skill] = _HIGH

    for raw_token in raw_skill_tokens:
        expanded = _expand_token(raw_token)
        conf     = _score_confidence(raw_token, expanded)
        for skill in expanded:
            skill = skill.strip()
            if not skill:
                continue
            if skill not in clean_skills:
                clean_skills.append(skill)
            # Take the max confidence if the same skill appears via different paths
            confidence_map[skill] = max(confidence_map.get(skill, 0.0), conf)

    # ── 4. Expand interest tokens ─────────────────────────────────────────
    clean_interests: List[str] = []
    for raw_token in raw_interest_tokens:
        # Check interest map first
        if raw_token in INTEREST_MAP:
            clean_interests.extend(INTEREST_MAP[raw_token])
        else:
            # Fallback: expand through synonym map and take the first token
            expanded = _expand_token(raw_token)
            clean_interests.extend(expanded)

    # deduplicate while preserving order
    seen_i: set = set()
    clean_interests = [x for x in clean_interests if not (x in seen_i or seen_i.add(x))]

    # ── 5. Detect high-level intents ──────────────────────────────────────
    detected_intents = _extract_intents(skills, interests)

    # ── 6. Build normalized text strings for the vector builder ───────────
    normalized_skills_text    = ", ".join(clean_skills)
    normalized_interests_text = ", ".join(clean_interests)

    return {
        "clean_skills":              clean_skills,
        "clean_interests":           clean_interests,
        "detected_intents":          detected_intents,
        "domains":                   classify_domains(clean_skills, detected_intents, interests),
        "confidence_map":            confidence_map,
        "normalized_skills_text":    normalized_skills_text,
        "normalized_interests_text": normalized_interests_text,
    }
