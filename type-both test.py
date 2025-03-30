import requests

url = "http://localhost:8000/detect"

files = {
    "image": open(r"D:\Backend\yolov5\yolov5\test_data\00000002_224resized.png", "rb"),
    "audio": open(r"D:\Backend\audio_server\balance\gunshot\gunshot_005.wav", "rb")
}

data = {
    "type": "both",
    "datasource": 3
}

response = requests.post(url, files=files, data=data)
print(response.json())