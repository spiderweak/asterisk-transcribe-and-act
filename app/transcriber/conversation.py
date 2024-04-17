"""
transcriber.py

This module handles the processing and transcription of audio data. It includes the AudioTranscriptionManager class, 
which manages audio blobs, merges them, and transcribes the merged audio using the Whisper model.
"""

import whisper
import logging
import os
import requests

import pandas as pd

from typing import Optional

from ..utils import check_ffmpeg_installed, get_wav_duration, cut_beginning, write_to_file, MissingPackageError

import asyncio

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

    def __init__(self, in_file_path: str, out_file_path: str, transcription_folder_name: str, unique_identifier:str):
        """Initializes the AudioTranscriptionManager with an optional temporary folder and session ID.

        If no temporary folder is provided, a new one is created. The temporary folder is used for storing audio files.
        The session ID, if provided, is used to identify the session associated with this manager.

        Args:
            temp_folder (Optional[tempfile.TemporaryDirectory]): The temporary folder for storing audio files.
        """

        self.in_file = in_file_path # inbound file, Check if path exists
        self.out_file = out_file_path # outbound file, Check if path exists

        self.transcription_folder_name = transcription_folder_name
        self.transcription_file = self.generate_output_file()

        self.unique_identifier = unique_identifier

    def process(self):
        self.fold()
        # Append to MP queue
        try:
            print(asyncio.run(uploadToMissionPlanner("10.11.0.8", self.transcription_file)))
        except Exception:
            pass

    def generate_output_file(self) -> str:
        file_path = os.path.join(self.transcription_folder_name, "transcription.txt")
        return file_path

    def fold(self):
        # Read the CSV files
        df_in = pd.read_csv(self.in_file, delimiter=";",  names=['time_start', 'time_end', 'text'])
        df_out = pd.read_csv(self.out_file, delimiter=";", names=['time_start', 'time_end', 'text'])

        # Add a label to distinguish the speaker
        df_in['speaker'] = 'IN :'
        df_out['speaker'] = 'OUT:'

        # Merge the dataframes
        merged_df = pd.concat([df_in, df_out])

        # Sort by start time
        merged_df.sort_values('time_start', inplace=True)

        # Format the data for output
        formatted_lines = merged_df.apply(lambda x: f"{x['speaker']} {x['text']}", axis=1)

        # Write to a text file
        with open(self.transcription_file, 'w') as file:
            for line in formatted_lines:
                file.write(line + '\n')


async def uploadToMissionPlanner(url, filepath):
    api_url = "http://" + url + ":5200/api/Asterisk/upload"
    logging.info(f"Upload file to : {api_url}")
    with open(filepath, "rb") as file:
        files = {"file": (filepath, file)}
        print(files)
        response = requests.post(api_url, files=files)
        print(response)

    if response.status_code == 201:
        print(response)
        logging.debug("File uploaded successfully.")
    else:
        logging.error(f"Error uploading file. Status code: {response.status_code}")
        logging.error(response.text)

