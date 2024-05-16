import logging
import os
import tempfile
import requests
import json

def generate_folder(unique_identifier: str) -> str:
    """Generates a folder based on given folder name
    Folder name is extracted from the asterisk monitor file name
    Folder will be temporary and created with specific name
    """
    if not unique_identifier:
        raise ValueError("Unique identifier cannot be empty.")

    base_temp_dir = tempfile.gettempdir()
    conversation_temp_dir = os.path.join(base_temp_dir, "asterisk_transcript",f"{unique_identifier}")

    # Ensure the directory exists
    os.makedirs(conversation_temp_dir, exist_ok=True)

    return conversation_temp_dir

def get_pair_path(file_path: str):
        """
        Given one file of a pair, returns the expected path of its pair.
        Assumes file naming convention of '...-in.wav' and '...-out.wav'.
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

def write_to_file(folder_name, file_name, data) -> str:
    file_path = os.path.join(folder_name, file_name)

    # Open the file and write the data
    with open(file_path, 'w') as file:
        for segment in data:
            line = f"{segment['start']}; {segment['end']}; \"{segment['text']}\"\n"
            file.write(line)

    return file_path

def purge_file(file: str):
    """Attempts to delete the specified file.

    Args:
        file (str): The path of the file to be deleted.

    Logs a warning if the file deletion fails.
    """

    try:
        os.remove(file)
    except OSError as e:
        logging.warning(f"Failed to delete file: {e}")


def upload_to_mission_planner(url, port, filepath):
    api_url = "http://" + url + ":"+ str(port) + "/api/Asterisk/upload"
    logging.info(f"Upload file to : {api_url}")
    with open(filepath, "rb") as file:
        files = {"file": (filepath, file)}
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
