import os
from datetime import datetime
from supabase import create_client, Client
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Twilio client
twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Data sources with geolocation and protection zone names
DATA_SOURCES = {
    "S1": {"location": (35.6895, 139.6917), "zone": "Tokyo Wildlife Sanctuary"},
    "S2": {"location": (28.7041, 77.1025), "zone": "Delhi Conservation Area"},
    "S3": {"location": (40.7128, -74.0060), "zone": "New York Protected Zone"},
    "S4": {"location": (-33.8688, 151.2093), "zone": "Sydney Wildlife Reserve"},
}

def get_all_phone_numbers():
    """Fetches all user phone numbers from the Supabase database."""
    try:
        response = supabase.table("users").select("phone_number").execute()
        phone_numbers = [user["phone_number"] for user in response.data]
        return phone_numbers if phone_numbers else None
    except Exception as e:
        print(f"Error fetching phone numbers: {e}")
        return None

def send_otp_sms(phone_number, otp):
    """Sends an OTP SMS for verification."""
    message_body = f"Your WildWatch OTP: {otp}. Do not share this with anyone."
    send_sms(phone_number, message_body)

# def send_alert_sms(status):
#     """Sends an alert SMS when a threat is detected."""
#     if status == 0:
#         return  # No threat detected, no SMS sent

#     phone_numbers = get_all_phone_numbers()
#     if not phone_numbers:
#         print("No phone numbers found in database. Alert SMS not sent.")
#         return

#     timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    
#     for sensor_id, details in DATA_SOURCES.items():
#         location = details["location"]
#         zone = details["zone"]
        
#         message_body = (
#     f"⚠ ALERT! Suspicious activity detected.\n"
#     f"Zone: {zone}\n"
#     f"📍 {location[0]}, {location[1]}\n"
#     f"⏰ {timestamp}\n"
#     f"Take action! - WildWatch"
#         )


#         for phone in phone_numbers:
#             send_sms(phone, message_body)


def send_alert_sms(datasource_id, animal, status):
    """Sends an alert SMS with detailed threat information."""
    if status == 0:
        return  # No threat detected, no SMS sent

    # Validate and get data source
    source_key = f"S{datasource_id}"
    source_info = DATA_SOURCES.get(source_key)
    
    if not source_info:
        print(f"Invalid data source ID: {datasource_id}")
        return

    phone_numbers = get_all_phone_numbers()
    if not phone_numbers:
        print("No phone numbers found in database. Alert SMS not sent.")
        return

    # Prepare message components
    animal_display = animal if animal != "No" else "None"
    lat, long = source_info["location"]
    location_str = f"{lat:.4f}, {long:.4f}"
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    # Construct message body
    message_body = (
        f"⚠ ALERT! Suspicious activity detected.\n"
        f"Zone: {source_info['zone']}\n"
        f"📍 Coordinates: {location_str}\n"
        f"🐾 Animal: {animal_display}\n"
        f"⏰ {timestamp}\n"
        f"Take action! - WildWatch"
    )

    # Send SMS to all recipients
    for phone in phone_numbers:
        send_sms(phone, message_body)

# Example usage:
# send_alert_sms(3, "Elephant", 1)  # Valid animal
# send_alert_sms(4, "No", 1)        # No animal involved

def send_sms(phone_number, message_body):
    """Handles sending SMS using Twilio."""
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number} (SID: {message.sid})")
    except Exception as e:
        print(f"Error sending SMS to {phone_number}: {e}")

# Example Usage (Will be tested separately)
# send_otp_sms("+1234567890", random.randint(100000, 999999))  # Test OTP SMS
# send_alert_sms(1)  # Send alert SMS
