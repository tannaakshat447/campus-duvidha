"""
Student Portal — Submit complaints and view AI pipeline results in real time.
"""

import streamlit as st
import time
from PIL import Image
import io

from agents.orchestrator import run_pipeline
from database.models import insert_problem, update_problem_fields, insert_status_log, get_problems_by_email
from utils.helpers import (
    generate_tracking_id, render_badge, render_confidence_bar,
    priority_color, sentiment_color, status_color, format_timestamp
)
from utils.notify import notify_submission_success, notify_admin_flagged


def render():
    st.markdown('<h1 class="main-title">📝 Student Portal</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Submit a new complaint or track your existing ones.</p>', unsafe_allow_html=True)

    tab_submit, tab_my = st.tabs(["📋 New Complaint", "📁 My Complaints"])

    with tab_submit:
        render_submit_tab()

    with tab_my:
        render_my_complaints_tab()


def render_submit_tab():
    st.markdown("### 📋 New Complaint")

    col1, col2 = st.columns([3, 1])
    with col1:
        student_name = st.text_input(
            "Your Name (optional)",
            placeholder="e.g. Rahul Sharma",
            key="student_name",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        anonymous = st.checkbox("Submit anonymously", value=True, key="anonymous")

    complaint_text = st.text_area(
        "Describe your problem",
        height=180,
        placeholder="Tell us what's wrong. You can write in English, Hindi, or Hinglish.\n\nExamples:\n• The Wi-Fi in Block C has been down for 3 days\n• bhai 3rd floor pe paani nahi aata yaar\n• Some seniors are harassing freshers at night",
        key="complaint_text",
    )

    uploaded_image = st.file_uploader(
        "Attach a photo (optional)",
        type=["jpg", "jpeg", "png", "webp"],
        key="uploaded_image",
    )

    # Preview uploaded image
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption="Attached image preview", width=300)

    st.markdown("---")

    # ── Submit Button ───────────────────────────────────────────────────
    if st.button("🚀 Submit Complaint", use_container_width=True, key="submit_btn"):
        if not complaint_text or len(complaint_text.strip()) < 10:
            st.error("⚠️ Please describe your problem in at least 10 characters.")
            return

        # Prepare image blob
        image_blob = None
        if uploaded_image:
            uploaded_image.seek(0)
            image_blob = uploaded_image.read()

        name = "Anonymous" if anonymous or not student_name.strip() else student_name.strip()
        tracking_id = generate_tracking_id()
        current_email = st.session_state.get("student_email")

        # Insert placeholder row first (so agents can log against the ID)
        problem_id = insert_problem(
            description=complaint_text.strip(),
            tracking_id=tracking_id,
            student_name=name,
            student_email=current_email,
            image_blob=image_blob,
        )

        # Log initial status
        insert_status_log(problem_id, None, "Submitted", "System")

        # ── Run Agent Pipeline with Live Progress ───────────────────
        st.markdown("---")
        st.markdown("### 🤖 AI Agent Pipeline — Processing")
        st.markdown("*Each agent analyzes your complaint independently...*")

        agent_names = [
            ("🏷️ Classifier Agent", "Detecting complaint category..."),
            ("⚡ Priority Agent", "Assessing urgency level..."),
            ("📝 Summarizer Agent", "Generating clean summary..."),
            ("📬 Router Agent", "Finding the right department..."),
            ("💭 Sentiment Agent", "Analyzing emotional tone..."),
        ]

        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        for i, (agent_display, desc) in enumerate(agent_names):
            status_placeholder.markdown(
                f'<div class="agent-step">'
                f'<strong style="color:#0f766e;">{agent_display}</strong><br>'
                f'<span style="color:#475569; font-size:0.9rem;">{desc}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            progress_bar.progress((i + 1) / len(agent_names))
            if i < len(agent_names) - 1:
                time.sleep(0.3)  # Brief visual pause between agents

        # Run the actual pipeline
        with st.spinner("🔄 Running full AI pipeline..."):
            result = run_pipeline(complaint_text.strip(), problem_id)

        # Update the DB row with agent results
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

        progress_bar.progress(1.0)
        status_placeholder.empty()

        st.toast("Complaint submitted successfully! 🎉", icon="✅")
        from utils.helpers import trigger_professional_success
        trigger_professional_success()
        st.success(f"✅ Complaint submitted successfully!")
        notify_submission_success(tracking_id)

        if result.flagged:
            notify_admin_flagged(tracking_id, result.summary, result.sentiment)

        # Tracking ID card
        st.markdown(f'<div style="background:linear-gradient(135deg,#4f46e5,#9333ea);border-radius:16px;padding:32px;text-align:center;margin:24px 0;box-shadow:0 8px 32px rgba(79,70,229,0.25);border:1px solid rgba(255,255,255,0.2);"><p style="color:rgba(255,255,255,0.9);font-size:0.95rem;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your Tracking ID</p><h2 style="color:white;font-family:\'Outfit\',sans-serif;font-size:2.8rem;font-weight:800;letter-spacing:3px;margin:0;text-shadow:0 2px 4px rgba(0,0,0,0.2);">{tracking_id}</h2><p style="color:rgba(255,255,255,0.8);font-size:0.85rem;margin-top:12px;">Save this ID securely to track your complaint status on the Track Complaint page.</p></div>', unsafe_allow_html=True)

        # ── Agent Results Display ───────────────────────────────────
        st.markdown("### 🧠 AI Analysis Results")

        # Row 1: Category + Confidence
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">🏷️ Category</strong><br><span style="color:#0f172a;font-size:1.2rem;font-weight:600;">{result.category}</span></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">📊 Confidence</strong><br>{render_confidence_bar(result.confidence)}</div>', unsafe_allow_html=True)

        # Row 2: Priority + Sentiment
        c3, c4 = st.columns(2)
        with c3:
            p_color = priority_color(result.priority)
            st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">⚡ Priority</strong><br>{render_badge(result.priority, p_color)}<br><span style="color:#475569;font-size:0.85rem;margin-top:6px;display:inline-block;">{result.priority_reason}</span></div>', unsafe_allow_html=True)
        with c4:
            s_color = sentiment_color(result.sentiment)
            flag_icon = "🔴" if result.flagged else "🟢"
            flag_text = "⚠️ Flagged for admin attention" if result.flagged else "No emotional flags detected"
            st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">💭 Sentiment</strong><br>{render_badge(result.sentiment, s_color)} {flag_icon}<br><span style="color:#475569;font-size:0.85rem;margin-top:6px;display:inline-block;">{flag_text}</span></div>', unsafe_allow_html=True)

        # Row 3: Summary
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">📝 AI Summary</strong><br><span style="color:#0f172a;font-size:1.05rem;font-style:italic;">"{result.summary}"</span></div>', unsafe_allow_html=True)

        # Row 4: Department routing
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">📬 Routed To</strong><br><span style="color:#0f172a;font-size:1.1rem;font-weight:600;">{result.department}</span><br><span style="color:#475569;font-size:0.85rem;">{result.routing_reason}</span></div>', unsafe_allow_html=True)

        # Fallback indicator
        if result.used_fallback:
            st.markdown('<div class="agent-step" style="border-left-color:#f59e0b;"><strong style="color:#f59e0b;">⚠️ Fallback Mode</strong><br><span style="color:#fcd34d;font-size:0.9rem;">One or more agents used keyword-based heuristics instead of AI. Results may be less accurate. Set your OpenAI API key for full AI analysis.</span></div>', unsafe_allow_html=True)


def render_my_complaints_tab():
    current_email = st.session_state.get("student_email")
    if not current_email:
        st.warning("You must be logged in to view your complaints.")
        return

    problems = get_problems_by_email(current_email)

    if not problems:
        st.info("You haven't submitted any complaints yet.")
        return

    st.markdown(f"### You have {len(problems)} submitted complaint(s)")

    def jump_to_tracking(tid):
        st.session_state.force_nav = "🔍 Track Complaint"
        st.session_state.tracking_input = tid

    for prob in problems:
        is_flagged = prob.get("flagged", 0)
        card_class = "problem-card flagged" if is_flagged else "problem-card"

        p_color = priority_color(prob.get("priority", ""))
        st_color = status_color(prob.get("status", ""))
        tid = prob.get("tracking_id", "")

        flag_icon = "🔴" if is_flagged else ""
        card_html = f'<div class="{card_class}"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;"><div><span style="color:#4f46e5;font-family:\'Outfit\', sans-serif;font-weight:700;font-size:1.2rem;">{tid}</span></div><div style="display:flex;gap:8px;flex-wrap:wrap;">{render_badge(prob.get("priority","N/A"), p_color)}{render_badge(prob.get("status","N/A"), st_color)} {flag_icon}</div></div><div style="margin-top:12px;"><p style="color:#0f172a;font-size:1.05rem;font-weight:500;margin-bottom:6px;">{prob.get("summary", prob.get("description", "")[:80] + "...")}</p><p style="color:#64748b;font-size:0.85rem;">Department: <strong style="color:#1e293b;">{prob.get("department","Pending")}</strong></p><p style="color:#94a3b8;font-size:0.75rem;margin-top:8px;">Submitted: {format_timestamp(prob.get("created_at",""))}</p></div></div>'
        
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(card_html, unsafe_allow_html=True)
        with c2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.button("View Details ➡️", key=f"jump_{tid}", on_click=jump_to_tracking, args=(tid,), use_container_width=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
