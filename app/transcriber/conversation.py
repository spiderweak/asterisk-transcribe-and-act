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
from ..renderer.speech import SpeechProcessor
from ..renderer.tts import audio_synthesis

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

    def __init__(self, in_file_path: str, out_file_path: str, transcription_folder_name: str, unique_identifier:str, speech_processing : Optional[SpeechProcessor]):
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

        self.speech_processing = speech_processing
        self.last_timestamp = None

    def process(self):
        self.fold()

        timestamp = self.get_timestamp_of_keyword("chronos", after= self.last_timestamp)
        if timestamp and self.speech_processing:
            # Schedule the upload to happen 60 seconds after detection, passing the timestamp
            self.speech_processing.schedule_event(60, self.handle_upload_and_synthesis)

    def get_timestamp_of_keyword(self, keyword, after = None):
        """Find the next timestamp of the keyword in the transcription file."""
        df_in = pd.read_csv(self.in_file, delimiter=";",  names=['time_start', 'time_end', 'text'])
        df_out = pd.read_csv(self.out_file, delimiter=";", names=['time_start', 'time_end', 'text'])
        df = pd.concat([df_in, df_out])
        if after is not None:
            df_in = df_in[df_in['time_start'] > after]
            df_out = df_out[df_out['time_start'] > after]
            df = pd.concat([df_in, df_out])
        keyword_rows = df[df['text'].str.contains(keyword, case=False, na=False)]
        if not keyword_rows.empty:
            return keyword_rows.iloc[0]['time_start']
        return None

    def handle_upload_and_synthesis(self):
        """Upload the transcription file and handle audio synthesis."""
        try:
            response = upload_to_mission_planner("10.11.0.8", self.transcription_file)
            if response:
                audio_synthesis(response, self.transcription_folder_name, self.unique_identifier)
                return response
            else:
                logging.warning("Upload returned no response or failed.")
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Network request failed: {e}")
        except Exception as e:
            logging.error(f"Error during upload or synthesis: {e}")

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

        output = ""
        # Write to a text file
        with open(self.transcription_file, 'w') as file:
            for line in formatted_lines:
                file.write(line + '\n')
                output += (line + '\n')

        return output


def upload_to_mission_planner(url, filepath):
    api_url = "http://" + url + ":5200/api/Asterisk/upload"
    logging.info(f"Upload file to : {api_url}")
    with open(filepath, "rb") as file:
        files = {"file": (filepath, file)}
        response = requests.post(api_url, files=files)

    if response.status_code == 201:
        logging.debug("File uploaded successfully.")
    else:
        logging.error(f"Error uploading file. Status code: {response.status_code}")
        logging.error(response.text)

