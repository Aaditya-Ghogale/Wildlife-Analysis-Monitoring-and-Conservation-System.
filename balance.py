import os
import numpy as np
import librosa
import soundfile as sf
import shutil
import random

def process_audio_files(input_dir, output_dir, target_duration=2, sr=22050):
    """
    Process audio files to ensure they all have the same length.
    
    :param input_dir: Directory containing the input audio files.
    :param output_dir: Directory to save the processed audio files.
    :param target_duration: Target duration for each audio file in seconds.
    :param sr: Sampling rate for audio files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.wav'):
                file_path = os.path.join(root, file)
                y, _ = librosa.load(file_path, sr=sr)
                
                # Adjust the length of the audio file
                if len(y) > target_duration * sr:
                    y = y[:target_duration * sr]
                else:
                    y = np.pad(y, (0, max(0, target_duration * sr - len(y))), 'constant')
                
                output_file_path = os.path.join(output_dir, file)
                sf.write(output_file_path, y, sr)

def balance_dataset(gunshot_dir, other_sounds_dir, balanced_dir, sr=22050):
    """
    Balance the dataset by creating an equal number of samples from both classes.
    
    :param gunshot_dir: Directory containing processed gunshot audio files.
    :param other_sounds_dir: Directory containing processed other sounds audio files.
    :param balanced_dir: Directory to save the balanced dataset.
    """
    if not os.path.exists(balanced_dir):
        os.makedirs(balanced_dir)

    gunshot_files = [f for f in os.listdir(gunshot_dir) if f.endswith('.wav')]
    other_files = [f for f in os.listdir(other_sounds_dir) if f.endswith('.wav')]

    min_samples = min(len(gunshot_files), len(other_files))

    random.shuffle(gunshot_files)
    random.shuffle(other_files)

    for i in range(min_samples):
        shutil.copy(os.path.join(gunshot_dir, gunshot_files[i]), os.path.join(balanced_dir, f'gunshot_{i+1:03d}.wav'))
        shutil.copy(os.path.join(other_sounds_dir, other_files[i]), os.path.join(balanced_dir, f'no_gunshot_{i+1:03d}.wav'))

# Main script to process and balance the dataset
gunshot_dir = input("Enter the path to the gunshot sounds directory: ")
other_sounds_dir = input("Enter the path to the other sounds directory: ")
processed_gunshot_dir = 'processed_gunshot_sounds'
processed_other_sounds_dir = 'processed_other_sounds'
balanced_dir = 'balanced_dataset'

process_audio_files(gunshot_dir, processed_gunshot_dir, target_duration=2)
process_audio_files(other_sounds_dir, processed_other_sounds_dir, target_duration=2)
balance_dataset(processed_gunshot_dir, processed_other_sounds_dir, balanced_dir)

print(f"Balanced dataset created in: {balanced_dir}")
