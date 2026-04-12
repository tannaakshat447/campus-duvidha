"""
Campus Duvidha Solver — Main Streamlit Application
Entry point with sidebar navigation and database initialization.
"""

import streamlit as st
from database.db import init_db
from utils.helpers import inject_custom_css

# ── Page Config ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Campus Duvidha Solver",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize DB ───────────────────────────────────────────────────────
init_db()

# ── Inject Custom CSS ──────────────────────────────────────────────────
inject_custom_css()

# ── Sidebar Navigation ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 20px 0 10px;">
            <p style="font-size:2.5rem; margin-bottom:0;">🎓</p>
            <h2 style="background: linear-gradient(90deg, #818cf8, #c084fc);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;
                       font-size:1.4rem; font-weight:800; margin-top:4px;">
                Campus Duvidha Solver
            </h2>
            <p style="color:#7c83db; font-size:0.8rem; margin-top:-8px;">
                AI-Powered Complaint Management
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    page = st.radio(
        "Navigate",
        [
            "📝 Student Portal",
            "🛡️ Admin Dashboard",
            "🔍 Track Complaint",
            "📊 Analytics",
        ],
        index=0,
        key="nav_radio",
    )

    st.markdown("---")

    # Show Logout if student is logged in
    if "student_email" in st.session_state:
        st.markdown(f"**Logged in as:**<br><span style='color:#0f766e;font-size:0.85rem;'>{st.session_state['student_email']}</span>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state["student_email"]
            st.rerun()
        st.markdown("---")

    # API key status
    from config import OPENAI_API_KEY
    if OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-key-here":
        st.markdown(
            """
            <div style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3);
                        border-radius:10px; padding:12px; text-align:center;">
                <span style="color:#34d399; font-size:0.85rem;">🟢 AI Agents Active</span>
                <br><span style="color:#6ee7b7; font-size:0.75rem;">Using GPT-4o-mini</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3);
                        border-radius:10px; padding:12px; text-align:center;">
                <span style="color:#fbbf24; font-size:0.85rem;">⚠️ Fallback Mode</span>
                <br><span style="color:#fcd34d; font-size:0.75rem;">Set OPENAI_API_KEY in .env</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div style="position:fixed; bottom:20px; left:20px; right:20px;">
            <p style="color:#4b5563; font-size:0.7rem; text-align:center;">
                v1.0.0 · Built with Multi-Agent AI
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Page Router ─────────────────────────────────────────────────────────
if page == "📝 Student Portal":
    if "student_email" not in st.session_state:
        from views.auth import render
        render()
    else:
        from views.student_portal import render
        render()
elif page == "🛡️ Admin Dashboard":
    from views.admin_dashboard import render
    render()
elif page == "🔍 Track Complaint":
    from views.tracking import render
    render()
elif page == "📊 Analytics":
    from views.analytics import render
    render()
