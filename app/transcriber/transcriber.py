"""
transcriber.py

This module handles the processing and transcription of audio data. It includes the AudioTranscriptionManager class, 
which manages audio blobs, merges them, and transcribes the merged audio using the Whisper model.
"""

import whisper
import logging
import os

from typing import Optional

from ..utils import check_ffmpeg_installed, MissingPackageError

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

    def __init__(self, in_file_path: str, out_file_path: str, unique_identifier: Optional[str] = None, transcription_folder_name: Optional[str] = None):
        """Initializes the AudioTranscriptionManager with an optional temporary folder and session ID.

        If no temporary folder is provided, a new one is created. The temporary folder is used for storing audio files.
        The session ID, if provided, is used to identify the session associated with this manager.

        Args:
            temp_folder (Optional[tempfile.TemporaryDirectory]): The temporary folder for storing audio files.
        """

        if unique_identifier is None:
            if ('-'.join(os.path.basename(in_file_path).split('-')[:-1])) == ('-'.join(os.path.basename(out_file_path).split('-')[:-1])):
                self.unique_identifier = '-'.join(os.path.basename(in_file_path).split('-')[:-1])
            else:
                raise ValueError("Please use a custime unique identifier if you cross-transcribe two different files")
        else:
            self.unique_identifier = unique_identifier

        self.in_file = in_file_path # Check if path exists
        self.out_file = out_file_path # Check if path exists

        self.transcription_folder_name = transcription_folder_name

        self.in_transcription = ""
        self.out_transcription = ""

        self.model : whisper.Whisper = audio_model

        self.ffmpeg_installed = check_ffmpeg_installed()

    def transcribe(self):
        """Transcribes the given audio file using the Whisper model.

        Raises:
            Exception: Propagates any exceptions that occur during transcription.
        """
        try:
            in_result = self.model.transcribe(self.in_file, word_timestamps=True)
            out_result = self.model.transcribe(self.out_file, word_timestamps=True)

            self.in_transcription = in_result
            self.out_transcription = out_result#['text'])
            logging.debug("Transcription completed successfully.")
            return (self.in_transcription, self.out_transcription)
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            raise



DEFAULT_TIMEOUT = 8 # in seconds

def process_transcription(transcription_manager: AudioTranscriptionManager, timeout = DEFAULT_TIMEOUT):
    """Process the transcription of an audio file.

    Args:
        transcription_manager (AudioTranscriptionManager): The manager handling audio transcriptions.
        timeout (int): Transcription timeout in seconds.

    Raises:
        Exception: Propagates exceptions that occur during processing.
        TimeoutError: If the thread processing the transcription exceeds the allowed time.
    """

    if not transcription_manager.ffmpeg_installed:
        logging.warning("ffmpeg package is not installed on the system, the transcription will be unavailable")
        raise MissingPackageError("ffmpeg not installed on system")

    try:
        transcription_manager.transcribe()
        logging.debug(f"In Transcription : {transcription_manager.in_transcription}")
        logging.debug(f"Out Transcription : {transcription_manager.out_transcription}")
    except Exception as ex:
        logging.error(f"Error processing transcription: {ex}")
        raise
