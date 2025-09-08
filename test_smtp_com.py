import asyncio
import aiohttp
import json
import logging
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def list_smtp_channels(api_key: str):
    """List available SMTP.com channels."""
    url = "https://api.smtp.com/v4/account/channels"
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response_text = await response.text()
                try:
                    return await response.json()
                except json.JSONDecodeError:
                    return {"error": "Invalid JSON response", "response": response_text}
    except Exception as e:
        return {"error": str(e)}


async def test_smtp_com_api():
    """Test SMTP.com API connectivity and authentication."""
    api_key = os.getenv("SMTP_API_KEY")

    if not api_key:
        print("❌ Error: SMTP_API_KEY not found in .env file")
        return

    # First, list available channels
    print("\n🔍 Listing available channels...")
    channels = await list_smtp_channels(api_key)
    print("Available channels:")
    print(json.dumps(channels, indent=2))

    # Get the first available channel or use 'default'
    channel_id = "default"
    if isinstance(channels, dict) and "data" in channels and channels["data"]:
        channel_id = channels["data"][0].get("id", "default")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "channel": channel_id,
        "subject": "SMTP.com API Test",
        "body": {
            "parts": [
                {
                    "type": "text/plain",
                    "content": "This is a test email from SMTP.com API",
                },
                {
                    "type": "text/html",
                    "content": "<h1>Test Email</h1><p>This is a test email from SMTP.com API</p>",
                },
            ]
        },
        "recipients": {"to": [{"address": "dai.globaila@gmail.com"}]},
        "originator": {
            "from_email": "no-reply@dentalpatienttriage.com",
            "from_name": "Dental Patient Triage",
            "reply_to": {"email": "no-reply@dentalpatienttriage.com"},
        },
    }

    print("\n🚀 Testing SMTP.com API...")
    print(f"Using channel: {channel_id}")
    print(
        f"From: {payload['originator']['from_email']} ({payload['originator']['from_name']})"
    )
    print(f"To: {[r['address'] for r in payload['recipients']['to']]}")

    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("\nSending test email...")
            async with session.post(
                "https://api.smtp.com/v4/messages", headers=headers, json=payload
            ) as response:
                response_text = await response.text()
                print(f"\nResponse Status: {response.status}")
                print("Response Headers:")
                for k, v in response.headers.items():
                    print(f"  {k}: {v}")

                try:
                    response_data = json.loads(response_text)
                    print("\nResponse JSON:")
                    print(json.dumps(response_data, indent=2))
                except json.JSONDecodeError:
                    print("\nResponse Text:")
                    print(response_text)

                if response.status in (200, 201, 202):
                    print("\n✅ Test email sent successfully!")
                else:
                    error_msg = response_data.get("message", "Unknown error")
                    if "data" in response_data:
                        error_msg += f"\nValidation errors: {json.dumps(response_data.get('data'), indent=2)}"
                    print(f"\n❌ Failed to send email: {error_msg}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_smtp_com_api())
