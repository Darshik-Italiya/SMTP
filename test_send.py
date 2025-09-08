import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import email_service

async def send_test_email():
    """Send a test email using the email service."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Test email details
        to_email = os.getenv("EMAIL_FROM")  # Send to yourself for testing
        subject = "Test Email from FastAPI Email Service"
        
        # HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4a6fa5; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }
                .content { padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px; }
                .footer { margin-top: 20px; font-size: 12px; color: #666; text-align: center; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Hello from FastAPI Email Service! 👋</h1>
                </div>
                <div class="content">
                    <p>This is a test email sent from the FastAPI Email Service using Gmail SMTP.</p>
                    <p>If you're seeing this, your email service is working correctly! 🎉</p>
                    <p>You can now use this service to send emails from your application.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text content (optional)
        text_content = """
        Hello from FastAPI Email Service!
        
        This is a test email sent from the FastAPI Email Service using Gmail SMTP.
        
        If you're seeing this, your email service is working correctly!
        
        You can now use this service to send emails from your application.
        
        ---
        This is an automated message, please do not reply to this email.
        """
        
        print(f"Sending test email to: {to_email}")
        
        # Send the email
        result = await email_service.send_email(
            to_emails=[to_email],
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
        
        if result["status"] == "success":
            print("✅ Test email sent successfully!")
            print(f"   - To: {to_email}")
            print(f"   - Subject: {subject}")
        else:
            print("❌ Failed to send test email:")
            print(f"   - Error: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(send_test_email())
