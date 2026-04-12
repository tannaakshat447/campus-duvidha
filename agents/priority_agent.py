"""
Agent 2 — Priority Agent
Assigns a priority level (Low / Medium / High / Urgent) based on
the complaint text and the category determined by Agent 1.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

SYSTEM_PROMPT = """You are the Priority Agent in a campus complaint management system.
Your ONLY job is to assign a priority level to a student complaint.

PRIORITY LEVELS (choose exactly one):
  - "Urgent"  — life-threatening, safety risk, ragging, harassment, medical emergency
  - "High"    — essential services down (water, electricity, internet outage affecting many),
                 security concerns, blocked access
  - "Medium"  — quality-of-life issues (food quality, cleanliness, minor maintenance,
                 academic scheduling, slow Wi-Fi)
  - "Low"     — suggestions, general feedback, cosmetic issues, minor inconveniences

HARD RULES (override everything else):
  1. Category "Anti-Ragging" → ALWAYS "Urgent", no exceptions.
  2. Water outage or electricity outage → at least "High".
  3. Words like "threat", "unsafe", "emergency", "assault", "suicide", "danger" → "Urgent".
  4. Food quality complaints without health risk → "Medium".
  5. Suggestions or feature requests → "Low".

INPUT FORMAT:
  You receive a JSON with "complaint" and "category" fields.

OUTPUT FORMAT:
  Return ONLY a JSON object with exactly two keys:
  - "priority": one of "Low", "Medium", "High", "Urgent"
  - "reason": a single sentence explaining why this priority was assigned

EXAMPLES:
Input: {"complaint": "Seniors are forcing freshers to do their homework", "category": "Anti-Ragging"}
Output: {"priority": "Urgent", "reason": "Anti-ragging complaints are always treated as Urgent per policy."}

Input: {"complaint": "The mess food had insects in it today", "category": "Hostel & Mess"}
Output: {"priority": "High", "reason": "Food contamination poses a direct health risk to students."}

Input: {"complaint": "Library closes too early on weekends", "category": "Administration"}
Output: {"priority": "Low", "reason": "Scheduling suggestion with no immediate impact on safety or services."}
"""


def assign_priority(complaint_text: str, category: str) -> dict:
    """
    Assign priority based on complaint text and category.
    Returns: {"priority": str, "reason": str}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    user_input = json.dumps({"complaint": complaint_text, "category": category})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.1,
        max_tokens=200,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            result = json.loads(json_str.strip())
        else:
            result = {"priority": "Medium", "reason": "Could not parse agent response; defaulting to Medium."}

    valid_priorities = {"Low", "Medium", "High", "Urgent"}
    if result.get("priority") not in valid_priorities:
        result["priority"] = "Medium"

    # Enforce hard rule: Anti-Ragging is always Urgent
    if category == "Anti-Ragging":
        result["priority"] = "Urgent"
        result["reason"] = "Anti-ragging complaints are always classified as Urgent per institutional policy."

    return {
        "priority": result.get("priority", "Medium"),
        "reason": result.get("reason", "Priority assigned by AI agent."),
    }
