from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import io
import json
import hashlib

# ── Import Models & Agents ───────────────────────────────────────────────────
from database.models import (
    create_user, get_user_by_email,
    insert_problem, update_problem_status, update_problem_fields,
    get_all_problems, get_problem_by_tracking_id, get_problems_by_email,
    get_status_logs, get_comments, insert_comment, insert_agent_log, get_agent_logs,
    get_category_distribution, get_sentiment_distribution,
    get_priority_distribution, get_department_stats, get_fallback_rate
)
from database.db import init_db, DB_PATH
from agents.orchestrator import run_pipeline
from utils.helpers import generate_tracking_id
from utils.notify import notify_admin_flagged, notify_submission_success, notify_status_change

# ── Configuration ─────────────────────────────────────────────────────────────
ADMIN_PIN = os.getenv("ADMIN_PIN", "Admin@123")

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Flask App Setup ──────────────────────────────────────────────────────────
# We set static_folder to 'frontend/dist' to serve the React production build
app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
CORS(app)

# ── Route: Serve React App ───────────────────────────────────────────────────
@app.route("/", defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# ── API Routes ──────────────────────────────────────────────────────────────
@app.before_request
def before_request():
    if not os.path.exists(DB_PATH):
        init_db()

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").strip().lower()
    pw = data.get("password", "")
    if not email.endswith("@iiitranchi.ac.in"):
        return jsonify({"error": "Only @iiitranchi.ac.in emails allowed"}), 400
    try:
        create_user(email, hash_password(pw))
        return jsonify({"message": "Registration successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").strip().lower()
    pw = data.get("password", "")
    user = get_user_by_email(email)
    if user and user["password_hash"] == hash_password(pw):
        return jsonify({"message": "OK", "user": email}), 200
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/api/auth/admin_login", methods=["POST"])
def admin_login():
    data = request.json
    pin = data.get("pin", "")
    if pin == ADMIN_PIN:
        return jsonify({"message": "OK", "role": "admin"}), 200
    return jsonify({"error": "Invalid PIN"}), 401

@app.route("/api/complaints/submit", methods=["POST"])
def submit_complaint():
    student_name = request.form.get("student_name", "Anonymous")
    email = request.form.get("email")
    description = request.form.get("description")
    
    if not email or not description:
        return jsonify({"error": "Missing required fields"}), 400
    
    tracking_id = generate_tracking_id()
    
    image_blob = None
    if 'image' in request.files:
        file = request.files['image']
        image_blob = file.read()
        
    problem_id = insert_problem(description=description, tracking_id=tracking_id, student_name=student_name, student_email=email, image_blob=image_blob)
    
    # Run Agent Synchronously
    result = run_pipeline(description, problem_id)
    
    update_problem_fields(
        problem_id,
        category=result.category,
        confidence=result.confidence,
        priority=result.priority,
        priority_reason=result.priority_reason,
        summary=result.summary,
        department=result.department,
        routing_reason=result.routing_reason,
        sentiment=result.sentiment,
        flagged=int(result.flagged),
        used_fallback=int(result.used_fallback),
    )
    
    notify_submission_success(tracking_id)
    if result.flagged:
        notify_admin_flagged(tracking_id, result.summary, result.sentiment)
        
    return jsonify({
        "message": "Complaint submitted",
        "tracking_id": tracking_id,
        "ai_analysis": {
            "category": result.category,
            "confidence": result.confidence,
            "priority": result.priority,
            "priority_reason": result.priority_reason,
            "department": result.department,
            "sentiment": result.sentiment,
            "flagged": result.flagged
        }
    }), 200

@app.route("/api/complaints/me", methods=["GET"])
def get_my_complaints():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400
    problems = get_problems_by_email(email)
    for p in problems:
        if 'image_blob' in p:
            del p['image_blob']
    return jsonify({"data": problems}), 200

@app.route("/api/tracking/<tracking_id>", methods=["GET"])
def tracking_details(tracking_id):
    p = get_problem_by_tracking_id(tracking_id)
    if not p:
        return jsonify({"error": "Tracking ID not found"}), 404
        
    if 'image_blob' in p:
        del p['image_blob'] # omit raw bytes
        
    logs = get_status_logs(p['id'])
    comments = get_comments(p['id'])
    ai_logs = get_agent_logs(p['id'])
    
    return jsonify({
        "problem": p,
        "timeline": logs,
        "comments": comments,
        "ai_trace": ai_logs
    }), 200

@app.route("/api/tracking/<problem_id>/comment", methods=["POST"])
def post_comment(problem_id):
    data = request.json
    insert_comment(problem_id, data['text'], data['sender'])
    return jsonify({"message": "Comment posted"}), 200

@app.route("/api/admin/complaints", methods=["GET"])
def all_complaints():
    problems = get_all_problems()
    for p in problems:
        if 'image_blob' in p:
            del p['image_blob']
    return jsonify({"data": problems}), 200

@app.route("/api/admin/complaints/<problem_id>/status", methods=["POST"])
def update_status(problem_id):
    data = request.json
    new_status = data['status']
    tracking_id = data.get('tracking_id', '')
    update_problem_status(problem_id, new_status, "Admin")
    notify_status_change(tracking_id, "Unknown", new_status)
    return jsonify({"message": "Status updated"}), 200

@app.route("/api/admin/analytics", methods=["GET"])
def analytics():
    problems = get_all_problems()
    resolved = sum(1 for p in problems if p['status'] == 'Resolved')
    overall = {
        "total": len(problems),
        "resolved": resolved
    }
    return jsonify({
        "stats": overall,
        "categories": get_category_distribution(),
        "sentiments": get_sentiment_distribution(),
        "priorities": get_priority_distribution(),
        "departments": get_department_stats(),
        "fallback": get_fallback_rate()
    }), 200

if __name__ == "__main__":
    init_db()
    # On production platforms like Render, port is often provided by environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
