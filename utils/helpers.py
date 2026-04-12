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
    """Inject global custom CSS for the Streamlit app with Modern Glassmorphism layout."""
    import streamlit as st
    st.markdown("""
    <style>
    /* ── Import Google Fonts ──────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Global Overrides ─────────────────────────────────── */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        font-family: 'Inter', sans-serif;
    }
    .stApp > header {
        background: transparent;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.4);
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }

    /* ── Cards (Glassmorphism) ────────────────────────────── */
    .problem-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .problem-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.08);
        border-color: rgba(255, 255, 255, 0.8);
    }
    .problem-card.flagged {
        border: 1px solid rgba(252, 165, 165, 0.8);
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.1);
    }

    /* ── Badges ───────────────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-family: 'Outfit', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        backdrop-filter: blur(4px);
    }

    /* ── Metric Cards ─────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: scale(1.02);
    }

    /* ── Agent Pipeline Visual ────────────────────────────── */
    .agent-step {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border-left: 4px solid #0f766e;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        border-top: 1px solid rgba(255,255,255,0.8);
        border-right: 1px solid rgba(255,255,255,0.8);
        border-bottom: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    .agent-step:hover {
        background: rgba(255, 255, 255, 0.9);
        transform: translateX(4px);
    }
    .agent-step.success {
        border-left-color: #059669;
    }

    /* ── Headings ─────────────────────────────────────────── */
    .main-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #1e1b4b 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }
    .sub-title {
        color: #64748b;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 32px;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {
        border-radius: 12px;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }

    /* ── Inputs ───────────────────────────────────────────── */
    .stTextArea textarea, .stTextInput input, .stSelectbox select {
        border-radius: 12px !important;
        background: rgba(255,255,255,0.7) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(4px);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Expander ─────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.5);
    }
    hr {
        border-color: rgba(0,0,0,0.06) !important;
    }

    /* ── Timeline ─────────────────────────────────────────── */
    .timeline-item { position:relative; padding-left:28px; margin-bottom:20px; }
    .timeline-item::before { content:''; position:absolute; left:8px; top:0; bottom:-20px; width:2px; background:rgba(99,102,241,0.3); }
    .timeline-item:last-child::before { display:none; }
    .timeline-item::after { content:''; position:absolute; left:3px; top:6px; width:12px; height:12px; border-radius:50%; background:#4f46e5; border:2px solid #fff; box-shadow:0 0 0 2px rgba(99,102,241,0.2); }
    
    /* ── Animations ───────────────────────────────────────── */
    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .problem-card, .agent-step { animation: fadeInSlide 0.5s ease forwards; }

    /* ── Tabs Overrides ───────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] { background: transparent; padding: 4px; border-radius: 16px; gap: 8px; border:none; }
    .stTabs [data-baseweb="tab"] { background: rgba(255,255,255,0.5); border-radius: 12px; padding: 12px 24px; font-weight: 600; font-family:'Outfit', sans-serif; transition:all 0.2s; border: 1px solid rgba(255,255,255,0.2); }
    .stTabs [aria-selected="true"] { background: rgba(255,255,255,0.95) !important; color: #4f46e5 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }

    /* ── Confidence Bar ───────────────────────────────────── */
    .confidence-bar-bg { background: rgba(0,0,0,0.05); height: 10px; border-radius: 10px; margin-top: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); }
    .confidence-bar-fill { height: 100%; border-radius: 10px; transition: width 1s cubic-bezier(0.4, 0, 0.2, 1); }
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

def trigger_professional_success():
    """Renders a sleek checkmark animation and plays a professional UI chime via Web Audio API."""
    import streamlit.components.v1 as components
    html_code = """
    <style>
    .success-container {
        display: flex; justify-content: center; align-items: center; padding: 20px;
        animation: fadeIn 0.5s ease-out forwards;
    }
    .check-icon {
        width: 80px; height: 80px; border-radius: 50%; display: block;
        stroke-width: 3; stroke: #10b981; stroke-miterlimit: 10;
        box-shadow: inset 0px 0px 0px #10b981;
        animation: fill 0.4s ease-in-out 0.4s forwards, scale 0.3s ease-in-out 0.9s both;
    }
    .check-icon-circle {
        stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 3; stroke-miterlimit: 10;
        stroke: #10b981; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
    }
    .check-icon-check {
        transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48;
        stroke: #fff; stroke-width: 3; fill: none; 
        animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
    }
    @keyframes stroke { 100% { stroke-dashoffset: 0; } }
    @keyframes scale { 0%, 100% { transform: none; } 50% { transform: scale3d(1.1, 1.1, 1); } }
    @keyframes fill { 100% { box-shadow: inset 0px 0px 0px 50px #10b981; } }
    @keyframes fadeIn { 0% { opacity: 0; transform: translateY(-10px); } 100% { opacity: 1; transform: translateY(0); } }
    </style>
    <div class="success-container">
        <svg class="check-icon" viewBox="0 0 52 52">
            <circle class="check-icon-circle" cx="26" cy="26" r="25" />
            <path class="check-icon-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
        </svg>
    </div>
    <script>
    setTimeout(function() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function playNote(freq, startTime, duration) {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, startTime);
                gain.gain.setValueAtTime(0, startTime);
                gain.gain.linearRampToValueAtTime(0.15, startTime + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
                osc.start(startTime);
                osc.stop(startTime + duration);
            }
            const now = ctx.currentTime;
            playNote(783.99, now, 0.4); // G5 
            playNote(1046.50, now + 0.15, 0.6); // C6 
        } catch(e) {}
    }, 100);
    </script>
    """
    components.html(html_code, height=140)
