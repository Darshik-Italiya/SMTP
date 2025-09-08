from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging

from app.config import settings
from app.services.email_service import email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A FastAPI service for sending emails via Gmail SMTP",
    version="1.0.0",
)

# CORS middleware configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with your frontend URL
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Request models
class EmailRecipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class EmailContent(BaseModel):
    subject: str
    html_content: str
    text_content: Optional[str] = None


class EmailRequest(BaseModel):
    to: List[EmailStr]
    subject: str
    html_content: str
    text_content: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


# Health check endpoint
# @app.get("/")
# async def root():
#     return {
#         "status": "ok",
#         "message": f"{settings.APP_NAME} is running",
#         "version": "1.0.0"
#     }


# Email sending endpoint
@app.post("/api/emails/send", status_code=status.HTTP_200_OK)
async def send_email(email_request: EmailRequest):
    """
    Send an email using Gmail SMTP

    - **to**: List of recipient email addresses
    - **subject**: Email subject
    - **html_content**: HTML content of the email
    - **text_content**: Plain text content (optional, will be auto-generated if not provided)
    - **cc**: List of CC email addresses (optional)
    - **bcc**: List of BCC email addresses (optional)
    """
    try:
        result = await email_service.send_email(
            to_emails=email_request.to,
            subject=email_request.subject,
            html_content=email_request.html_content,
            text_content=email_request.text_content,
            cc_emails=email_request.cc,
            bcc_emails=email_request.bcc,
        )

        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Email sent successfully",
                "data": {
                    "to": email_request.to,
                    "subject": email_request.subject,
                    "cc": email_request.cc,
                    "bcc": email_request.bcc,
                },
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to send email"),
            )
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


# Example usage at startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Dental Patient Triage Service...")
    logger.info(f"Email sender: {settings.EMAIL_FROM}")

    if settings.DEBUG:
        logger.info("Running in DEBUG mode")
        # Only send test email if we have a valid channel configured
        if (
            hasattr(settings, "SMTP_CHANNEL")
            and settings.SMTP_CHANNEL
            and settings.SMTP_CHANNEL != "smtpcom"
        ):
            test_result = await email_service.send_email(
                to_emails=[settings.EMAIL_FROM],
                subject="Dental Triage Service Started",
                html_content="<h1>Service Started</h1><p>The Dental Triage Service has started successfully.</p>",
            )
            if test_result.get("status") != "success":
                logger.warning(f"Test email failed: {test_result.get('message')}")
        else:
            logger.warning("Skipping test email - no valid SMTP channel configured")


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return {
        "status": "error",
        "message": "An unexpected error occurred",
        "details": str(exc),
    }, status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
