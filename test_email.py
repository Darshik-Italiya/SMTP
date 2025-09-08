import asyncio
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Log environment variables (masking sensitive data)
logger.info("Environment variables loaded:")
for var in ["SMTP_SERVER", "SMTP_PORT", "SMTP_USE_TLS", "EMAIL_FROM"]:
    logger.info(f"  {var}: {os.getenv(var)}")
logger.info(
    "  SMTP_USERNAME: set" if os.getenv("SMTP_USERNAME") else "  SMTP_USERNAME: not set"
)
logger.info(
    "  SMTP_PASSWORD: set" if os.getenv("SMTP_PASSWORD") else "  SMTP_PASSWORD: not set"
)


async def test_smtp_connection():
    """Test SMTP connection and authentication."""
    import aiosmtplib

    try:
        logger.info("Testing SMTP connection...")

        # First try with STARTTLS (port 587)
        smtp = aiosmtplib.SMTP(
            hostname=os.getenv("SMTP_SERVER"),
            port=int(os.getenv("SMTP_PORT", "587")),
            use_tls=False,  # We'll use STARTTLS explicitly
            timeout=10,
        )

        await smtp.connect()
        logger.info("SMTP connection established")

        # Only try STARTTLS if not already using TLS and port is 587
        if (
            os.getenv("SMTP_USE_TLS", "").lower() == "true"
            and os.getenv("SMTP_PORT") == "587"
        ):
            try:
                logger.info("Starting TLS...")
                await smtp.starttls()
                logger.info("TLS started successfully")
            except aiosmtplib.SMTPException as e:
                if "already using TLS" in str(e):
                    logger.info("Connection is already using TLS")
                else:
                    raise

        if os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD"):
            logger.info("Authenticating...")
            await smtp.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            logger.info("Authentication successful")

        await smtp.quit()
        return True

    except Exception as e:
        logger.error(f"SMTP test failed: {str(e)}", exc_info=True)

        # Try alternative port 465 with SSL
        if "587" in str(os.getenv("SMTP_PORT", "")):
            logger.info("Trying alternative port 465 with SSL...")
            try:
                smtp = aiosmtplib.SMTP(
                    hostname=os.getenv("SMTP_SERVER"),
                    port=465,
                    use_tls=True,
                    timeout=10,
                )
                await smtp.connect()
                logger.info("Connected to port 465 with SSL")

                if os.getenv("SMTP_USERNAME") and os.getenv("SMTP_PASSWORD"):
                    await smtp.login(
                        os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD")
                    )
                    logger.info("Authentication successful on port 465")

                await smtp.quit()
                return True

            except Exception as e2:
                logger.error(f"Also failed on port 465: {str(e2)}")
                return False

        return False

    finally:
        if "smtp" in locals() and hasattr(smtp, "is_connected") and smtp.is_connected:
            try:
                await smtp.quit()
            except:
                pass


async def test_send_email():
    from app.services.email_service import email_service

    try:
        logger.info("Starting email test...")

        # Test with a simple email
        test_recipient = "rahulbodara7@gmail.com"
        logger.info(f"Sending test email to {test_recipient}...")

        result = await email_service.send_email(
            to_emails=[test_recipient],
            subject="Test Email from FastAPI",
            html_content="""
            <h1>Hello from FastAPI Email Service!</h1>
            <p>This is a test email sent using the FastAPI SMTP service.</p>
            <p>If you're seeing this, the email was sent successfully!</p>
            """,
        )

        logger.info(f"Email send result: {result}")

        if result.get("status") == "sent":
            print("✅ Email sent successfully!")
            print(f"Recipients: {', '.join(result.get('recipients', []))}")
            return True
        else:
            print("❌ Failed to send email")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        logger.error(f"Error in test_send_email: {str(e)}", exc_info=True)
        print(f"❌ An error occurred: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Testing email service...")

    # First test the SMTP connection
    print("\n🔍 Testing SMTP connection...")
    connection_success = asyncio.run(test_smtp_connection())

    if connection_success:
        print("✅ SMTP connection test passed!")

        # If connection is good, test sending an email
        print("\n✉️  Testing email sending...")
        email_success = asyncio.run(test_send_email())

        if email_success:
            print("\n✅ All tests passed! Check your email inbox.")
        else:
            print("\n❌ Email sending test failed. Check the logs above for details.")
    else:
        print(
            "\n❌ SMTP connection test failed. Please check your SMTP settings and try again."
        )
        print("\nTroubleshooting tips:")
        print("1. Verify your Gmail App Password is correct")
        print("2. Make sure 'Less secure app access' is enabled in your Google Account")
        print("3. Check if your firewall is blocking the connection")
        print("4. Try using a different network connection")
        print("\nFor more help, please share the error messages above.")
