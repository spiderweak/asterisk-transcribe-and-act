"""
This module provides utility functions and classes for audio processing, including:

* Singleton pattern implementation for the AudioModel class.
* Checking if `ffmpeg` is installed.
* Getting the duration of a WAV file.
* Cutting the beginning of a WAV file.

Classes:

* AudioModel: A singleton class that loads and provides access to the Whisper audio model.

Functions:

* singleton: A decorator that ensures a class follows the singleton pattern.
* check_ffmpeg_installed: Checks if `ffmpeg` is installed on the system.
* get_wav_duration: Gets the duration of a WAV file.
* cut_beginning: Cuts the beginning of a WAV file.
"""
import subprocess
import logging
import wave
import shutil
import whisper

def singleton(cls):
    """
    A decorator that ensures a class follows the singleton pattern.

    Args:
        cls: The class to be instantiated as a singleton.

    Returns:
        The singleton instance of the class.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class AudioModel:
    """
    A singleton class that loads and provides access to the Whisper audio model.
    """

    def __init__(self):
        """
        Initializes the AudioModel instance and loads the Whisper model.

        Possible models are:
        ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large']
        To update the list, use the following commands in a Python terminal:
        import whisper
        whisper.available_models()
        """
        self.model = whisper.load_model("base")

    def get_model(self):
        """
        Returns the loaded Whisper model.

        Returns:
            The loaded Whisper model.
        """
        return self.model

def check_ffmpeg_installed():
    """
    Check if ffmpeg is installed on the system.

    Returns:
        bool: True if ffmpeg is installed, False otherwise.

    Raises:
        subprocess.CalledProcessError: If the ffmpeg command fails.
        FileNotFoundError: If ffmpeg is not found on the system.
    """
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as cpe:
        logging.error(f"ffmpeg is not installed or not in PATH: {cpe}")
        raise
    except FileNotFoundError as fe:
        logging.error(f"ffmpeg command not found: {fe}")
        raise

def get_wav_duration(filename):
    """
    Get the duration of a WAV file.

    Args:
        filename (str): Path to the WAV file.

    Returns:
        float: Duration of the WAV file in seconds.

    Raises:
        wave.Error: If there is an error reading the WAV file.
    """
    try:
        with wave.open(filename, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        return duration
    except wave.Error:
        raise

def cut_beginning(input_filename, output_filename, cut_seconds):
    """
    Cut the beginning of a WAV file.

    Args:
        input_filename (str): Path to the input WAV file.
        output_filename (str): Path to the output WAV file.
        cut_seconds (int): Number of seconds to cut from the beginning.

    Raises:
        Exception: If an error occurs during file operations.
    """
    if not cut_seconds:
        try:
            shutil.copy(input_filename, output_filename)
            return
        except Exception as e:
            raise e

    with wave.open(input_filename, 'rb') as infile:
        # Get audio parameters
        n_channels, sampwidth, framerate, n_frames, comptype, compname = infile.getparams()

        # Calculate the number of frames to skip
        start_index = int(cut_seconds * framerate)

        # Set position to the desired start index
        infile.setpos(start_index)

        # Read the remaining frames
        remaining_frames = infile.readframes(n_frames - start_index)

        with wave.open(output_filename, 'wb') as outfile:
            # Set parameters for the output file
            outfile.setparams((n_channels, sampwidth, framerate, 0, comptype, compname))

            # Write the remaining frames to the output file
            outfile.writeframes(remaining_frames)
