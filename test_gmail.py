import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email():
    try:
        # Import here to ensure the path is set up first
        from app.services.email_service import email_service
        
        logger.info("Starting email test...")
        
        # Get test email from user
        test_email = input("Enter your test email address: ").strip()
        
        if not test_email or '@' not in test_email:
            print("❌ Please enter a valid email address")
            return
            
        print("Sending test email...")
        
        result = await email_service.send_email(
            to_emails=[test_email],
            subject="Test Email from Gmail SMTP",
            html_content="""
            <h1>Test Email</h1>
            <p>This is a test email sent via Gmail SMTP.</p>
            <p>If you're seeing this, the email service is working correctly!</p>
            """
        )
        
        logger.info("Email send result: %s", result)
        
        if result.get('status') == 'success':
            print("✅ Email sent successfully! Please check your inbox (and spam folder).")
        else:
            print("❌ Failed to send email:", result.get('message', 'Unknown error'))
            
    except ImportError as e:
        print("❌ Could not import email service:", str(e))
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        logger.error("Error during email test: %s", str(e), exc_info=True)
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Testing Gmail SMTP configuration...")
    print("Make sure you've updated the .env file with your Gmail app password")
    print("-" * 50)
    
    # Run the async function
    asyncio.run(test_email())
