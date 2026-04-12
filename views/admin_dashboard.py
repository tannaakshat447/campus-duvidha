"""
Admin Dashboard — Filter, review, manage, and export complaints.
"""

import streamlit as st
import csv
import io
import json

from database.models import (
    get_all_problems, update_problem_status,
    insert_comment, get_comments, get_agent_logs,
    get_total_problems, get_flagged_count,
)
from utils.helpers import (
    render_badge, priority_color, sentiment_color, status_color,
    format_timestamp,
)
from utils.notify import notify_status_change
from config import STATUSES, PRIORITIES, SENTIMENTS, DEPARTMENTS


def render():
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    if not st.session_state["admin_authenticated"]:
        st.markdown('<h1 class="main-title">🔒 Admin Login</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Please enter the admin PIN to access this page.</p>', unsafe_allow_html=True)
        
        pwd = st.text_input("Admin PIN", type="password", key="admin_login_pin")
        if st.button("Login", type="primary"):
            if pwd == "Admin@123":
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid PIN")
        return

    st.markdown('<h1 class="main-title">🛡️ Admin Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Review complaints, update statuses, and monitor flagged issues.</p>', unsafe_allow_html=True)

    # ── Quick Stats Row ─────────────────────────────────────────────────
    all_problems = get_all_problems()
    total = len(all_problems)
    submitted = sum(1 for p in all_problems if p["status"] == "Submitted")
    in_progress = sum(1 for p in all_problems if p["status"] == "In Progress")
    resolved = sum(1 for p in all_problems if p["status"] == "Resolved")
    flagged = sum(1 for p in all_problems if p["flagged"])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("📊 Total", total)
    c2.metric("📩 Submitted", submitted)
    c3.metric("🔄 In Progress", in_progress)
    c4.metric("✅ Resolved", resolved)
    c5.metric("🚨 Flagged", flagged)

    st.markdown("---")

    # ── Filters ─────────────────────────────────────────────────────────
    st.markdown("### 🔍 Filters")
    fc1, fc2, fc3, fc4 = st.columns(4)

    def reset_page():
        st.session_state.admin_page = 1

    with fc1:
        dept_filter = st.selectbox(
            "Department",
            ["All"] + list(DEPARTMENTS.values()),
            key="admin_dept_filter",
            on_change=reset_page
        )
    with fc2:
        status_filter = st.selectbox(
            "Status",
            ["All"] + STATUSES,
            key="admin_status_filter",
            on_change=reset_page
        )
    with fc3:
        priority_filter = st.selectbox(
            "Priority",
            ["All"] + PRIORITIES,
            key="admin_priority_filter",
            on_change=reset_page
        )
    with fc4:
        st.markdown("<br>", unsafe_allow_html=True)
        flagged_filter = st.checkbox("🚨 Flagged Only", key="admin_flagged_filter", on_change=reset_page)

    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1

    # First get total number for these filters
    all_filtered = get_all_problems(
        department=dept_filter if dept_filter != "All" else None,
        status=status_filter if status_filter != "All" else None,
        priority=priority_filter if priority_filter != "All" else None,
        flagged_only=flagged_filter,
    )
    total_matches = len(all_filtered)
    
    ITEMS_PER_PAGE = 10
    total_pages = (total_matches + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE or 1
    
    if st.session_state.admin_page > total_pages:
        st.session_state.admin_page = total_pages

    offset = (st.session_state.admin_page - 1) * ITEMS_PER_PAGE

    # Apply pagination filters
    filtered = get_all_problems(
        department=dept_filter if dept_filter != "All" else None,
        status=status_filter if status_filter != "All" else None,
        priority=priority_filter if priority_filter != "All" else None,
        flagged_only=flagged_filter,
        limit=ITEMS_PER_PAGE,
        offset=offset
    )

    # ── Export Button ───────────────────────────────────────────────────
    st.markdown(f"**Showing {len(filtered)} items (Total matches: {total_matches})**")

    if all_filtered:
        csv_buffer = io.StringIO()
        writer = csv.DictWriter(
            csv_buffer,
            fieldnames=[
                "tracking_id", "student_name", "description", "category",
                "confidence", "priority", "priority_reason", "summary",
                "department", "routing_reason", "sentiment", "flagged",
                "status", "created_at", "updated_at",
            ],
        )
        writer.writeheader()
        for p in all_filtered:
            row = {k: p.get(k, "") for k in writer.fieldnames}
            row["flagged"] = "Yes" if p.get("flagged") else "No"
            writer.writerow(row)

        st.download_button(
            "📥 Export All Matches as CSV",
            csv_buffer.getvalue(),
            file_name="campus_complaints_export.csv",
            mime="text/csv",
            key="export_csv",
        )

    st.markdown("---")

    # ── Pagination UI Top ───────────────────────────────────────────────
    if total_pages > 1:
        p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
        with p_col1:
            if st.button("⬅️ Previous", disabled=st.session_state.admin_page <= 1, key="prev_top"):
                st.session_state.admin_page -= 1
                st.rerun()
        with p_col2:
            st.markdown(f"<div style='text-align:center; padding-top:8px; color:#64748b; font-weight:600;'>Page {st.session_state.admin_page} of {total_pages}</div>", unsafe_allow_html=True)
        with p_col3:
            if st.button("Next ➡️", disabled=st.session_state.admin_page >= total_pages, key="next_top"):
                st.session_state.admin_page += 1
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Complaint Cards ─────────────────────────────────────────────────
    if not filtered:
        st.info("No complaints match the current filters.")
        return

    for idx, problem in enumerate(filtered):
        is_flagged = problem.get("flagged", 0)
        card_class = "problem-card flagged" if is_flagged else "problem-card"

        p_color = priority_color(problem.get("priority", ""))
        s_color = sentiment_color(problem.get("sentiment", ""))
        st_color = status_color(problem.get("status", ""))

        # Card header — no indentation inside HTML to avoid Streamlit code-block rendering
        flag_icon = "🔴" if is_flagged else ""
        card_html = f'<div class="{card_class}"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;"><div><span style="color:#4f46e5;font-family:\'Outfit\', sans-serif;font-weight:700;font-size:1.2rem;">{problem.get("tracking_id","N/A")}</span><span style="color:#64748b;margin-left:12px;font-size:0.85rem;">by {problem.get("student_name","Anonymous")}</span></div><div style="display:flex;gap:8px;flex-wrap:wrap;">{render_badge(problem.get("priority","N/A"), p_color)}{render_badge(problem.get("status","N/A"), st_color)}{render_badge(problem.get("sentiment","N/A"), s_color)} {flag_icon}</div></div><div style="margin-top:12px;"><p style="color:#0f172a;font-size:1.05rem;font-weight:500;margin-bottom:6px;">{problem.get("summary","")}</p><p style="color:#64748b;font-size:0.85rem;">{problem.get("category","")} → <strong style="color:#1e293b;">{problem.get("department","")}</strong></p><p style="color:#64748b;font-size:0.75rem;margin-top:4px;">{problem.get("routing_reason","")}</p><p style="color:#94a3b8;font-size:0.75rem;margin-top:8px;">Submitted: {format_timestamp(problem.get("created_at",""))}</p></div></div>'
        st.markdown(card_html, unsafe_allow_html=True)

        # Expandable details
        with st.expander(f"📋 Details & Actions — {problem.get('tracking_id', '')}", expanded=False):
            # Original text
            st.markdown("**📄 Original Complaint:**")
            desc_html = f'<div style="background:#f8fafc; border:1px solid #e2e8f0;padding:14px;border-radius:10px;color:#334155;font-size:0.9rem;line-height:1.6;">{problem.get("description","")}</div>'
            st.markdown(desc_html, unsafe_allow_html=True)

            # Display attached image if exists
            if problem.get("image_blob"):
                try:
                    from PIL import Image
                    img = Image.open(io.BytesIO(problem["image_blob"]))
                    st.image(img, caption="Attached image", width=400)
                except Exception:
                    st.caption("📎 Image attached (could not render)")

            st.markdown("---")

            st.markdown("---")

            # Status update
            ac1, ac2 = st.columns([2, 1])
            with ac1:
                new_status = st.selectbox(
                    "Update Status",
                    STATUSES,
                    index=STATUSES.index(problem["status"]) if problem["status"] in STATUSES else 0,
                    key=f"status_{problem['id']}",
                )
            with ac2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Update", key=f"update_btn_{problem['id']}"):
                    if new_status != problem["status"]:
                        update_problem_status(problem["id"], new_status, "Admin")
                        notify_status_change(
                            problem.get("tracking_id", ""),
                            problem["status"],
                            new_status,
                        )
                        st.success(f"Status updated to **{new_status}**")
                        st.rerun()
                    else:
                        st.info("Status unchanged.")

            # Resolution comment
            comment_text = st.text_area(
                "Add Resolution Comment",
                placeholder="Describe the resolution or next steps...",
                key=f"comment_{problem['id']}",
            )
            if st.button("💬 Post Comment", key=f"comment_btn_{problem['id']}"):
                if comment_text.strip():
                    insert_comment(problem["id"], comment_text.strip(), "Admin")
                    st.success("Comment posted!")
                    st.rerun()
                else:
                    st.warning("Please enter a comment.")

            # Show existing comments
            comments = get_comments(problem["id"])
            if comments:
                st.markdown("**💬 Comments:**")
                for c in comments:
                    sender = c.get("posted_by", "Admin")
                    border_color = "#3b82f6" if sender == "Student" else "#10b981"
                    c_html = f'<div style="background:#f8fafc; border:1px solid #e2e8f0;padding:10px 14px;border-radius:8px;margin-bottom:8px;border-left:4px solid {border_color};"><span style="color:#0f766e;font-weight:600;font-size:0.85rem;">{sender}</span><span style="color:#64748b;font-size:0.75rem;margin-left:8px;">{format_timestamp(c.get("posted_at",""))}</span><p style="color:#334155;margin:6px 0 0;font-size:0.9rem;">{c.get("comment","")}</p></div>'
                    st.markdown(c_html, unsafe_allow_html=True)

            st.markdown("---")

            # AI Traceability (Backend Agent Logs)
            ai_logs = get_agent_logs(problem["id"])
            if ai_logs:
                with st.expander("🤖 AI Traceability & Backend Logs", expanded=False):
                    st.caption("Raw LLM network transactions and independent agent logic.")
                    for log in ai_logs:
                        latency = f"{log.get('latency_ms', 0):.0f}ms"
                        st.markdown(f"**{log.get('agent_name')}** ⏱️ `{latency}`")
                        
                        tabs = st.tabs(["JSON Output", "Input Context"])
                        with tabs[0]:
                            st.json(json.loads(log.get('output_json', '{}')))
                        with tabs[1]:
                            st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{log.get('input_text')}</span>", unsafe_allow_html=True)
                        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)



        st.markdown("")  # Spacer

