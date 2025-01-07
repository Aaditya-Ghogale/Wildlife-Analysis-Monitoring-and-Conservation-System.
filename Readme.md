
This will be updated as the project progresses...

---
Wildlife  Analysis Monitoring and Conservation System   

A centralized system designed to detect Animals and potential poachers in the jungle using data from various sources and identify animals and gunshots using image and sound-based gunshot detection.

---

## Table of Contents
- [Introduction](#introduction)  
- [Features](#features)  
- [Technologies Used](#technologies-used)  
- [Project Structure](#project-structure)  
- [Installation](#installation)  

---

## Introduction  
The Wildlife  Analysis Monitoring and Conservation System is a machine learning-based project aimed at safeguarding wildlife.It is made with the aim of Identifying Animals in Wildlife Setups. We also aim to identify potential poachers by detecting the sound of gunshots.  

The project is currently trained to classify audio data to distinguish gunshots from other sounds and detect their presence in real-time.

---

## Features 
- Data Source- As this is not a IOT project we will not be using sensors for real time Audio but we will use readily available data for testing. 
- Audio Classification: Uses a dataset to classify gunshot and non-gunshot sounds.  
- Camera Monitoring: Centralized system for Wildlife surveillance.  
- Gunshot Detection Model: Real-time detection of gunshot events.  
- Data Preprocessing: Proper dataset balancing for gunshot and non-gunshot sounds.

---

## Technologies Used  
- Python  
- Jupyter Notebook  
- Machine Learning Libraries: TensorFlow, Keras, scikit-learn, NumPy, pandas  
- Audio Processing Libraries: Librosa, PyDub , Tenserflow , Keras.

---
## Installation  

1. Clone the repository:  

git clone https://github.com/your-username/wildlife-hunter-detection.git  
cd wildlife-hunter-detection  
  

2. Install the required dependencies:  
  
pip install -r requirements.txt  
  

3. Set up your data:  
- Place the gunshot and non-gunshot audio files in the `data/` folder.  
- Update the label CSV files with appropriate paths.  

4. Run the project:  
  
python main.py  
  
---
