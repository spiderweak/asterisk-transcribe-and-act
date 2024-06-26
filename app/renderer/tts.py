"""
This module manages text-to-speech (TTS) conversions using the pyttsx3 library.

Functions:

* convert_text_to_speech: Converts text to speech and saves it as an audio file.
* audio_synthesis: Synthesizes audio from text and sends it to Asterisk.
* send_to_asterisk: Sends the audio file to Asterisk for playback.
"""

import os
import pyttsx3
import uuid
import base64
import time
import logging
import subprocess

from ..utils import get_wav_duration

# Default timeout, 10s
TTS_TIMEOUT = 10

class TextToSpeechConverter:
    """
    Converts text to speech using the pyttsx3 library.
    """
    def __init__(self, tts_timeout: int = TTS_TIMEOUT):
        """
        Initializes the TextToSpeechConverter with a specified timeout.

        Args:
            tts_timeout (int): The timeout for TTS conversion in seconds. Default is 10 seconds.
        """
        self.engine = pyttsx3.init()
        self._tts_timeout = tts_timeout  # Timeout in seconds

    def convert_text_to_speech(self, text: str, folder: str):
        """
        Converts text to speech, saves as an audio file, and returns the content encoded in base64.

        Args:
            text (str): The text to convert to speech.
            folder (str): The folder where the temporary audio file will be saved.

        Returns:
            str: The base64 encoded content of the generated audio file.

        Raises:
            TextToSpeechTimeoutError: If the audio file creation exceeds the timeout.
        """
        file_name = str(uuid.uuid4()) + ".mp3"
        temp_filename = os.path.join(folder, file_name)

        os.makedirs(folder, exist_ok=True)
        self.engine.save_to_file(text, temp_filename)
        self.engine.runAndWait()

        start_time = time.time()

        while not os.path.exists(temp_filename):
            time.sleep(0.2)  # Wait a bit for the file to be created
            if time.time() - start_time > self._tts_timeout:
                logging.error(f"Timeout while waiting for the audio file {temp_filename} to be created.")
                #raise TextToSpeechTimeoutError("Timeout waiting for the audio file to be created.")

        try:
            with open(temp_filename, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
            logging.debug(f"Audio file {temp_filename} successfully converted to base64.")
        finally:
            os.remove(temp_filename)
            logging.debug(f"Temporary audio file {temp_filename} deleted.")

        return temp_filename, base64_audio


def audio_synthesis(sentence, temp_folder_name, conversation_unique_id):
    """
    Synthesizes audio from text and sends it to Asterisk.

    Args:
        sentence (str): The text to synthesize.
        temp_folder_name (str): The folder for temporary files.
        conversation_unique_id (str): The unique identifier for the conversation.
    """
    try:
        tts_interface = TextToSpeechConverter()
        temp_filename, _ = tts_interface.convert_text_to_speech(sentence, temp_folder_name)
        send_to_asterisk(temp_filename, conversation_unique_id)
        del tts_interface
    except NotImplementedError as nie:
        logging.error("Audio synthesis implemented, but audio not sent to asterisk yet")
    except Exception as e:
        logging.error(f"Audio error : {e}")


def send_to_asterisk(filename: str, conversation_unique_id: str):
    """
    Sends the audio file to Asterisk for playback.

    Args:
        filename (str): The path to the audio file.
        conversation_unique_id (str): The unique identifier for the conversation.

    Raises:
        ValueError: If the audio file is too short.
    """
    # check length
    if get_wav_duration(filename) < 5:
        raise ValueError("Answer too short")

    # Design a counter (from listing the files with conversation_unique_id in output folder ?)
    count = 1

    # Need to os.path.join with the correct path with output folder
    output_file = str(conversation_unique_id) + "-" + str(count) + ".gsm"

    subprocess.run(["ffmpeg", "-i", filename, "-ar", "8000", "-ac", "1", "-ab", "13k", "-c:a", "gsm", output_file],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Design the same command to play output_file in the audio conversation
    # subprocess.run(["ffmpeg", "-i", filename, "-ar", "8000", "-ac", "1", "-ab", "13k", "-c:a", "gsm", output_file],
    #               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)