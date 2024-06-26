"""
This module provides classes to watch a directory for changes and process files as they are created or modified.
It uses the watchdog library to monitor the file system events and handle them accordingly.

Classes:
    Watcher: Watches a directory for file changes and processes them.
    EventHandler: Handles file system events and processes files based on the event type.

Functions:

* __init__: Initializes the Watcher and EventHandler classes.
* run: Starts the watchdog observer to monitor the directory.
* on_created: Handles the event when a file is created.
* on_modified: Handles the event when a file is modified.
* process_files: Processes files based on their type and path.
"""

import time
import os
import logging

from typing import Optional, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from .transcriber import DualAudioTranscriptionManager
from .conversation import ConversationTranscriptionManager
from ..utils import generate_folder, get_pair_path

class Watcher:
    """
    Watches a directory for file changes and processes them.

    Attributes:
        watch_directory (str): The directory to watch for file changes.
        processing_queue (Queue): The queue to process files.
        file_type (str): The type of files to watch for (e.g., 'wav', 'csv').
        speech_processing (Optional[SpeechProcessor]): Optional speech processing component.
        observer (Observer): The watchdog observer to monitor the directory.
    """

    def __init__(self, watch_directory: str, processing_queue, file_type: str, speech_processing = None):
        """
        Initializes the Watcher class with the directory to watch, the processing queue, the file type, and optional speech processing.

        Args:
            watch_directory (str): The directory to watch for file changes.
            processing_queue (Queue): The queue to process files.
            file_type (str): The type of files to watch for (e.g., 'wav', 'csv').
            speech_processing (Optional[SpeechProcessor]): Optional speech processing component.
        """
        self.watch_directory = watch_directory
        self.processing_queue = processing_queue
        self.file_type = file_type
        self.speech_processing = speech_processing
        self.observer = Observer()

    def run(self):
        """
        Starts the watchdog observer to monitor the directory.
        """
        event_handler = EventHandler(self.processing_queue, self.file_type, self.speech_processing)
        self.observer.schedule(event_handler, self.watch_directory, recursive=True)
        try:
            self.observer.start()
        except FileNotFoundError as fnfe:
            print(f"{fnfe}, creating folder {self.watch_directory}")
            os.makedirs(self.watch_directory)
            self.observer.start()

        logging.info("Watcher Running")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class EventHandler(FileSystemEventHandler):
    """
    Handles file system events and processes files based on the event type.

    Attributes:
        data (dict): A dictionary to store file data.
        processing_queue (Queue): The queue to process files.
        file_type (str): The type of files to watch for (e.g., 'wav', 'csv').
        speech_processing (Optional[SpeechProcessor]): Optional speech processing component.
    """

    def __init__(self, processing_queue, file_type: str, speech_processing = None):
        """
        Initializes the EventHandler with the processing queue, the file type, and optional speech processing.

        Args:
            processing_queue (Queue): The queue to process files.
            file_type (str): The type of files to watch for (e.g., 'wav', 'csv').
            speech_processing (Optional[SpeechProcessor]): Optional speech processing component.
        """
        self.data = dict()
        self.processing_queue = processing_queue
        self.file_type = file_type
        self.speech_processing = speech_processing

    def on_created(self, event):
        """
        Handles the event when a file is created.

        Args:
            event : The file system event.
        """
        if event.is_directory or not event.src_path.endswith(f'.{self.file_type}'):
            return

        logging.debug(f"Received created event - {event.src_path}.")
        file_path = event.src_path
        pair_path = get_pair_path(file_path)

        if pair_path and os.path.exists(pair_path):
            self.process_files(file_path, pair_path)

    def on_modified(self, event):
        """
        Handles the event when a file is modified.

        Args:
            event: The file system event.
        """
        if event.is_directory or not event.src_path.endswith(f'.{self.file_type}'):
            return

        logging.debug(f"Received modified event - {event.src_path}.")
        file_path = event.src_path
        pair_path = get_pair_path(file_path)

        if pair_path and os.path.exists(pair_path):
            transcription_manager = self.process_files(file_path, pair_path)

            if transcription_manager is None or transcription_manager in self.processing_queue:
                logging.debug("No action for this event, action already done or currently processing")
                return
            else:
                logging.debug("Appending transcription request to queue")
                self.processing_queue.append(transcription_manager)

    def process_files(self, file_path: str, pair_path: str) -> Optional[Union[DualAudioTranscriptionManager, ConversationTranscriptionManager]]:
        """
        Processes files based on their type and path.

        Args:
            file_path (str): The path to the file to process.
            pair_path (str): The path to the paired file.

        Returns:
            Optional[Union[DualAudioTranscriptionManager, ConversationTranscriptionManager]]: The transcription manager for the files, if any.
        """
        # Determine in_path and out_path based on file naming
        in_path, out_path = (file_path, pair_path) if "in" in file_path else (pair_path, file_path)

        # Extract unique identifier from the file name (assuming a certain naming convention)
        unique_identifier = '-'.join(os.path.basename(file_path).split('-')[:-1])

        # Generate or retrieve the temporary folder for this conversation
        folder_name = generate_folder(unique_identifier)
        logging.debug(f"Temporary folder for conversation: {folder_name}")

        if self.file_type == "wav":
            # Initialize or retrieve the DualAudioTranscriptionManager for this conversation
            if unique_identifier not in self.data:
                self.data[unique_identifier] = DualAudioTranscriptionManager(in_path, out_path, folder_name, unique_identifier)
            audio_transcription_manager = self.data[unique_identifier]
            return audio_transcription_manager

        if self.file_type == "csv":
            # Initialize or retrieve the DualAudioTranscriptionManager for this conversation
            if unique_identifier not in self.data:
                self.data[unique_identifier] = ConversationTranscriptionManager(in_path, out_path, folder_name, unique_identifier, self.speech_processing)
            conversation_transcription_manager = self.data[unique_identifier]
            return conversation_transcription_manager
