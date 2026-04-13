"""
Campus Duvidha Solver — Central Configuration
Loads environment variables and defines app-wide constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenAI ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── SMTP Email Config ───────────────────────────────────────────────────────
SMTP_SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL", "")
SMTP_SENDER_PASSWORD = os.getenv("SMTP_SENDER_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# ── Database ────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "campus_solver.db")

# ── Categories ──────────────────────────────────────────────────────────────
CATEGORIES = [
    "Bathroom and hygiene",
    "Anti ragging and safety",
    "Mess and food quality",
    "Academic issues",
    "Infrastructure/Maintenance",
    "Other",
]

# ── Departments ─────────────────────────────────────────────────────────────
DEPARTMENTS = {
    "Bathroom and hygiene":     "Sanitation & Hygiene Dept.",
    "Anti ragging and safety":  "Anti-Ragging & Security Cell",
    "Mess and food quality":    "Mess & Catering Committee",
    "Academic issues":          "Academic Affairs Office",
    "Infrastructure/Maintenance": "Maintenance & Infrastructure Dept.",
    "Other":                    "Dean of Student Welfare",
    "Needs Manual Review":      "Dean of Student Welfare",
}

# ── Priority Levels ─────────────────────────────────────────────────────────
PRIORITIES = ["Low", "Medium", "High", "Urgent"]

# ── Sentiments ──────────────────────────────────────────────────────────────
SENTIMENTS = ["Neutral", "Frustrated", "Distressed", "Angry"]

# ── Status Options ──────────────────────────────────────────────────────────
STATUSES = ["Submitted", "In Progress", "Resolved"]

# ── Agent confidence threshold ──────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.55

# ── App Metadata ────────────────────────────────────────────────────────────
APP_TITLE = "🎓 Campus Duvidha Solver"
APP_SUBTITLE = "AI-Powered Complaint Management System"
APP_VERSION = "1.0.0"
