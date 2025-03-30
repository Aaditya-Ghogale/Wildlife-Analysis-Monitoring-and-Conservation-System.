import requests

url = "http://localhost:8000/detect"

files = {
    "image": open(r"D:\Backend\Myproject\Images--Data set\47.jpeg", "rb"),
    "audio": open(r"D:\Backend\audio_server\balance\gunshot\gunshot_005.wav", "rb")
}

data = {
    "type": "gun",
    "datasource": 2
}

response = requests.post(url, files=files, data=data)
print(response.json())