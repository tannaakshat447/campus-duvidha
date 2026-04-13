"""
Agent 1 — Classifier Agent
Classifies a raw complaint into one of 6 campus categories
and returns a confidence score.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, CATEGORIES, CONFIDENCE_THRESHOLD

SYSTEM_PROMPT = f"""You are the Classifier Agent in a campus complaint management system.
Your ONLY job is to classify a student complaint into exactly ONE of these categories:

{chr(10).join(f"  - {c}" for c in CATEGORIES)}

RULES:
1. Read the complaint carefully. Consider keywords, context, and intent.
2. Return your answer as a JSON object with exactly two keys:
   - "category": one of the categories listed above (exact string match)
   - "confidence": a float between 0.0 and 1.0 representing how confident you are
3. If the complaint is ambiguous or doesn't clearly fit any category, pick the closest
   match but set confidence below 0.55.
4. Consider these mappings:
   - Wi-Fi, internet, computer lab, software, email → "Other"
   - Classroom, teacher, exam, grades, syllabus, attendance → "Academic issues"
   - Bathroom, toilet, hygiene, cleaning, housekeeping → "Bathroom and hygiene"
   - Ragging, bullying, harassment, security, safety, threats → "Anti ragging and safety"
   - Building, road, furniture, AC, fan, maintenance → "Infrastructure/Maintenance"
   - Mess food, canteen, food quality, water supply in mess → "Mess and food quality"
5. Return ONLY the JSON object. No explanation, no markdown fences.

EXAMPLES:
Input: "The toilet on the 2nd floor is clogged and hasn't been cleaned."
Output: {{"category": "Bathroom and hygiene", "confidence": 0.95}}

Input: "Senior students are blocking the entrance to the hostel at night."
Output: {{"category": "Anti ragging and safety", "confidence": 0.88}}

Input: "The dal in the mess today had insects in it."
Output: {{"category": "Mess and food quality", "confidence": 0.97}}
"""


def classify(complaint_text: str) -> dict:
    """
    Classify the complaint text.
    Returns: {"category": str, "confidence": float}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.1,
        max_tokens=150,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": complaint_text},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Parse JSON from the response
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown fences
        if "```" in raw:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            result = json.loads(json_str.strip())
        else:
            result = {"category": "Needs Manual Review", "confidence": 0.0}

    # Validate category
    if result.get("category") not in CATEGORIES:
        result["category"] = "Needs Manual Review"
        result["confidence"] = min(result.get("confidence", 0.0), 0.3)

    # Apply confidence threshold
    if result.get("confidence", 0.0) < CONFIDENCE_THRESHOLD:
        result["category"] = "Needs Manual Review"

    return {
        "category": result.get("category", "Needs Manual Review"),
        "confidence": round(float(result.get("confidence", 0.0)), 2),
    }
