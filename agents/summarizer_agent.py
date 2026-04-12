"""
Agent 3 — Summarizer Agent
Rewrites the raw complaint as a clean, formal 1-line summary
suitable for admin display — even if the student wrote in
bad grammar, slang, or Hinglish.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

SYSTEM_PROMPT = """You are the Summarizer Agent in a campus complaint management system.
Your ONLY job is to rewrite a student's raw complaint as a single, clean, formal sentence
suitable for display on an admin dashboard.

RULES:
1. Output must be ONE sentence, maximum 30 words.
2. Use formal, professional English regardless of the input language or quality.
3. Preserve the core issue, location, and any specific details (floor numbers, block names, dates).
4. Remove filler words, emotions, slang, and profanity.
5. Do NOT add information that isn't in the original complaint.
6. If the complaint mentions a specific location, include it.
7. Return ONLY a JSON object with one key: "summary".

EXAMPLES:
Input: "bhai 3rd floor pe paani nahi aata yaar fix karo"
Output: {"summary": "Water supply disruption reported on the 3rd floor of the hostel block."}

Input: "The wifi is literally the worst thing ever omg fix it already its been 5 days!!!!"
Output: {"summary": "Wi-Fi outage persisting for five days requires immediate attention."}

Input: "some seniors came to our room at 2am and forced us to sing and do pushups they r threatening us daily"
Output: {"summary": "Seniors reportedly entering freshman rooms at night for forced ragging activities."}

Input: "mess ka khana bahut ganda hai aaj dal me keeda tha"
Output: {"summary": "Insect contamination found in mess food (dal) today."}
"""


def summarize(complaint_text: str) -> dict:
    """
    Generate a clean 1-line summary.
    Returns: {"summary": str}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.3,
        max_tokens=150,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": complaint_text},
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
            # Use the raw text as the summary itself
            result = {"summary": raw.strip('"').strip("'")}

    return {"summary": result.get("summary", complaint_text[:100])}
