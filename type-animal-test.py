import requests

url = "http://localhost:8000/detect"

# Simulate frontend form-data
files = {
    "image": open(r"D:\Backend\yolov5\yolov5\test_data\00000002_224resized.png", "rb")
}

data = {
    "type": "animal",
    "datasource": 1
}

response = requests.post(url, files=files, data=data)
print(response.json())