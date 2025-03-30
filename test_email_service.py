import os
from dotenv import load_dotenv
from email_service import send_otp_email, send_alert_email
from email_service import forgot_password_email

# Load environment variables
load_dotenv()

# def test_otp_email():
#     """Test sending an OTP email."""
#     test_email = "crazzygunn2429@example.com"  # Replace with your test email
#     otp = 123456
#     send_otp_email(test_email, otp)

# def test_alert_email():
#     """Test sending an alert email when a threat is detected."""
#     send_alert_email(1)  # Status = 1 should send an email
#     send_alert_email(0)  # Status = 0 should NOT send an email

# def test_forget():
#     forgot_password_email("aadityaghogale01@gmail.com")  # Test forgot password email


# if __name__ == "__main__":
#     print("Testing OTP email...")
#     test_otp_email()
#     print("\nTesting Alert email...")
#     test_alert_email()
#     print("\nTesting Forgot Password...")
#     test_forget()


def test_alert_emails():
    """Test email formatting and delivery"""
    test_cases = [
        (1, "lion", "Should show RED 'LION' for Tokyo"),
        (2, "no", "Should show GREEN 'NONE' for Delhi"),
        (3, "tiger", "Should show RED 'TIGER' for New York"),
        (4, "no", "Should show GREEN 'NONE' for Sydney"),
    ]

    print("📧 Testing Alert Emails (Standalone)")
    print("=" * 50)
    
    for ds_id, animal, desc in test_cases:
        print(f"\nCase {ds_id}: {desc}")
        print(f"Data Source: S{ds_id} - {DATA_SOURCES[f'S{ds_id}']['zone']}")
        print(f"Animal Input: '{animal}'")
        
        # Call the actual email function
        send_alert_email(ds_id, animal)
        print("✅ Email sent")

if __name__ == "__main__":
    
    
    test_alert_emails()