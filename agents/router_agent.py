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

1. "Maintenance & Infrastructure Dept."
   — Handles: building repairs, furniture, AC/fans, plumbing (non-hostel),
     road/parking, lighting, campus grounds, elevators, classroom facilities.

2. "Academic Affairs Office"
   — Handles: teaching quality, syllabus issues, examination concerns, grades,
     attendance disputes, faculty complaints, academic scheduling, lab equipment.

3. "Hostel Warden & Mess Committee"
   — Handles: hostel room issues, roommate conflicts, mess food quality,
     water supply in hostels, laundry, hostel security, mess timing, menu.

4. "Anti-Ragging Cell"
   — Handles: ALL ragging, bullying, harassment, intimidation, threats by seniors,
     mental harassment, physical abuse. This takes absolute priority.

5. "Registrar / Admin Office"
   — Handles: fees, admissions, certificates, ID cards, library memberships,
     scholarships, document verification, transfer requests.

6. "IT Services & Network Dept."
   — Handles: Wi-Fi, internet, LAN, computer labs, email/portal access,
     software licenses, printer issues, ERP/LMS problems.

7. "Dean of Student Welfare"
   — Handles: anything that doesn't clearly fit above, cross-department issues,
     general welfare, mental health referrals, complaints needing manual review.
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
2. If category is "Anti-Ragging", ALWAYS route to "Anti-Ragging Cell".
3. If category is "Needs Manual Review", route to "Dean of Student Welfare".
4. If a complaint spans two departments, pick the PRIMARY one and mention the overlap in routing_reason.
5. Department names must EXACTLY match the names listed above.

EXAMPLES:
Input: {{"category": "IT & Network", "priority": "High", "summary": "Wi-Fi outage in Block C for 3 days."}}
Output: {{"department": "IT Services & Network Dept.", "routing_reason": "Wi-Fi connectivity issues fall under IT Services jurisdiction."}}

Input: {{"category": "Anti-Ragging", "priority": "Urgent", "summary": "Seniors forcing freshers to perform physical tasks at night."}}
Output: {{"department": "Anti-Ragging Cell", "routing_reason": "All ragging complaints are mandatorily routed to the Anti-Ragging Cell."}}
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

    # Enforce hard rule: Anti-Ragging always goes to Anti-Ragging Cell
    if category == "Anti-Ragging":
        result["department"] = "Anti-Ragging Cell"

    # Enforce hard rule: Needs Manual Review goes to Dean
    if category == "Needs Manual Review":
        result["department"] = "Dean of Student Welfare"

    return {
        "department": result.get("department", "Dean of Student Welfare"),
        "routing_reason": result.get("routing_reason", "Routed by AI agent."),
    }
