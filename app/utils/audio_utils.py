import subprocess
import logging
import wave
import shutil
import whisper

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class AudioModel:
    def __init__(self):
        self.model = whisper.load_model("base")

        # Possible models are :
        # ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large']
        # In case of updated list, list should be available with the following commands in a python terminal
        # import whisper
        # whisper.avaiable_models()

    def get_model(self):
        return self.model


def check_ffmpeg_installed():
    """Check if ffmpeg is installed on the system."""
    try:
        # Run 'ffmpeg -version' command and capture its output
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as cpe:
        logging.error(f"ffmpeg is not installed or not in PATH : {cpe}")
        raise
    except FileNotFoundError as fe:
        logging.error(f"ffmpeg command not found.  : {fe}")
        raise


def get_wav_duration(filename):
    try:
        with wave.open(filename, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        return duration
    except wave.Error:
        raise


def cut_beginning(input_filename, output_filename, cut_seconds):

    if not cut_seconds:
        try:
            shutil.copy(input_filename, output_filename)
            return
        except:
            raise

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
