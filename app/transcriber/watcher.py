import time
import os
import logging

from typing import Optional, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from .transcriber import AudioTranscriptionManager
from .conversation import ConversationTranscriptionManager
from ..utils import  generate_folder, get_pair_path


class Watcher:
    def __init__(self, watch_directory, processing_queue, file_type, speech_processing = None):
        self.watch_directory = watch_directory
        self.processing_queue = processing_queue
        self.file_type = file_type
        self.observer = Observer()
        self.speech_processing = speech_processing

    def run(self):
        event_handler = EventHandler(self.processing_queue, self.file_type, self.speech_processing)
        self.observer.schedule(event_handler, self.watch_directory, recursive=True)
        try:
            self.observer.start()
        except FileNotFoundError as fnfe:
            print(f"{fnfe}, creating folder {self.watch_directory}")
            os.makedirs(self.watch_directory)
            self.observer.start

        logging.info("Watcher Running")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class EventHandler(FileSystemEventHandler):
    def __init__(self, processing_queue, file_type, speech_processing = None):
        self.data = dict()
        self.processing_queue = processing_queue
        self.file_type = file_type
        self.speech_processing = speech_processing

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(f'.{self.file_type}'):
            return

        logging.debug(f"Received created event - {event.src_path}.")
        file_path = event.src_path
        pair_path = get_pair_path(file_path)

        if pair_path and os.path.exists(pair_path):
            self.process_files(file_path, pair_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(f'.{self.file_type}'):
            return

        logging.debug(f"Received modified event - {event.src_path}.")
        file_path = event.src_path
        pair_path = get_pair_path(file_path)

        if pair_path and os.path.exists(pair_path):
            transcription_manager  = self.process_files(file_path, pair_path)

            if transcription_manager is None or transcription_manager in self.processing_queue:
                # Pair was already processed recently
                logging.debug("No action for this event, action already done or currently processing")
                return
            else:
                logging.debug("Appending transcription request to queue")
                self.processing_queue.append(transcription_manager)


    def process_files(self, file_path, pair_path) -> Optional[Union[AudioTranscriptionManager,ConversationTranscriptionManager]]:
        # Determine in_path and out_path based on file naming
        in_path, out_path = (file_path, pair_path) if "in" in file_path else (pair_path, file_path)

        # Extract unique identifier from the file name (assuming a certain naming convention)
        unique_identifier = '-'.join(os.path.basename(file_path).split('-')[:-1])

        # Generate or retrieve the temporary folder for this conversation
        folder_name = generate_folder(unique_identifier)
        logging.debug(f"Temporary folder for conversation: {folder_name}")

        if self.file_type == "wav":
            # Initialize or retrieve the AudioTranscriptionManager for this conversation
            if unique_identifier not in self.data:
                self.data[unique_identifier] = AudioTranscriptionManager(in_path, out_path, folder_name, unique_identifier)
            audio_transcription_manager = self.data[unique_identifier]
            return audio_transcription_manager
        if self.file_type == "csv":
            # Initialize or retrieve the AudioTranscriptionManager for this conversation
            if unique_identifier not in self.data:
                self.data[unique_identifier] = ConversationTranscriptionManager(in_path, out_path, folder_name, unique_identifier, self.speech_processing)
            conversation_transcription_manager = self.data[unique_identifier]
            return conversation_transcription_manager
