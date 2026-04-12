"""
Mail utilities — Handle sending OTPs and notifications.
"""

import random
import time
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SENDER_EMAIL, SMTP_SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT

def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp_email(email: str, otp: str) -> bool:
    """
    Send an OTP via email using SMTP.
    Falls back to mock console output if SMTP credentials are not found.
    """
    if not SMTP_SENDER_EMAIL or not SMTP_SENDER_PASSWORD:
        # ── MOCK EMAIL BEHAVIOR (For local dev only) ──
        try:
            print("=" * 60)
            print(f"⚠️ [NO SMTP CREDENTIALS FOUND IN .ENV]")
            print(f"[MOCK EMAIL SENT TO]: {email}")
            print(f"[OTP]: {otp}")
            print("=" * 60)
        except Exception:
            pass 
        
        st.toast(f"Note: No SMTP creds found. Check terminal for MOCK OTP.", icon="📫")
        return True

    # ── REAL SMTP EMAIL DISPATCH ──
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Campus Duvidha Solver <{SMTP_SENDER_EMAIL}>"
        msg['To'] = email
        msg['Subject'] = "Your Registration OTP - Campus Duvidha Solver"
        
        body = f"""
        Hello,

        Your One-Time Password (OTP) for Campus Duvidha Solver registration is: 
        
        {otp}
        
        Please enter this code in the portal to verify your account. 
        Do not share this code with anyone.

        Best regards,
        Admin Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_SENDER_EMAIL, SMTP_SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        st.toast(f"OTP successfully emailed to {email}", icon="✅")
        return True
    
    except Exception as e:
        print(f"SMTP Email Error: {e}")
        st.error("Failed to send OTP via Email. Check terminal logs.")
        return False
