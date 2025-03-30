from flask import Flask, request, jsonify
import os
import cv2
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

# Initialize Flask app
app = Flask(__name__)

# Define base directory (current script's directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define relative paths
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'input')
MODEL_PATH = os.path.join(BASE_DIR, 'trained_gun_detector.pth')
SPECIFIC_FOLDER = r"D:\Backend\uploads\gun" # Relative path for specific folder

# Ensure input folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ensure specific folder exists
if not os.path.exists(SPECIFIC_FOLDER):
    os.makedirs(SPECIFIC_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200

# Configuration
NUM_CLASSES = 2
CONFIDENCE_THRESHOLD = 0.5

# Load the trained model
def load_trained_model(model_path, num_classes, device):
    """Load trained gun detection model"""
    model = fasterrcnn_resnet50_fpn(weights=None)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model

# Process a single image
def process_image(image_path, model, device):
    """Process single image and return detection results"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Error: Could not read image"}
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = torch.tensor(img_rgb / 255.0, dtype=torch.float32).permute(2, 0, 1).unsqueeze(0)
        
        with torch.no_grad():
            predictions = model(img_tensor.to(device))[0]

        scores = predictions["scores"].cpu().numpy()
        valid_detections = scores > CONFIDENCE_THRESHOLD
        filtered_scores = scores[valid_detections]

        if len(filtered_scores) > 0:
            max_conf = round(float(filtered_scores.max()), 2)
            return {"Detection": "Gun Detected", "Confidence Score": max_conf}
        else:
            return {"Detection": "No Gun Detected", "Confidence Score": 0.0}
    
    except Exception as e:
        return {"error": str(e)}

# Route to predict on a specific file in the relative folder
@app.route('/predict', methods=['GET'])
def predict_on_specific_file():
    try:
        # Load the model
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = load_trained_model(MODEL_PATH, NUM_CLASSES, device)
        
        # Define the relative path to the specific folder
        if not os.path.exists(SPECIFIC_FOLDER):
            return jsonify({"error": f"Folder does not exist: {SPECIFIC_FOLDER}"})
        
        # Look for a file named "gun" with supported extensions
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        gun_file = None
        
        for ext in supported_extensions:
            potential_file = os.path.join(SPECIFIC_FOLDER, f"gun{ext}")
            if os.path.exists(potential_file):
                gun_file = potential_file
                break
        
        if not gun_file:
            return jsonify({"error": "No file named 'gun' found in the specified folder"})
        
        # Process the specific file
        result = process_image(gun_file, model, device)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)})

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)