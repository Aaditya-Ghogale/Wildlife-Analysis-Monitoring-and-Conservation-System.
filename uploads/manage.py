import re
import os
import random
import hashlib
from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
from email_service import send_otp_email, forgot_password_email
from sms_service import send_otp_sms

app = Flask(__name__)

# CORS Headers Setup
allowed_origins = ["https://wild-watch.netlify.app", "http://localhost:3000"]

def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.after_request
def apply_cors(response):
    return add_cors_headers(response)

# Load environment variables
load_dotenv()

# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Temporary storage for OTPs
otp_store = {}

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def is_valid_phone(phone):
    return re.match(r"^\+?[0-9]{10,15}$", phone)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes with OPTIONS handling

@app.route("/register", methods=["OPTIONS", "POST"])
def register():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    print(data)
    email = data.get("email")
    phone_number = data.get("phone")
    username = data.get("username")
    password = data.get("password")
    dept_id = data.get("deptId")
    otp = data.get("otp")

    if not all([email, phone_number, username, password, dept_id]):
        return jsonify({"error": "All fields are required."}), 400

    if not is_valid_email(email) or not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid email or phone number format."}), 400

    # Check if user already exists
    existing_email = supabase.table("users").select("email").eq("email", email).execute().data
    if existing_email:
        return jsonify({"error": "Email already registered."}), 400

    existing_phone = supabase.table("users").select("phone_number").eq("phone_number", phone_number).execute().data
    if existing_phone:
        return jsonify({"error": "Phone number already registered."}), 400

    # Generate and send OTP if not provided
    if not otp:
        generated_otp = str(random.randint(100000, 999999))
        otp_store[email] = generated_otp
        send_otp_email(email, generated_otp)
        send_otp_sms(phone_number, generated_otp)
        return jsonify({"message": "OTP sent successfully.", "otp": generated_otp})       

    # Verify OTP before storing user details
    if otp_store.get(email) != otp:
        return jsonify({"error": "Invalid OTP."}), 400

    del otp_store[email]

    # Store user details
    supabase.table("users").insert({
        "username": username,
        "email": email,
        "phone_number": phone_number,
        "dept_id": dept_id,
        "password": hash_password(password)
    }).execute()

    return jsonify({"message": "User registered successfully."})

@app.route("/login", methods=["OPTIONS", "POST"])
def login():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = supabase.table("users").select("password").eq("email", email).execute()
    if not user.data or user.data[0]["password"] != hash_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    return jsonify({"message": "Login successful."})

@app.route("/forgot-password", methods=["OPTIONS", "POST"])
def forgot_password():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    email = data.get("email")

    user = supabase.table("users").select("email").eq("email", email).execute()
    if not user.data:
        return jsonify({"error": "Email not found."}), 404

    forgot_password_email(email)
    return jsonify({"message": "Password recovery email sent."})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)