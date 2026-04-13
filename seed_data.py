"""
Seed Data — Pre-populate the database with 15 sample complaints
across all categories, priorities, sentiments, and statuses.
Run this script once: python seed_data.py
"""

import sys
import os
import json
import random

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import init_db, get_connection
from database.models import (
    insert_problem, insert_status_log, insert_comment,
    insert_agent_log, update_problem_status,
)
from utils.helpers import generate_tracking_id


SEED_COMPLAINTS = [
    # ── Infrastructure ──────────────────────────────────────────────────
    {
        "description": "The corridor lights on the 2nd floor of Block A have been flickering for a week. It's very dark at night and students feel unsafe walking through.",
        "student_name": "Aditya Sharma",
        "category": "Infrastructure",
        "confidence": 0.92,
        "priority": "High",
        "priority_reason": "Safety concern due to inadequate lighting in a high-traffic area.",
        "summary": "Flickering corridor lights on 2nd floor of Block A creating safety hazard.",
        "department": "Maintenance & Infrastructure Dept.",
        "routing_reason": "Lighting and building maintenance falls under Infrastructure department.",
        "sentiment": "Frustrated",
        "flagged": False,
        "status": "In Progress",
    },
    {
        "description": "The AC in Room 301 of the CS building has not been working for the past 3 days. Temperature is unbearable during afternoon lectures.",
        "student_name": "Priya Patel",
        "category": "Infrastructure",
        "confidence": 0.89,
        "priority": "Medium",
        "priority_reason": "AC malfunction affecting classroom comfort but not a safety issue.",
        "summary": "Non-functional air conditioning in CS building Room 301 for three days.",
        "department": "Maintenance & Infrastructure Dept.",
        "routing_reason": "HVAC and classroom facility issues handled by Maintenance department.",
        "sentiment": "Neutral",
        "flagged": False,
        "status": "Submitted",
    },

    # ── Academic ────────────────────────────────────────────────────────
    {
        "description": "Professor Verma has not updated the syllabus for Data Structures since 2022. We are studying outdated material and it's affecting placement prep.",
        "student_name": "Rahul Gupta",
        "category": "Academic",
        "confidence": 0.87,
        "priority": "Medium",
        "priority_reason": "Outdated academic material affecting learning quality.",
        "summary": "Data Structures syllabus not updated since 2022, affecting placement preparation.",
        "department": "Academic Affairs Office",
        "routing_reason": "Syllabus and curriculum issues are handled by Academic Affairs.",
        "sentiment": "Frustrated",
        "flagged": False,
        "status": "Submitted",
    },
    {
        "description": "My attendance is showing 62% but I have attended all classes. The biometric system is not registering my entries properly. I might get detained!",
        "student_name": "Sneha Reddy",
        "category": "Academic",
        "confidence": 0.83,
        "priority": "High",
        "priority_reason": "Incorrect attendance record may lead to academic detention.",
        "summary": "Biometric system failing to register attendance correctly, showing 62% instead of actual.",
        "department": "Academic Affairs Office",
        "routing_reason": "Attendance disputes require Academic Affairs intervention.",
        "sentiment": "Distressed",
        "flagged": True,
        "status": "In Progress",
    },

    # ── Hostel & Mess ───────────────────────────────────────────────────
    {
        "description": "bhai 3rd floor pe paani nahi aata subah 6 se 9 baje tak. nahane ka time hi nahi milta. do hafte se same issue hai.",
        "student_name": "Vikram Singh",
        "category": "Hostel & Mess",
        "confidence": 0.91,
        "priority": "High",
        "priority_reason": "Essential water supply disruption persisting for two weeks.",
        "summary": "Water supply disruption on 3rd floor of hostel block during morning hours for past two weeks.",
        "department": "Hostel Warden & Mess Committee",
        "routing_reason": "Hostel water supply issues managed by Hostel Warden.",
        "sentiment": "Frustrated",
        "flagged": False,
        "status": "In Progress",
    },
    {
        "description": "Found a cockroach in my dal today at lunch. This is the third time this month. The kitchen hygiene is absolutely terrible.",
        "student_name": "Ananya Iyer",
        "category": "Hostel & Mess",
        "confidence": 0.95,
        "priority": "High",
        "priority_reason": "Repeated food contamination poses serious health risk.",
        "summary": "Recurring cockroach contamination in mess food, third incident this month.",
        "department": "Hostel Warden & Mess Committee",
        "routing_reason": "Mess food quality and kitchen hygiene complaints go to Mess Committee.",
        "sentiment": "Angry",
        "flagged": True,
        "status": "Submitted",
    },
    {
        "description": "The mess timing for dinner is 7-9 PM but I have lab till 8:30 PM. By the time I reach, only leftover food is available. Can we extend dinner till 9:30?",
        "student_name": "Karthik Menon",
        "category": "Hostel & Mess",
        "confidence": 0.88,
        "priority": "Low",
        "priority_reason": "Scheduling suggestion without immediate impact on safety.",
        "summary": "Request to extend dinner timing due to lab schedule conflict.",
        "department": "Hostel Warden & Mess Committee",
        "routing_reason": "Mess scheduling managed by Mess Committee.",
        "sentiment": "Neutral",
        "flagged": False,
        "status": "Resolved",
    },

    # ── Anti-Ragging ────────────────────────────────────────────────────
    {
        "description": "Some seniors from the 4th year came to our room at 2 AM and forced us to do pushups and sing songs. They threatened to beat us if we complained. I am very scared.",
        "student_name": "Anonymous",
        "category": "Anti-Ragging",
        "confidence": 0.98,
        "priority": "Urgent",
        "priority_reason": "Anti-ragging complaints are always classified as Urgent per institutional policy.",
        "summary": "Seniors forcing freshers to perform physical tasks at night with threats of violence.",
        "department": "Anti-Ragging Cell",
        "routing_reason": "All ragging complaints are mandatorily routed to the Anti-Ragging Cell.",
        "sentiment": "Distressed",
        "flagged": True,
        "status": "In Progress",
    },
    {
        "description": "A group of third-year students is regularly bullying first-year students near the canteen area. They take money and food forcefully.",
        "student_name": "Anonymous",
        "category": "Anti-Ragging",
        "confidence": 0.96,
        "priority": "Urgent",
        "priority_reason": "Bullying and extortion are serious ragging offenses requiring immediate action.",
        "summary": "Third-year students bullying and extorting first-year students near canteen area.",
        "department": "Anti-Ragging Cell",
        "routing_reason": "Bullying and ragging complaints are handled exclusively by Anti-Ragging Cell.",
        "sentiment": "Angry",
        "flagged": True,
        "status": "Submitted",
    },

    # ── Administration ──────────────────────────────────────────────────
    {
        "description": "I applied for my degree certificate 3 months ago and still haven't received it. The office keeps saying 'come next week'. I need it urgently for my job joining.",
        "student_name": "Deepak Kumar",
        "category": "Administration",
        "confidence": 0.90,
        "priority": "High",
        "priority_reason": "Delayed degree certificate affecting employment joining date.",
        "summary": "Degree certificate pending for three months despite repeated follow-ups, needed for employment.",
        "department": "Registrar / Admin Office",
        "routing_reason": "Certificate issuance and document processing handled by Registrar.",
        "sentiment": "Frustrated",
        "flagged": False,
        "status": "In Progress",
    },
    {
        "description": "Scholarship amount has not been credited for the last 2 semesters. I come from a financially weak background and this money is essential for my education.",
        "student_name": "Meera Joshi",
        "category": "Administration",
        "confidence": 0.88,
        "priority": "High",
        "priority_reason": "Pending scholarship affecting student's ability to continue education.",
        "summary": "Scholarship funds not credited for two consecutive semesters, causing financial hardship.",
        "department": "Registrar / Admin Office",
        "routing_reason": "Scholarship disbursement issues managed by Admin Office.",
        "sentiment": "Distressed",
        "flagged": True,
        "status": "Submitted",
    },

    # ── IT & Network ────────────────────────────────────────────────────
    {
        "description": "The Wi-Fi in Block C has been completely down for 5 days now. We cannot access online assignments, LMS, or even basic browsing. Multiple complaints but no action.",
        "student_name": "Arjun Nair",
        "category": "IT & Network",
        "confidence": 0.94,
        "priority": "High",
        "priority_reason": "Complete internet outage affecting academic work for an entire block.",
        "summary": "Complete Wi-Fi outage in Block C for five days disrupting academic activities.",
        "department": "IT Services & Network Dept.",
        "routing_reason": "Network outages and Wi-Fi issues are handled by IT Services.",
        "sentiment": "Angry",
        "flagged": True,
        "status": "In Progress",
    },
    {
        "description": "The ERP portal keeps crashing whenever I try to register for elective courses. The deadline is tomorrow and I still can't register.",
        "student_name": "Riya Saxena",
        "category": "IT & Network",
        "confidence": 0.86,
        "priority": "High",
        "priority_reason": "ERP system failure blocking time-sensitive course registration.",
        "summary": "ERP portal crashes during elective course registration with deadline imminent.",
        "department": "IT Services & Network Dept.",
        "routing_reason": "ERP and web portal issues managed by IT Services department.",
        "sentiment": "Frustrated",
        "flagged": False,
        "status": "Resolved",
    },

    # ── Mixed / Edge cases ──────────────────────────────────────────────
    {
        "description": "The library should have extended hours during exam season. Currently it closes at 9 PM but we need at least till midnight. Also the reading room chairs are uncomfortable.",
        "student_name": "Tanvi Aggarwal",
        "category": "Administration",
        "confidence": 0.72,
        "priority": "Low",
        "priority_reason": "General suggestion for improvement without urgency.",
        "summary": "Request for extended library hours during exams and improvement of reading room furniture.",
        "department": "Registrar / Admin Office",
        "routing_reason": "Library operations managed by Admin Office; furniture concern noted for Infrastructure.",
        "sentiment": "Neutral",
        "flagged": False,
        "status": "Resolved",
    },
]


def seed():
    """Populate the database with sample data."""
    print("🌱 Initializing database...")
    init_db()

    # Check if already seeded
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) as c FROM problems").fetchone()
    if dict(count)["c"] > 0:
        print(f"⚠️  Database already has {dict(count)['c']} records. Skipping seed.")
        print("   To re-seed, delete campus_solver.db and run again.")
        conn.close()
        return
    conn.close()

    print(f"📝 Inserting {len(SEED_COMPLAINTS)} sample complaints...")

    for i, complaint in enumerate(SEED_COMPLAINTS, 1):
        tracking_id = generate_tracking_id()

        # Insert the problem
        problem_id = insert_problem(
            description=complaint["description"],
            tracking_id=tracking_id,
            student_name=complaint.get("student_name", "Anonymous"),
            category=complaint["category"],
            confidence=complaint["confidence"],
            priority=complaint["priority"],
            priority_reason=complaint["priority_reason"],
            summary=complaint["summary"],
            department=complaint["department"],
            routing_reason=complaint["routing_reason"],
            sentiment=complaint["sentiment"],
            flagged=complaint["flagged"],
            status=complaint["status"],
            used_fallback=False,
        )

        # Insert initial status log
        insert_status_log(problem_id, None, "Submitted", "System")

        # Add additional status transitions for non-Submitted complaints
        if complaint["status"] == "In Progress":
            insert_status_log(problem_id, "Submitted", "In Progress", "Admin")
        elif complaint["status"] == "Resolved":
            insert_status_log(problem_id, "Submitted", "In Progress", "Admin")
            insert_status_log(problem_id, "In Progress", "Resolved", "Admin")
            # Add a resolution comment for resolved complaints
            insert_comment(
                problem_id,
                f"Issue has been resolved. Thank you for your patience.",
                "Admin",
            )

        # Insert mock agent logs for each complaint
        agents = [
            ("Classifier Agent", complaint["description"][:200],
             json.dumps({"category": complaint["category"], "confidence": complaint["confidence"]})),
            ("Priority Agent", json.dumps({"complaint": complaint["description"][:100], "category": complaint["category"]}),
             json.dumps({"priority": complaint["priority"], "reason": complaint["priority_reason"]})),
            ("Summarizer Agent", complaint["description"][:200],
             json.dumps({"summary": complaint["summary"]})),
            ("Router Agent", json.dumps({"category": complaint["category"], "priority": complaint["priority"], "summary": complaint["summary"]}),
             json.dumps({"department": complaint["department"], "routing_reason": complaint["routing_reason"]})),
            ("Sentiment Agent", complaint["description"][:200],
             json.dumps({"sentiment": complaint["sentiment"], "flag": complaint["flagged"]})),
        ]

        for agent_name, input_text, output_json in agents:
            latency = random.uniform(150, 900)
            insert_agent_log(problem_id, agent_name, input_text, output_json, round(latency, 1))

        print(f"   ✅ [{i:2d}/15] {tracking_id} — {complaint['category']} / {complaint['priority']} / {complaint['sentiment']}")

    print("\n🎉 Seed complete! Run the app with: streamlit run app.py")


if __name__ == "__main__":
    seed()
