import smtplib
import ssl
import os
from email.message import EmailMessage
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Data sources with geolocation and protection zone names
DATA_SOURCES = {
    "S1": {"location": (35.6895, 139.6917), "zone": "Tokyo Wildlife Sanctuary"},
    "S2": {"location": (28.7041, 77.1025), "zone": "Delhi Conservation Area"},
    "S3": {"location": (40.7128, -74.0060), "zone": "New York Protected Zone"},
    "S4": {"location": (-33.8688, 151.2093), "zone": "Sydney Wildlife Reserve"},
}

def get_all_emails():
    """Fetches all user emails from the Supabase database."""
    try:
        response = supabase.table("users").select("email").execute()
        emails = [user["email"] for user in response.data]
        return emails if emails else None
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return None

def send_otp_email(email, otp):
    """Sends an OTP email for verification."""
    subject = "Your One-Time Password (OTP) for WildWatch"
    body = f"""
    Dear User,

    Your One-Time Password (OTP) for accessing Wildlife Monitoring Analysis and Conservation System is: {otp}

    Please use this OTP to proceed with your login. 
    Do not share this OTP with anyone for security reasons.

    Regards,  
    Team WildWatch  
    """
    send_email(email, subject, body)  # BCC happens inside send_email

# def send_alert_email(status):
#     """Sends an alert email when a threat is detected."""
#     if status == 0:
#         return  # No threat detected, no email sent

#     emails = get_all_emails()
#     if not emails:
#         print("No emails found in database. Alert email not sent.")
#         return

#     primary_email = emails[0]  # First email as main recipient
#     cc_emails = emails[1:]  # All other emails as CC

#     timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
#     subject = "⚠ THREAT ALERT: Wildlife Monitoring System ⚠"
#     body = f"""
#     Sent from WildWatch System - ⚠ THREAT ALERT ⚠

#     Type: Threat Detected
#     Description: Human activity detected in a protected area.
#     Time: {timestamp}

#     Please take necessary precautions.

#     Regards,  
#     Team WildWatch  
#     """
    
    # send_email(primary_email, subject, body, cc_emails)


def send_alert_email(datasource_id, animal, status):
    """Sends an alert email when a threat is detected with enhanced details."""
    if status == 0:
        return  # No threat detected, no email sent

    emails = get_all_emails()
    if not emails:
        print("No emails found in database. Alert email not sent.")
        return

    primary_email = emails[0]  # First email as main recipient
    cc_emails = emails[1:]  # All other emails as CC

    # Get data source information
    source_key = f"S{datasource_id}"
    source_info = DATA_SOURCES.get(source_key)
    
    if not source_info:
        print(f"Invalid data source ID: {datasource_id}")
        return

    # Prepare animal display
    animal_display = animal if animal != "No" else "None"

    # Format location coordinates
    lat, long = source_info["location"]
    location_str = f"{lat:.4f}, {long:.4f}"  # Format to 4 decimal places

    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    subject = "⚠ THREAT ALERT: Wildlife Monitoring System ⚠"
    body = f"""
    Sent from WildWatch System - ⚠ THREAT ALERT ⚠

    Type: Threat Detected
    Description: Human activity detected in a protected area.
    Data Source: {source_info['zone']} (Coordinates: {location_str})
    Animal Involved: {animal_display}
    Time: {timestamp}

    Please take necessary precautions.

    Regards,  
    Team WildWatch  
    """
    
    send_email(primary_email, subject, body, cc_emails)



def send_email(receiver_email, subject, body, cc_emails=None):
    """Handles sending emails using SMTP with CC and BCC to sender for tracking."""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        if cc_emails:
            msg["Cc"] = ", ".join(cc_emails)
        msg["Bcc"] = SENDER_EMAIL  # BCC: Admin gets a hidden copy

        # Secure connection with Gmail SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully to {receiver_email} (CC: {cc_emails if cc_emails else 'None'}, BCC: {SENDER_EMAIL})")
    except Exception as e:
        print(f"Error sending email: {e}")

def forgot_password_email(email):
    """Handles forgot password requests by retrieving user details and sending an email."""
    try:
        response = supabase.table("users").select("username", "password", "phone_number", "email").eq("email", email).execute()
        if not response.data:
            print("No user found with this email.")
            return

        user = response.data[0]
        subject = "Your Account Details - WildWatch"
        body = f"""
        Dear {user['username']},

        You requested to recover your account details.

        📧 Email: {user['email']}
        📱 Phone: {user['phone_number']}
        🔑 Password: {user['password']}

        Note: Please keep this information secure.

        Regards,  
        Team WildWatch  
        """
        send_email(email, subject, body)
        print("Password recovery email sent successfully.")
    except Exception as e:
        print(f"Error retrieving user details: {e}")


# Example Usage
if __name__ == "__main__":
    # send_otp_email("crazzygunn2429@example.com", 123456)  # Test OTP email
    # send_alert_email(1)  # Send alert email
