"""
Agent 5 — Sentiment Agent
Detects the emotional state of the student from the raw complaint text.
Flags complaints where the student appears distressed or angry.
"""

import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

SYSTEM_PROMPT = """You are the Sentiment Agent in a campus complaint management system.
Your ONLY job is to analyze the emotional tone of a student's complaint.

SENTIMENT LABELS (choose exactly one):
  - "Neutral"     — calm, factual, informational tone
  - "Frustrated"  — annoyed, impatient, exasperated but not aggressive
  - "Distressed"  — anxious, scared, helpless, mentions mental health, feels unsafe
  - "Angry"       — aggressive language, threats, profanity, shouting (ALL CAPS), hostility

FLAGGING RULES:
  - If sentiment is "Distressed" or "Angry" → set "flag" to true
  - If sentiment is "Neutral" or "Frustrated" → set "flag" to false
  - Distressed/Angry flags trigger admin alerts so they get priority attention

OUTPUT FORMAT:
  Return ONLY a JSON object with exactly two keys:
  - "sentiment": one of the four labels above
  - "flag": true or false

ANALYSIS GUIDELINES:
1. Look for emotional indicators:
   - ALL CAPS = frustration or anger
   - Exclamation marks (!!!) = strong emotion
   - Profanity/slang insults = anger
   - "scared", "afraid", "helpless", "can't take it" = distress
   - "please help", "don't know what to do" = distress
   - Threats of self-harm or feeling unsafe = ALWAYS Distressed + flag
2. Hinglish emotional markers:
   - "bahut pareshaan", "tang aa gaya", "kya bakwas hai" = Frustrated
   - "dar lagta hai", "bahut bura feel ho raha" = Distressed
   - "saala", aggressive slang = Angry
3. If the complaint is purely informational with no emotional language → Neutral.
4. When in doubt between Frustrated and Angry, choose Frustrated (less severe).

EXAMPLES:
Input: "The Wi-Fi has been down for 3 days. Please look into it."
Output: {"sentiment": "Neutral", "flag": false}

Input: "FIX THE WIFI ALREADY!!! ITS BEEN A WEEK AND NOBODY CARES!!!"
Output: {"sentiment": "Angry", "flag": true}

Input: "I'm scared to go back to my room because the seniors keep threatening me. I don't know what to do."
Output: {"sentiment": "Distressed", "flag": true}

Input: "yaar kab tak chalega ye paani ka issue, bahut ho gaya"
Output: {"sentiment": "Frustrated", "flag": false}
"""


def analyze_sentiment(complaint_text: str) -> dict:
    """
    Analyze the emotional tone of the complaint.
    Returns: {"sentiment": str, "flag": bool}
    """
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.1,
        max_tokens=100,
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
            result = {"sentiment": "Neutral", "flag": False}

    valid_sentiments = {"Neutral", "Frustrated", "Distressed", "Angry"}
    if result.get("sentiment") not in valid_sentiments:
        result["sentiment"] = "Neutral"

    # Enforce flag logic
    result["flag"] = result.get("sentiment") in ("Distressed", "Angry")

    return {
        "sentiment": result.get("sentiment", "Neutral"),
        "flag": bool(result.get("flag", False)),
    }
