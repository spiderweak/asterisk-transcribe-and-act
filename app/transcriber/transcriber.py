"""
transcriber.py

This module handles the processing and transcription of audio data. It includes the AudioTranscriptionManager class, 
which manages audio blobs, merges them, and transcribes the merged audio using the Whisper model.
"""

import whisper
import logging
import os

from typing import Optional

from ..utils import check_ffmpeg_installed, get_wav_duration, cut_beginning, write_to_file, MissingPackageError

# Load Whisper model globally.
audio_model = whisper.load_model("base")

class AudioTranscriptionManager:
    """Manages the transcription of audio data for a session.

    This class handles audio blobs, stores them in a queue, and uses the Whisper model for transcription. 
    It also manages a temporary folder for storing audio files and keeps track of the session ID.

    Attributes:
        in_transcription (str): The current transcription text for input side of the conversation.
        out_transcription (str): The current transcription text for output side of the conversation.
        model (whisper.Whisper): The Whisper model used for transcription.
        _transcription_folder (tempfile.TemporaryDirectory): The temporary folder for transcriptions.
        transcription_folder_name (str): The name/path of the temporary transcriptions folder.
        ffmpeg_installed (bool): ffmpeg_installation_status
    """

    def __init__(self, in_file_path: str, out_file_path: str, transcription_folder_name: str):
        """Initializes the AudioTranscriptionManager with an optional temporary folder and session ID.

        If no temporary folder is provided, a new one is created. The temporary folder is used for storing audio files.
        The session ID, if provided, is used to identify the session associated with this manager.

        Args:
            temp_folder (Optional[tempfile.TemporaryDirectory]): The temporary folder for storing audio files.
        """

        self.in_file = in_file_path # Check if path exists
        self.out_file = out_file_path # Check if path exists

        self.transcription_folder_name = transcription_folder_name

        self.temp_in_file = os.path.join(self.transcription_folder_name, os.path.basename(self.in_file))
        self.temp_out_file = os.path.join(self.transcription_folder_name, os.path.basename(self.out_file))

        self.in_transcription = dict()
        self.out_transcription = dict()

        self.in_timer = 0.0
        self.out_timer = 0.0

        self.model : whisper.Whisper = audio_model

        self.ffmpeg_installed = check_ffmpeg_installed()

    def transcribe(self):
        """Transcribes the given audio file using the Whisper model.

        Raises:
            Exception: Propagates any exceptions that occur during transcription.
        """

        logging.info(f"Copying file to folder and removing times")
        cut_beginning(self.in_file, self.temp_in_file, self.in_timer)
        cut_beginning(self.out_file, self.temp_out_file, self.out_timer)

        try:
            print(f"Inbound file length is : {get_wav_duration(self.temp_in_file)}")
            in_result = self.model.transcribe(self.temp_in_file, word_timestamps=True)
            self.in_transcription = in_result
        except Exception as e:
            logging.error(f"Error during inbound transcription: {e}")
            raise

        try:
            print(f"Outbound file length is : {get_wav_duration(self.temp_out_file)}")
            out_result = self.model.transcribe(self.temp_out_file, word_timestamps=True)
            self.out_transcription = out_result#['text'])
        except Exception as e:
            logging.error(f"Error during inbound transcription: {e}")
            raise

        logging.debug("Transcription completed successfully.")

        try:
            write_to_file(self.transcription_folder_name, 'transcription-in.csv', self.in_transcription['segments'])
        except KeyError:
            logging.error('Inbound Transcription error')
            print('Inbound Transcription error')
            pass

        try:
            write_to_file(self.transcription_folder_name, 'transcription-out.csv', self.out_transcription['segments'])
        except KeyError:
            logging.error('Outbound Transcription error')
            print('Outbound Transcription error')
            pass
        

        logging.debug("Updating times values")

        return (self.in_transcription, self.out_transcription)


DEFAULT_TIMEOUT = 8 # in seconds
