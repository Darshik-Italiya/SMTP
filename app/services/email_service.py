import smtplib
import ssl
import aiohttp
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import List, Optional, Dict, Any
from pydantic import EmailStr

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.sender_email = settings.EMAIL_FROM
        self.sender_name = settings.EMAIL_FROM_NAME
        self.use_smtp_api = bool(settings.SMTP_API_KEY)

        if self.use_smtp_api:
            logger.info("Using SMTP.com API for sending emails")
            logger.debug(
                f"API Key: {'*' * 8 + settings.SMTP_API_KEY[-4:] if settings.SMTP_API_KEY else 'Not set'}"
            )
            logger.debug(f"Channel: {settings.SMTP_CHANNEL}")
        else:
            logger.info("Using direct SMTP for sending emails")
            self.smtp_server = settings.SMTP_SERVER
            self.smtp_port = settings.SMTP_PORT
            self.smtp_username = settings.SMTP_USERNAME
            self.smtp_password = settings.SMTP_PASSWORD

    async def _send_via_smtp_com(
        self,
        to_emails: List[EmailStr],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc_emails: Optional[List[EmailStr]] = None,
        bcc_emails: Optional[List[EmailStr]] = None,
    ) -> Dict[str, Any]:
        """Send email using SMTP.com API."""
        if not text_content:
            import re

            text_content = re.sub("<[^<]+?>", " ", html_content).strip()

        # Prepare email parts
        parts = [
            {"type": "text/plain", "content": text_content},
            {"type": "text/html", "content": html_content.strip()},
        ]

        # Prepare recipients
        recipients = {"to": [{"address": email} for email in to_emails]}
        if cc_emails:
            recipients["cc"] = [{"address": email} for email in cc_emails]
        if bcc_emails:
            recipients["bcc"] = [{"address": email} for email in bcc_emails]

        # Use the channel from settings or fallback to 'default'
        channel = getattr(settings, "SMTP_CHANNEL", "default")

        payload = {
            "channel": channel,
            "subject": subject,
            "body": {"parts": parts},
            "recipients": recipients,
            "originator": {
                "from_email": self.sender_email,
                "from_name": self.sender_name,
                "reply_to": {"email": self.sender_email},  # Changed to object format
            },
        }

        headers = {
            "Authorization": f"Bearer {settings.SMTP_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            logger.debug(f"Sending request to SMTP.com API: {settings.SMTP_API_URL}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    settings.SMTP_API_URL, headers=headers, json=payload
                ) as response:
                    response_text = await response.text()
                    logger.debug(f"Response status: {response.status}")
                    logger.debug(f"Response body: {response_text}")

                    try:
                        response_data = await response.json()
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}

                    if response.status in (200, 201, 202):
                        return {
                            "status": "success",
                            "message": "Email sent successfully via SMTP.com API",
                        }
                    else:
                        error_msg = response_data.get(
                            "message",
                            response_data.get(
                                "error", f"Failed with status {response.status}"
                            ),
                        )
                        logger.error(f"SMTP.com API error: {error_msg}")
                        return {
                            "status": "error",
                            "message": f"Failed to send email: {error_msg}",
                            "status_code": response.status,
                            "response": response_data,
                        }

        except Exception as e:
            error_msg = f"SMTP.com API request failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to connect to SMTP.com API: {str(e)}",
            }

    async def _send_via_direct_smtp(
        self,
        to_emails: List[EmailStr],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc_emails: Optional[List[EmailStr]] = None,
        bcc_emails: Optional[List[EmailStr]] = None,
    ) -> Dict[str, Any]:
        """Send email using direct SMTP connection."""
        if not text_content:
            import re

            text_content = re.sub("<[^<]+?>", "", html_content)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((self.sender_name, self.sender_email))
        msg["To"] = ", ".join(to_emails)

        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)

        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        all_recipients = to_emails.copy()
        if cc_emails:
            all_recipients.extend(cc_emails)
        if bcc_emails:
            all_recipients.extend(bcc_emails)

        try:
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if settings.USE_TLS:
                    server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender_email, all_recipients, msg.as_string())

            return {"status": "success", "message": "Email sent successfully"}

        except Exception as e:
            error_msg = f"Failed to send email via SMTP: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

    async def send_email(
        self,
        to_emails: List[EmailStr],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc_emails: Optional[List[EmailStr]] = None,
        bcc_emails: Optional[List[EmailStr]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email using the configured method (SMTP.com API or direct SMTP).

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional, will be auto-generated if not provided)
            cc_emails: List of CC email addresses (optional)
            bcc_emails: List of BCC email addresses (optional)

        Returns:
            dict: Status and message of the email sending operation
        """
        try:
            if self.use_smtp_api:
                return await self._send_via_smtp_com(
                    to_emails=to_emails,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                )
            else:
                return await self._send_via_direct_smtp(
                    to_emails=to_emails,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    cc_emails=cc_emails,
                    bcc_emails=bcc_emails,
                )
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}


# Create a singleton instance
email_service = EmailService()
