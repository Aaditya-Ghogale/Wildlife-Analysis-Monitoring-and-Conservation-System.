import os
from dotenv import load_dotenv
from sms_service import send_otp_sms, send_alert_sms

# Load environment variables
load_dotenv()

def test_otp_sms():
    """Test sending an OTP SMS."""
    test_phone = "+918976306036"  # Replace with a valid test number
    otp = 123456
    send_otp_sms(test_phone, otp)

def test_alert_sms():
    """Test sending an alert SMS when a threat is detected."""
    send_alert_sms(1)  # Status = 1 should send an SMS
    send_alert_sms(0)  # Status = 0 should NOT send an SMS

if __name__ == "__main__":
    print("Testing OTP SMS...")
    test_otp_sms()
    print("\nTesting Alert SMS...")
    test_alert_sms()
