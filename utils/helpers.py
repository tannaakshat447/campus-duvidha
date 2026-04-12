"""
Helper utilities — tracking ID generation, formatting, and CSS injection.
"""

import uuid
import datetime


def generate_tracking_id() -> str:
    """Generate a human-friendly tracking ID like CPS-A3F8-2024."""
    short_uuid = uuid.uuid4().hex[:6].upper()
    year = datetime.datetime.now().strftime("%Y")
    return f"CPS-{short_uuid}-{year}"


def format_timestamp(ts_str: str) -> str:
    """Format a SQLite datetime string into a human-readable format."""
    if not ts_str:
        return "N/A"
    try:
        dt = datetime.datetime.fromisoformat(ts_str)
        # SQLite CURRENT_TIMESTAMP is in UTC. Attach UTC tzinfo and convert to local time.
        dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone()
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except (ValueError, TypeError):
        return ts_str


def priority_color(priority: str) -> str:
    """Return a CSS color for priority badges."""
    return {
        "Low": "#3b82f6",
        "Medium": "#f59e0b",
        "High": "#f97316",
        "Urgent": "#ef4444",
    }.get(priority, "#6b7280")


def sentiment_color(sentiment: str) -> str:
    """Return a CSS color for sentiment badges."""
    return {
        "Neutral": "#6b7280",
        "Frustrated": "#f59e0b",
        "Distressed": "#ef4444",
        "Angry": "#dc2626",
    }.get(sentiment, "#6b7280")


def status_color(status: str) -> str:
    """Return a CSS color for status badges."""
    return {
        "Submitted": "#6366f1",
        "In Progress": "#f59e0b",
        "Resolved": "#10b981",
    }.get(status, "#6b7280")


def confidence_bar_color(confidence: float) -> str:
    """Return a gradient color based on confidence level."""
    if confidence >= 0.85:
        return "#10b981"
    elif confidence >= 0.7:
        return "#3b82f6"
    elif confidence >= 0.55:
        return "#f59e0b"
    else:
        return "#ef4444"


def inject_custom_css():
    """Inject global custom CSS for the Streamlit app."""
    import streamlit as st
    st.markdown("""
    <style>
    /* ── Import Google Font ───────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Overrides ─────────────────────────────────── */
    .stApp > header {
        background: transparent;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }

    /* ── Cards ────────────────────────────────────────────── */
    .problem-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    .problem-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transform: translateY(-1px);
    }
    .problem-card.flagged {
        border-color: #fca5a5;
        box-shadow: 0 0 0 1px #fca5a5, 0 4px 12px rgba(220, 38, 38, 0.08);
    }

    /* ── Badges ───────────────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    /* ── Metric Cards ─────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    /* ── Agent Pipeline Visual ────────────────────────────── */
    .agent-step {
        background: #f8fafc;
        border-left: 4px solid #0f766e;
        border-radius: 0 8px 8px 0;
        padding: 14px 20px;
        margin-bottom: 10px;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
        transition: all 0.2s ease;
    }
    .agent-step:hover {
        background: #f1f5f9;
    }
    .agent-step.success {
        border-left-color: #059669;
    }
    .agent-step.error {
        border-left-color: #dc2626;
    }

    /* ── Confidence Bar ───────────────────────────────────── */
    .confidence-bar-bg {
        background: #e2e8f0;
        border-radius: 8px;
        height: 8px;
        overflow: hidden;
        margin-top: 6px;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 8px;
        transition: width 0.8s ease;
    }

    /* ── Timeline ─────────────────────────────────────────── */
    .timeline-item {
        position: relative;
        padding-left: 28px;
        margin-bottom: 20px;
    }
    .timeline-item::before {
        content: '';
        position: absolute;
        left: 8px;
        top: 0;
        bottom: -20px;
        width: 2px;
        background: #cbd5e1;
    }
    .timeline-item:last-child::before {
        display: none;
    }
    .timeline-item::after {
        content: '';
        position: absolute;
        left: 3px;
        top: 6px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #0f766e;
        border: 2px solid #ffffff;
    }

    /* ── Headings ─────────────────────────────────────────── */
    .main-title {
        color: #0f172a;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        color: #64748b;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 32px;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 24px;
        transition: all 0.2s ease;
    }

    /* ── Text Area & Inputs ───────────────────────────────── */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif;
    }

    /* ── Expander ─────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        color: #334155;
        border: 1px solid #e2e8f0;
    }

    /* ── Tabs ─────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #f8fafc !important;
        color: #0f766e !important;
        border-top: 1px solid #e2e8f0;
        border-left: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
    }

    /* ── Divider ──────────────────────────────────────────── */
    hr {
        border-color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_badge(text: str, color: str) -> str:
    """Return HTML for a small colored badge."""
    return f'<span class="badge" style="background: {color}22; color: {color}; border: 1px solid {color}44;">{text}</span>'


def render_confidence_bar(confidence: float) -> str:
    """Return HTML for a confidence bar."""
    pct = int(confidence * 100)
    color = confidence_bar_color(confidence)
    return f"""
    <div style="display:flex; align-items:center; gap:10px;">
        <div class="confidence-bar-bg" style="flex:1;">
            <div class="confidence-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
        <span style="color:{color}; font-weight:600; font-size:0.85rem;">{pct}%</span>
    </div>
    """
