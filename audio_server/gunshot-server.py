from flask import Flask, request, jsonify
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # Disable oneDNN optimizations
import tensorflow as tf
import librosa
import numpy as np
import pandas as pd

app = Flask(__name__)

# A function to set CORS headers
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "./epoch/final_model.keras")
model = tf.keras.models.load_model(MODEL_PATH)

# Audio preprocessing function
def preprocess_audio(file_path, target_sample_rate=22050, n_mfcc=13, fixed_time_steps=87):
    audio, sr = librosa.load(file_path, sr=target_sample_rate)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc).T
    if mfccs.shape[0] < fixed_time_steps:
        pad_width = ((0, fixed_time_steps - mfccs.shape[0]), (0, 0))
        mfccs = np.pad(mfccs, pad_width, mode='constant')
    else:
        mfccs = mfccs[:fixed_time_steps, :]
    return np.expand_dims(mfccs, axis=0)

@app.route('/predict', methods=['GET'])
def predict():
    # Specify the audio folder and file name
    audio_folder = r"D:\Backend\uploads\audio"
    file_path = os.path.join(audio_folder, "gunshot.wav")
    
    if not os.path.exists(file_path):
        return jsonify({"error": "No file named 'gunshot.wav' found in uploads/audio"}), 400

    try:
        input_data = preprocess_audio(file_path)
        prediction = model.predict(input_data)
        result = int(prediction[0] > 0.5)
        return add_cors_headers(jsonify({"result": result}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=1000)
