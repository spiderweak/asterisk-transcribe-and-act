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

class ConversationTranscriptionManager:
    """Manages the transcribed audio data.

    This class handles audio blobs, stores them in a queue, and uses the Whisper model for transcription. 
    It also manages a temporary folder for storing audio files and keeps track of the session ID.

    Attributes:
        in_transcription (str): The current transcription text for input side of the conversation.
        out_transcription (str): The current transcription text for output side of the conversation.
        transcription_folder_name (str): The name/path of the temporary transcriptions folder.
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
