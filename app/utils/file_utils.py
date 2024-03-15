import logging
import os
import tempfile

def generate_folder(unique_identifier: str) -> str:
    """Generates a folder based on given folder name
    Folder name is extracted from the asterisk monitor file name
    Folder will be temporary and created with specific name
    """
    if not unique_identifier:
        raise ValueError("Unique identifier cannot be empty.")

    base_temp_dir = tempfile.gettempdir()
    conversation_temp_dir = os.path.join(base_temp_dir, f"asterisk_conversations_{unique_identifier}")

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
    return None

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
