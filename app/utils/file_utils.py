"""
This module provides utility functions for file operations in the asterisk-transcribe-and-act project.

Functions:

* generate_folder: Generates a folder based on a unique identifier.
* get_pair_path: Returns the expected path of the paired file.
* write_to_file: Writes data to a specified file in a given folder.
* purge_file: Attempts to delete the specified file.
* upload_to_mission_planner: Uploads a file to the mission planner.
"""

import logging
import os
import tempfile
import requests
import json

from typing import Optional

def generate_folder(unique_identifier: str) -> str:
    """
    Generates a folder based on the given unique identifier.

    Folder name is extracted from the asterisk monitor file name.
    The folder will be temporary and created with a specific name.

    Args:
        unique_identifier (str): The unique identifier for the folder.

    Returns:
        str: The path of the generated folder.
    """
    if not unique_identifier:
        raise ValueError("Unique identifier cannot be empty.")

    base_temp_dir = tempfile.gettempdir()
    conversation_temp_dir = os.path.join(base_temp_dir, "asterisk_transcript", f"{unique_identifier}")

    # Ensure the directory exists
    os.makedirs(conversation_temp_dir, exist_ok=True)

    return conversation_temp_dir

def get_pair_path(file_path: str) -> Optional[str]:
    """
    Given one file of a pair, returns the expected path of its pair.

    Assumes file naming convention of '...-in.wav' and '...-out.wav'.

    Args:
        file_path (str): The path of the file.

    Returns:
        str: The path of the paired file, or None if no pair is found.
    """
    if "-in.wav" in file_path:
        return file_path.replace("-in.wav", "-out.wav")
    elif "-out.wav" in file_path:
        return file_path.replace("-out.wav", "-in.wav")

    if "-in.csv" in file_path:
        return file_path.replace("-in.csv", "-out.csv")
    elif "-out.csv" in file_path:
        return file_path.replace("-out.csv", "-in.csv")

    return None

def write_to_file(folder_name: str, file_name: str, data: list) -> str:
    """
    Writes data to a specified file in a given folder.

    Args:
        folder_name (str): The name of the folder.
        file_name (str): The name of the file.
        data (list): The data to write to the file.

    Returns:
        str: The path of the written file.
    """
    file_path = os.path.join(folder_name, file_name)

    # Open the file and write the data
    with open(file_path, 'w') as file:
        for segment in data:
            line = f"{segment['start']}; {segment['end']}; \"{segment['text']}\"\n"
            file.write(line)

    return file_path

def purge_file(file: str):
    """
    Attempts to delete the specified file.

    Args:
        file (str): The path of the file to be deleted.

    Logs a warning if the file deletion fails.
    """
    try:
        os.remove(file)
    except OSError as e:
        logging.warning(f"Failed to delete file: {e}")

def upload_to_mission_planner(url: str, port: int, file_path: str) -> tuple:
    """
    Uploads a file to the mission planner.

    Args:
        url (str): The URL of the mission planner.
        port (int): The port of the mission planner.
        file_path (str): The path of the file to upload.

    Returns:
        tuple: The status code and response content from the upload request.
    """
    api_url = "http://" + url + ":" + str(port) + "/api/Asterisk/upload"
    logging.info(f"Upload file to : {api_url}")
    with open(file_path, "rb") as file:
        files = {"file": (file_path, file)}
        response = requests.post(api_url, files=files)

    if response.status_code == 201:
        response_json = json.loads(response.text)
        chat_bot_feedback = response_json["chatBotFeedBack"]
        logging.debug(chat_bot_feedback)
        return 201, chat_bot_feedback
    else:
        logging.error(f"Error uploading file. Status code: {response.status_code}")
        logging.error(response.text)
        return response.status_code, "Error uploading file"
