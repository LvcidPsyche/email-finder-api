"""
Email service integration for sending transactional emails.

Supports:
- SendGrid
- Mailgun
- SMTP (fallback)

Set EMAIL_SERVICE=sendgrid|mailgun|smtp in .env
"""
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "none")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@yourapi.com")
FROM_NAME = os.getenv("FROM_NAME", "Your API")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using configured email service.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML email body
        text_content: Plain text email body (optional)

    Returns:
        True if email sent successfully, False otherwise
    """
    if EMAIL_SERVICE == "none":
        logger.warning(f"Email service not configured. Would send email to {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Content preview: {html_content[:200]}...")
        return True

    try:
        if EMAIL_SERVICE == "sendgrid":
            return await _send_via_sendgrid(to_email, subject, html_content, text_content)
        elif EMAIL_SERVICE == "mailgun":
            return await _send_via_mailgun(to_email, subject, html_content, text_content)
        elif EMAIL_SERVICE == "smtp":
            return await _send_via_smtp(to_email, subject, html_content, text_content)
        else:
            logger.error(f"Unknown email service: {EMAIL_SERVICE}")
            return False
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def _send_via_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str]
) -> bool:
    """Send email via SendGrid API."""
    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg_api_key = os.getenv("SENDGRID_API_KEY")
        if not sg_api_key:
            logger.error("SENDGRID_API_KEY not set")
            return False

        sg = sendgrid.SendGridAPIClient(api_key=sg_api_key)
        
        from_email_obj = Email(FROM_EMAIL, FROM_NAME)
        to_email_obj = To(to_email)
        
        mail = Mail(
            from_email=from_email_obj,
            to_emails=to_email_obj,
            subject=subject,
            html_content=Content("text/html", html_content)
        )
        
        if text_content:
            mail.add_content(Content("text/plain", text_content))

        response = sg.send(mail)
        logger.info(f"SendGrid email sent to {to_email}: {response.status_code}")
        return response.status_code in [200, 201, 202]

    except ImportError:
        logger.error("sendgrid package not installed. Run: pip install sendgrid")
        return False
    except Exception as e:
        logger.error(f"SendGrid error: {str(e)}")
        return False


async def _send_via_mailgun(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str]
) -> bool:
    """Send email via Mailgun API."""
    try:
        import aiohttp

        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        
        if not mailgun_domain or not mailgun_api_key:
            logger.error("MAILGUN_DOMAIN or MAILGUN_API_KEY not set")
            return False

        async with aiohttp.ClientSession() as session:
            data = {
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": to_email,
                "subject": subject,
                "html": html_content
            }
            if text_content:
                data["text"] = text_content

            async with session.post(
                f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
                auth=aiohttp.BasicAuth("api", mailgun_api_key),
                data=data
            ) as response:
                result = await response.json()
                logger.info(f"Mailgun email sent to {to_email}: {response.status}")
                return response.status == 200

    except ImportError:
        logger.error("aiohttp package not installed. Run: pip install aiohttp")
        return False
    except Exception as e:
        logger.error(f"Mailgun error: {str(e)}")
        return False


async def _send_via_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str]
) -> bool:
    """Send email via SMTP (fallback method)."""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        smtp_host = os.getenv("SMTP_HOST", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        smtp_tls = os.getenv("SMTP_TLS", "true").lower() == "true"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_tls:
                server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        logger.info(f"SMTP email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"SMTP error: {str(e)}")
        return False


async def send_welcome_email(
    user_email: str,
    api_key: str,
    plan_tier: str,
    product_name: str,
    docs_url: str
) -> bool:
    """
    Send welcome email to new user with API key.

    Args:
        user_email: User's email address
        api_key: Generated API key
        plan_tier: Plan tier name (free, starter, pro, enterprise)
        product_name: Name of the product
        docs_url: URL to API documentation

    Returns:
        True if email sent successfully
    """
    subject = f"Welcome to {product_name} - Your API Key"
    
    # Import welcome email template from gumroad_integration
    try:
        from gumroad_integration import generate_welcome_email_html
        html_content = generate_welcome_email_html(
            user_email, api_key, plan_tier, product_name, docs_url
        )
    except ImportError:
        # Fallback simple template
        html_content = f"""
        <html>
        <body>
            <h1>Welcome to {product_name}!</h1>
            <p>Your API key: <code>{api_key}</code></p>
            <p>Plan: {plan_tier}</p>
            <p><a href="{docs_url}">View Documentation</a></p>
        </body>
        </html>
        """

    return await send_email(user_email, subject, html_content)
