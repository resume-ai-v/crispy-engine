import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 🔐 Environment config
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

TWILIO_API_URL = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"


def notify_missing_fields(phone_number: str, job_title: str, missing_fields: list) -> dict:
    """
    Sends an SMS alert to user for incomplete job application.

    Args:
        phone_number (str): User phone in +1XXX format
        job_title (str): Job title
        missing_fields (list): List of required fields

    Returns:
        dict: {status: 'sent' or 'error', message}
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE]):
        return {"status": "error", "message": "Twilio config missing in .env"}

    message = (
        f"Hi! We need your input to complete your application for '{job_title}'.\n"
        f"Missing fields: {', '.join(missing_fields)}. Please reply or open the app."
    )

    try:
        response = requests.post(
            TWILIO_API_URL,
            data={
                "From": TWILIO_PHONE,
                "To": phone_number,
                "Body": message
            },
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        )

        if response.status_code == 201 or response.ok:
            return {"status": "sent", "message": f"✅ Message sent to {phone_number}"}
        else:
            return {"status": "error", "message": f"Twilio error: {response.text}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
