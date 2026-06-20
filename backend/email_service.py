"""
Transactional email via Resend (https://resend.com). Chosen because
it has the simplest API of any provider for exactly this use case
(no SMTP fuss, generous free tier, clean HTML support) and pairs well
with Supabase/Streamlit Cloud deployments.

Required env var:
    RESEND_API_KEY=re_xxx
    EMAIL_FROM="Parent2Parent <noreply@yourdomain.com>"

If RESEND_API_KEY isn't set, these functions log instead of sending,
so local development doesn't require a live email account.
"""
from __future__ import annotations

import os
import logging

import requests

logger = logging.getLogger("p2p.email")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "Parent2Parent <noreply@parent2parent.app>")
BRAND_NAME = "Parent2Parent"
ACCENT_COLOR = "#3D5A80"  # matches styles/theme.py PRIMARY


def _send(to_email: str, subject: str, html: str) -> None:
    if not RESEND_API_KEY:
        logger.info("RESEND_API_KEY not set — email not sent. Subject=%r To=%r", subject, to_email)
        return

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={"from": EMAIL_FROM, "to": [to_email], "subject": subject, "html": html},
        timeout=10,
    )
    if resp.status_code >= 300:
        logger.error("Resend send failed: %s %s", resp.status_code, resp.text)
        raise RuntimeError("Could not send email right now. Try again shortly.")


def _base_template(body_html: str) -> str:
    return f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f6f8; padding: 32px 0;">
      <div style="max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 12px;
                  overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        <div style="background: linear-gradient(135deg, {ACCENT_COLOR}, #98C1D9); padding: 28px 32px;">
          <h1 style="color: #ffffff; margin: 0; font-size: 22px; letter-spacing: 0.3px;">{BRAND_NAME}</h1>
          <p style="color: rgba(255,255,255,0.9); margin: 4px 0 0; font-size: 13px;">
            Real people. Real problems. Real education.
          </p>
        </div>
        <div style="padding: 32px;">
          {body_html}
        </div>
        <div style="padding: 18px 32px; background: #f4f6f8; font-size: 12px; color: #8a93a1;">
          You're receiving this because you have an account with {BRAND_NAME}.
          If this wasn't you, you can safely ignore this email.
        </div>
      </div>
    </div>
    """


def send_verification_email(to_email: str, code: str, purpose: str = "signup") -> None:
    heading = "Confirm your email" if purpose == "signup" else "Your verification code"
    intro = (
        "Welcome! Enter this code to finish creating your account."
        if purpose == "signup"
        else "Use this code to continue."
    )
    body = f"""
        <h2 style="margin-top:0; color:#1f2733; font-size:18px;">{heading}</h2>
        <p style="color:#4a5568; font-size:14px; line-height:1.5;">{intro}</p>
        <div style="text-align:center; margin: 28px 0;">
          <span style="display:inline-block; font-size: 32px; font-weight: 700; letter-spacing: 8px;
                       color: {ACCENT_COLOR}; background:#eef2f7; padding: 14px 24px; border-radius: 10px;">
            {code}
          </span>
        </div>
        <p style="color:#8a93a1; font-size:12px;">This code expires in 15 minutes.</p>
    """
    _send(to_email, f"{code} is your {BRAND_NAME} verification code", _base_template(body))


def send_password_reset_email(to_email: str, code: str) -> None:
    body = f"""
        <h2 style="margin-top:0; color:#1f2733; font-size:18px;">Reset your password</h2>
        <p style="color:#4a5568; font-size:14px; line-height:1.5;">
          Enter this code in the app to set a new password.
        </p>
        <div style="text-align:center; margin: 28px 0;">
          <span style="display:inline-block; font-size: 32px; font-weight: 700; letter-spacing: 8px;
                       color: {ACCENT_COLOR}; background:#eef2f7; padding: 14px 24px; border-radius: 10px;">
            {code}
          </span>
        </div>
        <p style="color:#8a93a1; font-size:12px;">
          This code expires in 15 minutes. If you didn't request this, you can ignore this email.
        </p>
    """
    _send(to_email, f"{code} is your password reset code", _base_template(body))


def send_event_digest_email(to_email: str, first_name: str, events: list[dict]) -> None:
    if not events:
        return
    rows = ""
    for ev in events:
        rows += f"""
        <div style="border-left: 3px solid {ACCENT_COLOR}; padding: 10px 16px; margin-bottom: 14px; background:#f9fafb; border-radius: 0 8px 8px 0;">
          <div style="font-weight:600; color:#1f2733; font-size:15px;">{ev['title']}</div>
          <div style="color:{ACCENT_COLOR}; font-size:13px; margin-top:2px;">
            {ev['event_date']}{' · ' + ev['event_time'] if ev.get('event_time') else ''}
          </div>
          <div style="color:#4a5568; font-size:13px; margin-top:6px;">{ev.get('description','')}</div>
        </div>
        """
    body = f"""
        <h2 style="margin-top:0; color:#1f2733; font-size:18px;">Hi {first_name}, here's what's coming up</h2>
        <p style="color:#4a5568; font-size:14px; line-height:1.5;">
          A few upcoming Parent2Parent events you opted in to hear about:
        </p>
        {rows}
        <p style="color:#8a93a1; font-size:12px; margin-top:20px;">
          You can turn these off anytime in Settings.
        </p>
    """
    _send(to_email, "Upcoming Parent2Parent events", _base_template(body))
