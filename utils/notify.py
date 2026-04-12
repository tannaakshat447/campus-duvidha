"""
Notification utilities — in-app notifications via Streamlit.
Extensible for email / SMS / webhook in production.
"""

import streamlit as st


def notify_admin_flagged(tracking_id: str, summary: str, sentiment: str):
    """Show a toast-style warning for flagged complaints."""
    st.toast(
        f"🚨 FLAGGED [{sentiment}] — {tracking_id}: {summary}",
        icon="🔴",
    )


def notify_submission_success(tracking_id: str):
    """Show a success toast after complaint submission."""
    st.toast(
        f"✅ Complaint submitted! Tracking ID: {tracking_id}",
        icon="✅",
    )


def notify_status_change(tracking_id: str, old_status: str, new_status: str):
    """Show a toast for status updates."""
    st.toast(
        f"📝 {tracking_id}: {old_status} → {new_status}",
        icon="📝",
    )
