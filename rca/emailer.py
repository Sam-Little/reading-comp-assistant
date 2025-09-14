# rca/emailer.py
import os, ssl, smtplib
from typing import Optional
from email.message import EmailMessage

def _get_env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name, default)
    return v.strip() if isinstance(v, str) else ""

def send_email(
    to_email: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    from_name: str = "Reading Comprehension Assistant",
) -> str:
    """
    Sends an email via Gmail SMTP using env vars:
      SMTP_USER   -> your Gmail address
      SMTP_PASS   -> your Gmail App Password (16 chars, no spaces)
    Optional overrides:
      SMTP_SERVER (default: smtp.gmail.com)
      SMTP_PORT   (default: 465)
      FROM_EMAIL  (default: SMTP_USER)
    Returns "OK" if sent, or an error string.
    """
    smtp_user = _get_env("SMTP_USER")
    smtp_pass = _get_env("SMTP_PASS")
    smtp_server = _get_env("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(_get_env("SMTP_PORT", "465") or "465")
    from_email = _get_env("FROM_EMAIL", smtp_user)

    if not smtp_user or not smtp_pass:
        return "Missing SMTP_USER/SMTP_PASS environment variables."

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = to_email

    if body_html:
        msg.set_content(body_text)
        msg.add_alternative(body_html, subtype="html")
    else:
        msg.set_content(body_text)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return "OK"
    except Exception as e:
        return f"Email error: {e}"
