"""
Keyword-based heuristic fallback — used when no OpenAI API key is available.
Provides ~75% accuracy using rule-based keyword matching.
"""

import re
from config import CATEGORIES, DEPARTMENTS

# ── Keyword maps ────────────────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "Infrastructure": [
        "building", "road", "parking", "light", "lighting", "furniture",
        "chair", "desk", "bench", "ac", "air conditioning", "fan",
        "elevator", "lift", "construction", "leak", "roof", "wall",
        "broken", "repair", "maintenance", "classroom", "door", "window",
        "paint", "ground", "garden", "drainage",
    ],
    "Academic": [
        "teacher", "professor", "faculty", "exam", "grade", "marks",
        "syllabus", "attendance", "lecture", "class", "lab", "assignment",
        "project", "deadline", "timetable", "schedule", "course",
        "semester", "result", "viva", "practical", "plagiarism",
    ],
    "Hostel & Mess": [
        "hostel", "mess", "food", "water", "laundry", "room",
        "roommate", "warden", "curfew", "menu", "canteen", "hygiene",
        "pest", "cockroach", "insect", "rat", "dirty", "clean",
        "bathroom", "toilet", "shower", "geyser", "hot water",
        "mattress", "bed", "pillow", "dal", "roti", "rice",
        "paani", "khana", "ganda",
    ],
    "Anti-Ragging": [
        "ragging", "bully", "bullying", "harass", "harassment",
        "senior", "threat", "threaten", "intimidat", "assault",
        "force", "forced", "pushup", "push-up", "abuse",
        "humiliat", "scare", "scared", "afraid", "beat",
    ],
    "Administration": [
        "fee", "fees", "admission", "certificate", "id card",
        "library", "scholarship", "refund", "document", "transfer",
        "registrar", "form", "verification", "receipt", "payment",
        "transcript", "degree", "convocation",
    ],
    "IT & Network": [
        "wifi", "wi-fi", "internet", "network", "lan", "computer",
        "lab", "software", "email", "portal", "erp", "lms",
        "printer", "password", "login", "server", "website",
        "online", "download", "upload", "slow",
    ],
}

PRIORITY_KEYWORDS = {
    "Urgent": [
        "ragging", "harass", "threat", "assault", "unsafe", "emergency",
        "danger", "suicide", "abuse", "attack", "scared", "afraid",
        "force", "bullying", "intimidat",
    ],
    "High": [
        "water outage", "no water", "paani nahi", "electricity",
        "power cut", "no power", "outage", "flood", "fire",
        "health risk", "insect", "cockroach", "rat", "contamina",
        "broken pipe", "security", "theft", "stolen",
    ],
    "Medium": [
        "food", "mess", "clean", "dirty", "slow", "delay",
        "quality", "schedule", "timing", "temperature", "noise",
        "maintenance",
    ],
}

SENTIMENT_KEYWORDS = {
    "Angry": [
        "!!!", "wtf", "damn", "hell", "stupid", "idiot", "useless",
        "pathetic", "worst", "disgusting", "terrible", "saala",
        "bakwas", "nonsens",
    ],
    "Distressed": [
        "scared", "afraid", "helpless", "don't know what to do",
        "can't take", "please help", "crying", "depressed",
        "anxious", "panic", "unsafe", "dar lagta", "bahut bura",
    ],
    "Frustrated": [
        "again", "still", "yet", "how long", "kab tak", "fed up",
        "tired of", "annoyed", "seriously", "come on", "fix it",
        "tang", "pareshaan", "bahut ho gaya",
    ],
}


def _match_score(text: str, keywords: list) -> int:
    """Count how many keywords appear in the text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def classify_fallback(complaint_text: str) -> dict:
    """Keyword-based classification."""
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = _match_score(complaint_text, keywords)

    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]
    total_matches = sum(scores.values())

    if best_score == 0:
        return {"category": "Needs Manual Review", "confidence": 0.2}

    confidence = min(0.85, 0.4 + (best_score / max(total_matches, 1)) * 0.5)
    if confidence < 0.55:
        return {"category": "Needs Manual Review", "confidence": round(confidence, 2)}

    return {"category": best_cat, "confidence": round(confidence, 2)}


def priority_fallback(complaint_text: str, category: str) -> dict:
    """Keyword-based priority assignment."""
    if category == "Anti-Ragging":
        return {"priority": "Urgent", "reason": "Anti-ragging complaints are always Urgent."}

    for prio in ["Urgent", "High", "Medium"]:
        if _match_score(complaint_text, PRIORITY_KEYWORDS[prio]) > 0:
            return {"priority": prio, "reason": f"Keyword match triggered {prio} priority."}

    return {"priority": "Low", "reason": "No urgency indicators detected."}


def summarize_fallback(complaint_text: str) -> dict:
    """Simple extractive summarization fallback."""
    text = complaint_text.strip()
    # Take first sentence or first 100 chars
    sentences = re.split(r'[.!?]', text)
    first_sentence = sentences[0].strip() if sentences else text
    if len(first_sentence) > 120:
        first_sentence = first_sentence[:117] + "..."
    if not first_sentence:
        first_sentence = text[:100]
    return {"summary": first_sentence}


def route_fallback(category: str) -> dict:
    """Direct mapping based on category."""
    dept = DEPARTMENTS.get(category, "Dean of Student Welfare")
    return {"department": dept, "routing_reason": f"Routed to {dept} based on category '{category}'."}


def sentiment_fallback(complaint_text: str) -> dict:
    """Keyword-based sentiment detection."""
    # Check in order of severity
    if _match_score(complaint_text, SENTIMENT_KEYWORDS["Angry"]) >= 2:
        return {"sentiment": "Angry", "flag": True}
    if _match_score(complaint_text, SENTIMENT_KEYWORDS["Distressed"]) > 0:
        return {"sentiment": "Distressed", "flag": True}
    if _match_score(complaint_text, SENTIMENT_KEYWORDS["Frustrated"]) > 0:
        return {"sentiment": "Frustrated", "flag": False}
    # Check for ALL CAPS (sign of anger)
    upper_ratio = sum(1 for c in complaint_text if c.isupper()) / max(len(complaint_text), 1)
    if upper_ratio > 0.5 and len(complaint_text) > 20:
        return {"sentiment": "Angry", "flag": True}
    return {"sentiment": "Neutral", "flag": False}
