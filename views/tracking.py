"""
Student Tracking Page — Look up a complaint by tracking ID and view full timeline.
"""

import streamlit as st
import json
import io

from database.models import get_problem_by_tracking_id, get_status_logs, get_comments, get_agent_logs
from utils.helpers import (
    render_badge, priority_color, sentiment_color, status_color,
    format_timestamp, render_confidence_bar,
)


def render():
    st.markdown('<h1 class="main-title">🔍 Track Your Complaint</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Enter your tracking ID to see real-time status, full timeline, and AI analysis.</p>', unsafe_allow_html=True)

    # ── Search ──────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        tracking_id = st.text_input(
            "Tracking ID",
            placeholder="e.g. CPS-A3F8E1-2026",
            key="tracking_input",
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", use_container_width=True, key="search_btn")

    if not search_clicked and not tracking_id:
        st.markdown('<div style="background:#f8fafc; border:1px solid #e2e8f0;border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:40px;text-align:center;margin-top:40px;"><p style="font-size:3rem;margin-bottom:16px;">🎫</p><p style="color:#475569;font-size:1.1rem;">Enter the tracking ID you received when submitting your complaint.</p><p style="color:#64748b;font-size:0.9rem;margin-top:8px;">Format: CPS-XXXXXX-YYYY</p></div>', unsafe_allow_html=True)
        return

    if not tracking_id.strip():
        st.warning("Please enter a tracking ID.")
        return

    # ── Look up ─────────────────────────────────────────────────────────
    problem = get_problem_by_tracking_id(tracking_id.strip().upper())

    if not problem:
        st.error(f"❌ No complaint found with tracking ID: **{tracking_id.strip().upper()}**")
        st.markdown('<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:20px;margin-top:16px;"><p style="color:#fca5a5;">Tips:</p><ul style="color:#fca5a5;font-size:0.9rem;"><li>Check for typos in the tracking ID</li><li>The format is CPS-XXXXXX-YYYY (e.g., CPS-A3F8E1-2026)</li><li>Make sure you\'re using the correct ID from your submission</li></ul></div>', unsafe_allow_html=True)
        return

    # ── Status Header ───────────────────────────────────────────────────
    st_color = status_color(problem.get("status", ""))
    p_color = priority_color(problem.get("priority", ""))
    s_color = sentiment_color(problem.get("sentiment", ""))

    header_html = f'<div class="problem-card" style="border-left:4px solid {st_color};"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;"><div><span style="color:#0f766e;font-weight:700;font-size:1.3rem;">{problem.get("tracking_id","")}</span><span style="color:#64748b;margin-left:12px;">by {problem.get("student_name","Anonymous")}</span></div><div style="display:flex;gap:8px;">{render_badge(problem.get("status",""), st_color)}{render_badge(problem.get("priority",""), p_color)}</div></div><p style="color:#0f172a;font-size:1.1rem;font-weight:500;margin-top:16px;">{problem.get("summary","")}</p><p style="color:#64748b;font-size:0.85rem;margin-top:8px;">Submitted: {format_timestamp(problem.get("created_at",""))} &nbsp;|&nbsp; Last updated: {format_timestamp(problem.get("updated_at",""))}</p></div>'
    st.markdown(header_html, unsafe_allow_html=True)

    # ── Tabs ────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📜 Timeline", "🤖 AI Analysis", "💬 Comments", "📄 Original"])

    # ── Tab 1: Timeline ─────────────────────────────────────────────────
    with tab1:
        status_logs = get_status_logs(problem["id"])

        if not status_logs:
            st.info("No status changes recorded yet.")
        else:
            for i, log in enumerate(status_logs):
                old = log.get("old_status") or "—"
                new = log.get("new_status", "")
                new_color = status_color(new)

                tl_html = f'<div class="timeline-item"><div style="background:#f8fafc; border:1px solid #e2e8f0;border-radius:10px;padding:14px;"><div style="display:flex;justify-content:space-between;align-items:center;"><div><span style="color:#64748b;">{old}</span><span style="color:#0f766e;margin:0 8px;">→</span>{render_badge(new, new_color)}</div><span style="color:#64748b;font-size:0.8rem;">{format_timestamp(log.get("changed_at",""))}</span></div><p style="color:#64748b;font-size:0.8rem;margin-top:6px;">by {log.get("changed_by","System")}</p></div></div>'
                st.markdown(tl_html, unsafe_allow_html=True)

    # ── Tab 2: AI Analysis ──────────────────────────────────────────────
    with tab2:
        # Category + Confidence
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">🏷️ Category:</strong><span style="color:#0f172a;font-weight:600;margin-left:8px;">{problem.get("category","")}</span><br><span style="color:#475569;font-size:0.85rem;">Confidence:</span>{render_confidence_bar(problem.get("confidence", 0))}</div>', unsafe_allow_html=True)

        # Priority
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">⚡ Priority:</strong>{render_badge(problem.get("priority",""), p_color)}<br><span style="color:#475569;font-size:0.85rem;margin-top:4px;display:inline-block;">{problem.get("priority_reason","")}</span></div>', unsafe_allow_html=True)

        # Department
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">📬 Department:</strong><span style="color:#0f172a;font-weight:600;margin-left:8px;">{problem.get("department","")}</span><br><span style="color:#475569;font-size:0.85rem;">{problem.get("routing_reason","")}</span></div>', unsafe_allow_html=True)

        # Sentiment
        flag_text = "🔴 Flagged for immediate attention" if problem.get("flagged") else "🟢 No flags"
        st.markdown(f'<div class="agent-step success"><strong style="color:#10b981;">💭 Sentiment:</strong>{render_badge(problem.get("sentiment",""), s_color)}<br><span style="color:#475569;font-size:0.85rem;">{flag_text}</span></div>', unsafe_allow_html=True)

        # Fallback indicator
        if problem.get("used_fallback"):
            st.markdown('<div class="agent-step" style="border-left-color:#f59e0b;"><strong style="color:#f59e0b;">⚠️ Processed with fallback heuristics</strong><br><span style="color:#fcd34d;font-size:0.85rem;">AI agents were unavailable; keyword-based analysis was used.</span></div>', unsafe_allow_html=True)

    # ── Tab 3: Comments ─────────────────────────────────────────────────
    with tab3:
        comments = get_comments(problem["id"])
        if not comments:
            st.info("No comments yet. The admin will post updates here.")
        else:
            for c in comments:
                c_html = f'<div style="background:#f8fafc; border:1px solid #e2e8f0;padding:14px;border-radius:10px;margin-bottom:10px;border-left:3px solid #6366f1;"><div style="display:flex;justify-content:space-between;align-items:center;"><span style="color:#0f766e;font-weight:600;">{c.get("posted_by","Admin")}</span><span style="color:#64748b;font-size:0.8rem;">{format_timestamp(c.get("posted_at",""))}</span></div><p style="color:#334155;margin-top:8px;font-size:0.95rem;">{c.get("comment","")}</p></div>'
                st.markdown(c_html, unsafe_allow_html=True)

    # ── Tab 4: Original ─────────────────────────────────────────────────
    with tab4:
        st.markdown("**Original Complaint Text:**")
        desc = problem.get("description", "")
        st.markdown(f'<div style="background:#f8fafc; border:1px solid #e2e8f0;padding:20px;border-radius:12px;color:#334155;font-size:0.95rem;line-height:1.7;white-space:pre-wrap;">{desc}</div>', unsafe_allow_html=True)

        if problem.get("image_blob"):
            try:
                from PIL import Image
                img = Image.open(io.BytesIO(problem["image_blob"]))
                st.image(img, caption="Attached image", width=400)
            except Exception:
                st.caption("📎 Image attached (could not render)")
