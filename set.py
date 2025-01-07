
import os
import shutil

def copy_all_audio_files(source_dir, dest_dir, file_extension=".wav"):
    """
    Copy all audio files from subfolders of source_dir to dest_dir.

    :param source_dir: Path to the directory containing subfolders with audio files.
    :param dest_dir: Path to the directory where all audio files should be copied.
    :param file_extension: The file extension of the audio files to be copied.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for subdir, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(file_extension):
                source_file_path = os.path.join(subdir, file)
                shutil.copy(source_file_path, dest_dir)
                print(f"Copied: {source_file_path} to {dest_dir}")

# Example usage
source_directory = 'C:/Users/aadit/Downloads/archive/input'  # Replace with the path to your source directory
destination_directory = 'C:/Users/aadit/Downloads/archive/gunshot'  # Replace with the path to your destination directory

copy_all_audio_files(source_directory, destination_directory)
