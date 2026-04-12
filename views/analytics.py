"""
Analytics Dashboard — Data visualizations and agent pipeline stats.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database.models import (
    get_category_distribution, get_priority_distribution,
    get_sentiment_distribution, get_department_stats,
    get_daily_submissions, get_flagged_count, get_avg_confidence,
    get_fallback_rate, get_total_problems, get_all_agent_logs,
)
from utils.helpers import priority_color, sentiment_color


# ── Plotly theme ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#475569"),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(30,27,75,0.5)",
        bordercolor="rgba(99,102,241,0.2)",
        borderwidth=1,
    ),
)

COLORS = ["#6366f1", "#8b5cf6", "#a78bfa", "#c084fc", "#e879f9", "#f472b6",
          "#fb7185", "#f87171", "#fbbf24", "#34d399", "#2dd4bf", "#38bdf8"]


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

    st.markdown('<h1 class="main-title">📊 Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Visual insights into campus complaints, agent performance, and resolution metrics.</p>', unsafe_allow_html=True)

    # ── Quick Stats ─────────────────────────────────────────────────────
    total = get_total_problems()
    flagged = get_flagged_count()
    avg_conf = get_avg_confidence()
    fallback_rate = get_fallback_rate()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Total Complaints", total)
    c2.metric("🚨 Flagged", flagged)
    c3.metric("🎯 Avg Confidence", f"{avg_conf:.0%}")
    c4.metric("🔄 Fallback Rate", f"{fallback_rate:.1f}%")

    st.markdown("---")

    if total == 0:
        st.info("📭 No complaints yet. Submit some from the Student Portal to see analytics!")
        return

    # ── Row 1: Category Pie + Priority Bar ──────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏷️ Complaints by Category")
        cat_data = get_category_distribution()
        if cat_data:
            df = pd.DataFrame(cat_data)
            fig = px.pie(
                df, names="category", values="count",
                color_discrete_sequence=COLORS,
                hole=0.45,
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=12,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    with col2:
        st.markdown("### ⚡ Priority Breakdown")
        pri_data = get_priority_distribution()
        if pri_data:
            df = pd.DataFrame(pri_data)
            colors_map = {p: priority_color(p) for p in df["priority"]}
            fig = px.bar(
                df, x="priority", y="count",
                color="priority",
                color_discrete_map=colors_map,
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
            fig.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    # ── Row 2: Daily Submissions + Sentiment ────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### 📈 Submissions (Last 7 Days)")
        daily_data = get_daily_submissions(7)
        if daily_data:
            df = pd.DataFrame(daily_data)
            fig = px.line(
                df, x="date", y="count",
                markers=True,
                color_discrete_sequence=["#0f766e"],
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(xaxis_title="Date", yaxis_title="Submissions")
            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=10, symbol="circle"),
                fill="tozeroy",
                fillcolor="rgba(129,140,248,0.15)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No submissions in the last 7 days.")

    with col4:
        st.markdown("### 💭 Sentiment Distribution")
        sent_data = get_sentiment_distribution()
        if sent_data:
            df = pd.DataFrame(sent_data)
            colors_map = {s: sentiment_color(s) for s in df["sentiment"]}
            fig = px.bar(
                df, x="sentiment", y="count",
                color="sentiment",
                color_discrete_map=colors_map,
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
            fig.update_traces(marker_line_width=0, opacity=0.9)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data available.")

    st.markdown("---")

    # ── Row 3: Department Stats ─────────────────────────────────────────
    st.markdown("### 🏢 Department Performance")
    dept_data = get_department_stats()
    if dept_data:
        df = pd.DataFrame(dept_data)
        df["avg_resolution_hours"] = df["avg_resolution_hours"].fillna(0).round(1)

        # Bar chart: total vs resolved per department
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Total",
            x=df["department"],
            y=df["total"],
            marker_color="#6366f1",
            opacity=0.8,
        ))
        fig.add_trace(go.Bar(
            name="Resolved",
            x=df["department"],
            y=df["resolved"],
            marker_color="#10b981",
            opacity=0.8,
        ))
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_layout(
            barmode="group",
            xaxis_title="",
            yaxis_title="Complaints",
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Department stats table
        st.markdown("#### 📋 Detailed Stats")
        display_df = df[["department", "total", "resolved", "avg_resolution_hours"]].copy()
        display_df.columns = ["Department", "Total", "Resolved", "Avg Resolution (hrs)"]
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No department data available.")

    st.markdown("---")



    # ── Footer Stats ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align:center; padding:20px;">
            <span style="color:#64748b; font-size:0.85rem;">
                📊 {total} total complaints &nbsp;|&nbsp;
                🎯 {avg_conf:.0%} avg confidence &nbsp;|&nbsp;
                🔄 {fallback_rate:.1f}% fallback usage &nbsp;|&nbsp;
                🚨 {flagged} flagged
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
