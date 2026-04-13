"""
Agent 4 — Router Agent
Decides which department to route the complaint to and provides
a one-line routing justification.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, DEPARTMENTS

# Build department descriptions for the system prompt
DEPT_DESC = """
AVAILABLE DEPARTMENTS AND THEIR MANDATES:

1. "Sanitation & Hygiene Dept."
   — Handles: bathroom cleaning, toilet repairs, hygiene issues, pest control,
     waste management, general housekeeping, sanitation in classrooms and hostels.

2. "Anti-Ragging & Security Cell"
   — Handles: ALL ragging cases, bullying, harassment, safety concerns, theft,
     security guard behavior, campus lighting, gate control, nighttime safety.

3. "Mess & Catering Committee"
   — Handles: mess food quality, kitchen hygiene, food contamination,
     mess timing, menu disputes, canteen services, drinking water in mess.

4. "Academic Affairs Office"
   — Handles: teaching quality, syllabus issues, examination concerns, grades,
     attendance disputes, faculty complaints, academic scheduling, lab equipment.

5. "Maintenance & Infrastructure Dept."
   — Handles: building repairs, furniture, AC/fans, plumbing (non-bathroom),
     road/parking repairs, elevators, classroom infrastructure, gym equipment.

6. "Dean of Student Welfare"
   — Handles: fee issues, administration delays, certificates, ID cards,
     IT/WiFi issues, and anything that doesn't fit the specific mandates above.
"""

SYSTEM_PROMPT = f"""You are the Router Agent in a campus complaint management system.
Your ONLY job is to route a processed complaint to the correct department.

{DEPT_DESC}

INPUT FORMAT:
  You receive a JSON with "category", "priority", and "summary" fields.

OUTPUT FORMAT:
  Return ONLY a JSON object with exactly two keys:
  - "department": the exact department name from the list above
  - "routing_reason": a single sentence explaining why this department was chosen

RULES:
1. Match the complaint to the most appropriate department based on category and content.
2. If category is "Anti ragging and safety", ALWAYS route to "Anti-Ragging & Security Cell".
3. If category is "Needs Manual Review", route to "Dean of Student Welfare".
4. If a complaint spans two departments, pick the PRIMARY one and mention the overlap in routing_reason.
5. Department names must EXACTLY match the names listed above.

EXAMPLES:
Input: {{"category": "Other", "priority": "High", "summary": "Wi-Fi outage in Block C for 3 days."}}
Output: {{"department": "Dean of Student Welfare", "routing_reason": "IT and WiFi issues are handled by the Dean of Student Welfare office."}}

Input: {{"category": "Anti ragging and safety", "priority": "Urgent", "summary": "Seniors forcing freshers to perform physical tasks at night."}}
Output: {{"department": "Anti-Ragging & Security Cell", "routing_reason": "All ragging and safety complaints are mandatorily routed to the Anti-Ragging & Security Cell."}}
"""


def route(category: str, priority: str, summary: str) -> dict:
    """
    Route the complaint to the appropriate department.
    Returns: {"department": str, "routing_reason": str}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    user_input = json.dumps({
        "category": category,
        "priority": priority,
        "summary": summary,
    })

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
            # Fallback: use config mapping
            dept = DEPARTMENTS.get(category, "Dean of Student Welfare")
            result = {"department": dept, "routing_reason": "Routed based on category mapping."}

    # Enforce hard rule: Anti-Ragging always goes to Anti-Ragging & Security Cell
    if category == "Anti ragging and safety":
        result["department"] = "Anti-Ragging & Security Cell"

    # Enforce hard rule: Needs Manual Review goes to Dean
    if category == "Needs Manual Review":
        result["department"] = "Dean of Student Welfare"

    return {
        "department": result.get("department", "Dean of Student Welfare"),
        "routing_reason": result.get("routing_reason", "Routed by AI agent."),
    }
