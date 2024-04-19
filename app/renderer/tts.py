
import os
import pyttsx3
import uuid
import base64
import time
import logging
import subprocess

# Default timeout, 10s
TTS_TIMEOUT = 10

class TextToSpeechConverter:
    def __init__(self, tts_timeout : int = TTS_TIMEOUT):
        self.engine = pyttsx3.init()
        self._tts_timeout = tts_timeout # Timeout in seconds

    def convert_text_to_speech(self, text: str, folder: str):
        """
        Convert text to speech, save as an audio file, and return the content encoded in base64.

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
                raise TextToSpeechTimeoutError("Timeout waiting for the audio file to be created.")

        try:
            with open(temp_filename, 'rb') as audio_file:
                audio_data = audio_file.read()
                base64_audio = base64.b64encode(audio_data).decode('utf-8')
            logging.debug(f"Audio file {temp_filename} successfully converted to base64.")
        finally:
            os.remove(temp_filename)
            logging.debug(f"Temporary audio file {temp_filename} deleted.")

        return base64_audio


def audio_synthesis(sentence, temp_folder_name, conversation_unique_id):
    try:
        tts_interface = TextToSpeechConverter()
        base64_audio = tts_interface.convert_text_to_speech(sentence, temp_folder_name)
        send_to_asterisk(base64_audio, conversation_unique_id)
        del tts_interface
    except NotImplementedError as nie:
        logging.error("Audio synthesis implemented, but audio not sent to asterisk yet")
    except Exception as e:
        logging.error(f"Audio error : {e}")

def send_to_asterisk(base64_data : str, conversation_unique_id):
    """
        base64_data is a base64 encoded string that contains the audio data
        Will need an updated way to send the data to asterisk
        The following line is a baseline that runs a linux command
        Will need to modify it to play the audio file
        Maybe from a file written on disk, but in that case the base64_data needs to be written to a file first.
    """
    raise NotImplementedError("Missing the command to send the data to asterisk")
    subprocess.run("?", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
