import re
import os
import random
import hashlib
import csv
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
from email_service import send_otp_email, forgot_password_email, send_alert_email
from sms_service import send_otp_sms, send_alert_sms

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

#yaha pe sare files save honge testinng ke waqt
UPLOAD_BASE = r"D:\Backend\uploads"
PATHS = {
    "animal": os.path.join(UPLOAD_BASE, "animal"),
    "gun": os.path.join(UPLOAD_BASE, "gun"),
    "audio": os.path.join(UPLOAD_BASE, "audio")
}

# CSV Configuration
CSV_PATH = "results.csv"

# Server URLs
SERVERS = {
    "animal": "http://localhost:5000/detect",
    "gun": "http://localhost:9000/predict",
    "gunshot": "http://localhost:1000/predict"
}


# =================================================================
# Helper Functions
# =================================================================

def clear_folder(folder_path):
    """Empty a folder completely"""
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error clearing {file_path}: {e}")

def save_file(file, target_folder, forced_base_name):
    """Save uploaded file with original extension"""
    clear_folder(target_folder)
    
    # Preserve original extension
    original_ext = os.path.splitext(file.filename)[1]
    forced_filename = f"{forced_base_name}{original_ext}"
    
    file_path = os.path.join(target_folder, forced_filename)
    file.save(file_path)
    return file_path

def get_week_of_month():
    """Get zero-indexed week of month (0-3)"""
    today = datetime.today()
    return (today.day - 1) // 7

def save_to_csv(data):
    """Append results to CSV with auto-header creation"""
    # Create CSV if missing
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "datasource", "animal", "gunshot", "week"])
    
    # Prepare data
    csv_data = {
        "date": datetime.now().strftime("%d-%m-%Y"),
        "time": datetime.now().strftime("%H:%M"),
        "datasource": f"datasource{data['datasource']}",
        "animal": data.get("animal", "No"),
        "gunshot": data.get("gunshot", "No"),
        "week": get_week_of_month()
    }
    
    # Append row
    with open(CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_data.values())


# =================================================================
# Detection Endpoint
# =================================================================
@app.route("/upload", methods=["OPTIONS", "POST"])
def unified_detection():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    # Get request data (Changed to form-data handling)
    req_type = request.form.get("type")
    datasource = request.form.get("source")
    image_file = request.files.get("image")
    audio_file = request.files.get("audio")
    
    print(req_type, datasource)
    
    # Validate input
    if req_type not in ["animal", "gun", "both"] or not datasource:
        return jsonify({"error": "Invalid type or missing datasource"}), 400

    # Validate files based on type
    if req_type == "animal" and not image_file:
        return jsonify({"error": "Missing image file"}), 400
    if req_type == "gun" and (not image_file or not audio_file):
        return jsonify({"error": "Missing image or audio file"}), 400
    if req_type == "both" and (not image_file or not audio_file):
        return jsonify({"error": "Missing image or audio file"}), 400

    result = {}
    attempts = 0
    max_attempts = 3

    # Retry loop for file operations
    while attempts < max_attempts:
        try:
            # File Handling with dynamic extensions
            if req_type == "animal":
                save_file(image_file, PATHS["animal"], "animal")
                animal_res = requests.get(SERVERS["animal"]).json()
                result = {
                    "animal": animal_res.get("animal", "No"),
                    "gunshot": "No"
                }

            elif req_type == "gun":
                save_file(image_file, PATHS["gun"], "gun")
                save_file(audio_file, PATHS["audio"], "gunshot")
                
                gun_res = requests.get(SERVERS["gun"]).json()
                gunshot_res = requests.get(SERVERS["gunshot"]).json()
                
                # OR Logic
                gun_detected = gun_res.get("Confidence Score", 0) >= 0.5
                gunshot_detected = gunshot_res.get("result", 0) == 1
                result = {
                    "animal": "No",
                    "gunshot": "Yes" if gun_detected or gunshot_detected else "No"
                }

            elif req_type == "both":
                save_file(image_file, PATHS["animal"], "animal")
                save_file(audio_file, PATHS["audio"], "gunshot")
                
                animal_res = requests.get(SERVERS["animal"]).json()
                gunshot_res = requests.get(SERVERS["gunshot"]).json()
                
                result = {
                    "animal": animal_res.get("animal", "No"),
                    "gunshot": "Yes" if gunshot_res.get("result", 0) == 1 else "No"
                }

            # If we reach here, break retry loop
            break

        except Exception as e:
            attempts += 1
            if attempts == max_attempts:
                return jsonify({"error": f"Detection failed after {max_attempts} attempts: {str(e)}"}), 500
    
     # Prepare final response
    response_data = {
        "date": datetime.now().strftime("%d-%m-%Y"),
        "time": datetime.now().strftime("%H:%M"),
        "datasource": datasource,
        **result,
        "week": get_week_of_month()
    }

     # Save to CSV
    save_to_csv(response_data)

# =============================================================
# New Alert Trigger Logic (BEFORE return)
# =============================================================
    datasource_id = int(response_data['datasource'].replace('datasource', ''))
    animal = response_data.get('animal', 'No')
    status = 1 if response_data.get('gunshot') == 'Yes' else 0

    send_alert_email(datasource_id, animal, status)
    send_alert_sms(datasource_id, animal, status)

    return jsonify(response_data), 200


# =================================================================
# User Handling
# =================================================================

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
    # print()
    user = supabase.table("users").select("password, username").eq("email", email).execute()
    print(user)

    if not user.data or user.data[0]["password"] != hash_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    username = user.data[0]["username"]

    return jsonify({"message": "Login successful.", "username": username })

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
     # Create upload directories if missing
    for path in PATHS.values():
        os.makedirs(path, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=8000)