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


# ── Premium Plotly Theme ────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#334155"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(showgrid=False, zeroline=False, color="#94a3b8"),
    yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False, color="#94a3b8"),
    legend=dict(
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="rgba(0,0,0,0.05)",
        borderwidth=1,
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
)

COLORS = ["#4f46e5", "#8b5cf6", "#ec4899", "#f43f5e", "#f59e0b", "#10b981", "#06b6d4", "#3b82f6"]


def render_metric_card(title: str, value: str, icon: str):
    """Render a custom glassmorphism metric card."""
    st.markdown(f"""
    <div class="problem-card" style="padding:20px; text-align:center;">
        <div style="font-size:2rem; margin-bottom:8px;">{icon}</div>
        <div style="color:#64748b; font-size:0.9rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">{title}</div>
        <div style="color:#1e1b4b; font-size:2.2rem; font-weight:800; font-family:'Outfit', sans-serif;">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render():
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    if not st.session_state["admin_authenticated"]:
        st.markdown('<h1 class="main-title">🔒 Admin Login</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Please enter the admin PIN to secure your dashboard.</p>', unsafe_allow_html=True)
        
        pwd = st.text_input("Admin PIN", type="password", key="admin_login_pin")
        if st.button("Login", type="primary"):
            if pwd == "Admin@123":
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid PIN")
        return

    st.markdown('<h1 class="main-title">📊 Analytics Central</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Comprehensive insights into campus resolution metrics.</p>', unsafe_allow_html=True)

    # Global Stats
    total = get_total_problems()
    
    if total == 0:
        st.info("📭 No complaints to analyze yet. Check back once students submit requests!")
        return

    # Tabs structure
    t_overview, t_dept, t_ai = st.tabs(["🌎 Overview", "🏢 Departments", "🤖 AI Performance"])

    # ── TAB 1: OVERVIEW ──────────────────────────────────────────────────
    with t_overview:
        flagged = get_flagged_count()
        avg_conf = get_avg_confidence()

        c1, c2, c3 = st.columns(3)
        with c1: render_metric_card("Total Complaints", str(total), "📋")
        with c2: render_metric_card("Avg AI Confidence", f"{avg_conf:.0%}", "🎯")
        with c3: render_metric_card("Flagged Issues", str(flagged), "🚨")

        st.markdown("---")

        st.markdown("### 📈 7-Day Submission Trend")
        daily_data = get_daily_submissions(7)
        if daily_data:
            df = pd.DataFrame(daily_data)
            fig = px.area(
                df, x="date", y="count",
                color_discrete_sequence=["#4f46e5"],
            )
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_traces(mode="lines+markers", marker=dict(size=8), line_shape="spline", fillcolor="rgba(79,70,229,0.15)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No recent data.")

        # Side by side charts
        col_cat, col_pri = st.columns(2)
        with col_cat:
            st.markdown("### 🏷️ Category Spread")
            cat_data = get_category_distribution()
            if cat_data:
                df = pd.DataFrame(cat_data)
                fig = px.pie(df, names="category", values="count", hole=0.6, color_discrete_sequence=COLORS)
                fig.update_layout(**PLOTLY_LAYOUT)
                fig.update_traces(textinfo="percent", hoverinfo="label+value")
                st.plotly_chart(fig, use_container_width=True)

        with col_pri:
            st.markdown("### ⚡ Priority Levels")
            pri_data = get_priority_distribution()
            if pri_data:
                df = pd.DataFrame(pri_data)
                colors_map = {p: priority_color(p) for p in df["priority"]}
                fig = px.bar(df, x="priority", y="count", color="priority", color_discrete_map=colors_map)
                fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
                fig.update_traces(marker_line_width=0, opacity=0.9, marker_line_color="rgba(0,0,0,0)")
                # Hide x axis title easily via layout updates inside the layout dict but we can do it here
                fig.update_xaxes(title_text="")
                fig.update_yaxes(title_text="Count")
                st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: DEPARTMENTS ───────────────────────────────────────────────
    with t_dept:
        st.markdown("### 🏢 Department Deep-Dive")
        dept_data = get_department_stats()
        if dept_data:
            df = pd.DataFrame(dept_data)
            df["avg_resolution_hours"] = df["avg_resolution_hours"].fillna(0).round(1)
            # Calculate pending workload
            df["pending"] = df["total"] - df["resolved"]
            # Sort by total workload descending
            df = df.sort_values(by="total", ascending=True)

            cd1, cd2 = st.columns([1.5, 1])
            
            with cd1:
                st.markdown("#### Workload Distribution")
                # Premium Horizontal Bar Chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name="Pending",
                    y=df["department"],
                    x=df["pending"],
                    orientation='h',
                    marker=dict(color="#ef4444", line=dict(width=0))
                ))
                fig.add_trace(go.Bar(
                    name="Resolved",
                    y=df["department"],
                    x=df["resolved"],
                    orientation='h',
                    marker=dict(color="#10b981", line=dict(width=0))
                ))
                fig.update_layout(barmode='stack', **PLOTLY_LAYOUT)
                fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                fig.update_yaxes(title_text="", showgrid=False)
                fig.update_xaxes(title_text="Number of Complaints", showgrid=True, gridcolor="rgba(0,0,0,0.05)")
                st.plotly_chart(fig, use_container_width=True)

            with cd2:
                st.markdown("#### ⚡ Efficiency Metrics")
                # Rather than a boring dataframe, render glassmorphism metric cards
                for idx, row in df.sort_values("total", ascending=False).iterrows():
                    res_rate = int((row["resolved"] / row["total"]) * 100) if row["total"] > 0 else 0
                    color = "#10b981" if res_rate >= 80 else ("#f59e0b" if res_rate >= 50 else "#ef4444")
                    
                    card_html = f"""
                    <div style="background:rgba(255,255,255,0.6); backdrop-filter:blur(8px); border:1px solid rgba(0,0,0,0.05); border-radius:12px; padding:16px; margin-bottom:12px; box-shadow:0 4px 12px rgba(0,0,0,0.02); transition:transform 0.2s;">
                        <h4 style="margin:0 0 8px 0; color:#1e293b; font-family:'Outfit', sans-serif; font-size:1.05rem;">{row['department']}</h4>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:2rem; font-weight:800; color:#4f46e5;">{row['total']}</span>
                                <span style="color:#64748b; font-size:0.8rem; margin-left:4px;">Total</span>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:{color}; font-weight:700; font-size:1.1rem;">{res_rate}% Resolved</div>
                                <div style="color:#94a3b8; font-size:0.75rem;">Avg Time: {row['avg_resolution_hours']} hrs</div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No department data available yet.")

    # ── TAB 3: AI PERFORMANCE ────────────────────────────────────────────
    with t_ai:
        fallback = get_fallback_rate()
        
        ca1, ca2 = st.columns(2)
        with ca1:
            st.markdown("### 💭 Sentiment Engine")
            sent_data = get_sentiment_distribution()
            if sent_data:
                df = pd.DataFrame(sent_data)
                colors_map = {s: sentiment_color(s) for s in df["sentiment"]}
                fig = px.pie(df, names="sentiment", values="count", hole=0.5, color="sentiment", color_discrete_map=colors_map)
                fig.update_layout(**PLOTLY_LAYOUT)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        with ca2:
            st.markdown("### ⚙️ System Fallback")
            st.markdown(f"""
            <div class="problem-card" style="margin-top:20px; text-align:center;">
                <h3 style="font-size:3rem; color:#f59e0b; margin:0;">{fallback:.1f}%</h3>
                <p style="color:#64748b; font-weight:600;">Fallback Usage Rate</p>
                <span style="font-size:0.8rem; color:#94a3b8;">When AI agents are unavailable, the system successfully relies on regex keyword heuristics.</span>
            </div>
            """, unsafe_allow_html=True)
