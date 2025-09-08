#!/bin/bash

# SMTP.com API Test Script
# Make this script executable: chmod +x test_api.sh
# Run: ./test_api.sh

# API Configuration
API_KEY="33d4a40e35956ebcefb2591e2f982a048f86dd10"
API_URL="https://api.smtp.com/v4/messages"
SENDER_EMAIL="riverinadentalalbury@gmail.com"
SENDER_NAME="Dental Patient Triage Service"
RECIPIENT_EMAIL="rahulbodara7@gmail.com"

# Create test payload
PAYLOAD=$(cat <<EOF
{
  "channel": "smtpcom",
  "subject": "SMTP.com API Test",
  "body": {
    "html": "<h1>Test Email</h1><p>This is a test email from SMTP.com API</p>",
    "text": "This is a test email from SMTP.com API"
  },
  "recipients": {
    "to": [{"email": "$RECIPIENT_EMAIL"}]
  },
  "originator": {
    "from_email": "$SENDER_EMAIL",
    "from_name": "$SENDER_NAME"
  }
}
EOF
)

echo "Testing SMTP.com API..."
echo "API URL: $API_URL"
echo "Sender: $SENDER_EMAIL"
echo "Recipient: $RECIPIENT_EMAIL"
echo ""
echo "Request Payload:"
echo $PAYLOAD | jq .
echo ""

# Make the API request
echo "Sending request to SMTP.com API..."
response=$(curl -s -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  $API_URL)

echo ""
echo "API Response:"
echo $response | jq .

# Check if jq is installed to format JSON
if ! command -v jq &> /dev/null; then
    echo ""
    echo "Note: Install 'jq' for better JSON formatting: sudo apt-get install jq"
    echo "Raw response:"
    echo $response
fi
