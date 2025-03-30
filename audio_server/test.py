import os
import random
import tempfile
import shutil
import csv
import requests

TEST_AUDIO_FOLDER = r"C:\Users\aadit\Downloads\papap\test"
FLASK_SERVER_URL = "http://127.0.0.1:5000/predict"
CSV_FILE = "gunshot_results.csv"

def get_random_audio_files(folder, count=4):
    audio_files = [f for f in os.listdir(folder) if f.endswith('.wav')]
    
    if len(audio_files) < count:
        raise ValueError(f"Need at least {count} WAV files in the test folder")
    
    return random.sample(audio_files, count)

def save_as_temp_sensors(selected_files, temp_dir):
    sensor_files = []
    for i, filename in enumerate(selected_files, 1):
        dest_path = os.path.join(temp_dir, f"sensor_{i}.wav")
        src_path = os.path.join(TEST_AUDIO_FOLDER, filename)
        shutil.copy(src_path, dest_path)
        sensor_files.append(dest_path)
    return sensor_files

def predict_audio(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(FLASK_SERVER_URL, files={'file': f})
        
        if response.status_code != 200:
            return f"Error: {response.text}"
        
        result = response.json().get('result', -1)
        return "Gunshot detected" if result == 1 else "No gunshot detected"
    
    except Exception as e:
        return f"Prediction Error: {str(e)}"

def update_csv(results):
    try:
        # Remove existing CSV file if it exists
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            
        # Create new CSV file with results
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Sensor", "Result"])
            writer.writerows(results)
        return True
        
    except PermissionError:
        print(f"\nERROR: Please close {CSV_FILE} in other programs and try again")
        return False
    except Exception as e:
        print(f"\nCSV Error: {str(e)}")
        return False

def main():
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            selected_files = get_random_audio_files(TEST_AUDIO_FOLDER)
            sensor_paths = save_as_temp_sensors(selected_files, temp_dir)
            
            results = []
            for i, path in enumerate(sensor_paths, 1):
                result = predict_audio(path)
                results.append((f"Sensor {i}", result))
                print(f"Sensor {i}: {result}")
            
            if update_csv(results):
                print(f"\nNew results saved to {CSV_FILE} (previous file deleted)")
            else:
                print("\nFailed to save results to CSV")

    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == '__main__':
    main()