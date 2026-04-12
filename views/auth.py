import streamlit as st
import hashlib

from database.models import create_user, get_user_by_email

def hash_password(password: str) -> str:
    """Return SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def render():
    st.markdown('<h1 class="main-title">🔐 Student Portal Login</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Sign in with your @iiitranchi.ac.in email to submit and track your complaints.</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ── Login Tab ────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Welcome Back")
        login_email = st.text_input("College Email", key="login_email").strip()
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if not login_email or not login_password:
                st.warning("Please enter both email and password")
            elif not login_email.endswith("@iiitranchi.ac.in"):
                st.error("Please use your official @iiitranchi.ac.in email id.")
            else:
                user = get_user_by_email(login_email)
                if user and user["password_hash"] == hash_password(login_password):
                    st.session_state["student_email"] = login_email
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    # ── Register Tab ─────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Create an Account")
        reg_email = st.text_input("College Email", key="reg_email").strip()
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", type="primary", use_container_width=True):
            if not reg_email or not reg_password:
                st.warning("Please fill out all fields.")
            elif not reg_email.endswith("@iiitranchi.ac.in"):
                st.error("Registration failed! You must register using a valid @iiitranchi.ac.in email address.")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters long.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match!")
            else:
                # Check if user already exists
                existing_user = get_user_by_email(reg_email)
                if existing_user:
                    st.error("An account with this email already exists. Please login.")
                else:
                    try:
                        create_user(reg_email, hash_password(reg_password))
                        st.success("Registration successful! You can now log in.")
                    except Exception as e:
                        st.error(f"Error during registration: {e}")
