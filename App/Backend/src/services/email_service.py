import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ── Gmail SMTP Configuration ──────────────────────────────────────────────────

SMTP_HOST = os.getenv(
    "SMTP_HOST",
    "smtp.gmail.com"
)

SMTP_PORT = int(
    os.getenv("SMTP_PORT", "587")
)

SMTP_EMAIL = os.getenv(
    "SMTP_EMAIL",
    ""
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD",
    ""
)

EMAIL_FROM_ADDRESS = os.getenv(
    "EMAIL_FROM_ADDRESS",
    SMTP_EMAIL
)

EMAIL_FROM_NAME = os.getenv(
    "EMAIL_FROM_NAME",
    "LMS Platform"
)


# ── Internal Email Helper ─────────────────────────────────────────────────────

def _send_email(
    to_email: str,
    subject: str,
    html_body: str
) -> bool:
    """
    Internal helper to send email using Gmail SMTP.
    Returns True if email is sent successfully.
    Returns False if sending fails.
    """

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logger.error(
            "Gmail SMTP credentials are not configured"
        )
        return False

    if not EMAIL_FROM_ADDRESS:
        logger.error(
            "EMAIL_FROM_ADDRESS is not configured"
        )
        return False

    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = (
        f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
    )
    msg["To"] = to_email

    msg.attach(
        MIMEText(
            html_body,
            "html"
        )
    )

    try:
        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=10
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            server.sendmail(
                EMAIL_FROM_ADDRESS,
                [to_email],
                msg.as_string()
            )

        logger.info(
            "Email sent successfully to %s | Subject: %s",
            to_email,
            subject
        )

        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(
            "Gmail SMTP authentication failed: %s",
            str(e)
        )
        return False

    except smtplib.SMTPSenderRefused as e:
        logger.error(
            "Sender email was refused: %s",
            str(e)
        )
        return False

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(
            "Recipient email was refused: %s",
            str(e)
        )
        return False

    except smtplib.SMTPException as e:
        logger.error(
            "SMTP error while sending email: %s",
            str(e)
        )
        return False

    except Exception as e:
        logger.exception(
            "Unexpected error while sending email: %s",
            str(e)
        )
        return False


# ── OTP Email ─────────────────────────────────────────────────────────────────

def send_otp_email(
    to_email: str,
    otp: str,
    purpose: str,
    username: str = ""
) -> bool:
    """
    Send a 6-digit OTP to the user's email.

    purpose:
    - email_verification
    - password_reset
    - recovery_email_verification
    """

    purpose_labels = {
        "email_verification": "Email Verification",
        "password_reset": "Password Reset",
        "recovery_email_verification":
            "Recovery Email Verification",
    }

    label = purpose_labels.get(
        purpose,
        "Verification"
    )

    greeting = (
        f"Hi {username},"
        if username
        else "Hello,"
    )

    subject = (
        f"Your {label} OTP - LMS Platform"
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                max-width: 480px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 8px;
                padding: 32px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .otp-box {{
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #4F46E5;
                text-align: center;
                padding: 20px;
                background: #EEF2FF;
                border-radius: 8px;
                margin: 24px 0;
            }}

            .footer {{
                font-size: 12px;
                color: #888888;
                margin-top: 24px;
            }}
        </style>

    </head>

    <body>

        <div class="container">

            <h2 style="color: #1e1e2e;">
                {label} OTP
            </h2>

            <p>{greeting}</p>

            <p>
                Use the following OTP to complete your
                <strong>{label}</strong>.
                It is valid for
                <strong>2 minutes</strong>.
            </p>

            <div class="otp-box">
                {otp}
            </div>

            <p>
                If you did not request this,
                please ignore this email.
            </p>

            <div class="footer">
                &copy; LMS Platform -
                This is an automated message,
                please do not reply.
            </div>

        </div>

    </body>

    </html>
    """

    return _send_email(
        to_email,
        subject,
        html_body
    )


# ── Teacher Invitation Email ──────────────────────────────────────────────────

def send_teacher_invite_email(
    to_email: str,
    invite_token: str,
    invited_by_name: str = "Admin",
    accept_url_base: str = ""
) -> bool:
    """
    Send teacher invitation email.
    """

    if accept_url_base:

        cta = f"""
        <p style="text-align:center; margin:24px 0;">

            <a
                href="{accept_url_base}?token={invite_token}"
                style="
                    background:#4F46E5;
                    color:#ffffff;
                    padding:12px 28px;
                    border-radius:6px;
                    text-decoration:none;
                    font-weight:bold;
                "
            >
                Accept Invitation
            </a>

        </p>

        <p style="font-size:12px; color:#888888;">

            Or copy this token manually:

            <br>

            <code
                style="
                    background:#f4f4f4;
                    padding:4px 8px;
                    border-radius:4px;
                "
            >
                {invite_token}
            </code>

        </p>
        """

    else:

        cta = f"""
        <p>
            Use the following invitation token
            to complete your registration:
        </p>

        <div
            style="
                font-size:14px;
                font-weight:bold;
                background:#EEF2FF;
                padding:16px;
                border-radius:8px;
                word-break:break-all;
                color:#4F46E5;
                margin:20px 0;
            "
        >
            {invite_token}
        </div>
        """

    subject = (
        "You're invited to join LMS as a Teacher"
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                max-width: 520px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 8px;
                padding: 32px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .footer {{
                font-size: 12px;
                color: #888888;
                margin-top: 24px;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h2 style="color: #1e1e2e;">
                Teacher Invitation
            </h2>

            <p>Hello,</p>

            <p>
                <strong>{invited_by_name}</strong>
                has invited you to join the
                <strong>LMS Platform</strong>
                as a <strong>Teacher</strong>.

                This invitation expires in
                <strong>48 hours</strong>.
            </p>

            {cta}

            <p>
                If you did not expect this invitation,
                you can safely ignore this email.
            </p>

            <div class="footer">
                &copy; LMS Platform -
                This is an automated message,
                please do not reply.
            </div>

        </div>

    </body>

    </html>
    """

    return _send_email(
        to_email,
        subject,
        html_body
    )


# ── Teacher Welcome Email ─────────────────────────────────────────────────────

def send_teacher_welcome_email(
    to_email: str,
    name: str,
    username: str,
    temporary_password: str | None = None
) -> bool:
    """
    Send welcome email when admin directly
    creates a teacher account.
    """

    password_section = ""

    if temporary_password:

        password_section = f"""
        <p>

            Your temporary password is:

            <strong
                style="
                    background:#EEF2FF;
                    padding:4px 8px;
                    border-radius:4px;
                    color:#4F46E5;
                "
            >
                {temporary_password}
            </strong>

            <br>

            Please change it after your first login.

        </p>
        """

    subject = (
        "Welcome to LMS Platform - Your Teacher Account"
    )

    html_body = f"""
    <!DOCTYPE html>
    <html>

    <head>

        <meta charset="UTF-8">

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}

            .container {{
                max-width: 520px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 8px;
                padding: 32px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}

            .footer {{
                font-size: 12px;
                color: #888888;
                margin-top: 24px;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h2 style="color: #1e1e2e;">
                Welcome, {name}!
            </h2>

            <p>
                Your teacher account has been created
                on the <strong>LMS Platform</strong>.
            </p>

            <p>

                <strong>Username:</strong>
                {username}

                <br>

                <strong>Email:</strong>
                {to_email}

            </p>

            {password_section}

            <p>
                Please verify your email address
                by logging in and requesting an OTP.
            </p>

            <div class="footer">

                &copy; LMS Platform -
                This is an automated message,
                please do not reply.

            </div>

        </div>

    </body>

    </html>
    """

    return _send_email(
        to_email,
        subject,
        html_body
    )