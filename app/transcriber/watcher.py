import time
import os
import pprint
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler

from .transcriber import AudioTranscriptionManager
from ..utils import  generate_folder


class Watcher:
    def __init__(self, watch_directory):
        self.watch_directory = watch_directory
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watch_directory, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.processed_created_pairs = set()
        self.processed_modified_pairs = set()
        self.atm_data = dict()

    def on_created(self, event):
        if event.is_directory:
            return None

        logging.debug(f"Received created event - {event.src_path}.")
        file_path = event.src_path
        pair_path = self.get_pair_path(file_path)

        if pair_path is None or not os.path.exists(pair_path):
            logging.debug(f"Waiting for associated file for {file_path}.")
        else:
            self.process_created_files(file_path, pair_path)
            logging.debug(f"Associated file found, processing pair")

    def get_pair_path(self, file_path: str):
        """
        Given one file of a pair, returns the expected path of its pair.
        Assumes file naming convention of '...-in.wav' and '...-out.wav'.
        """
        if "-in.wav" in file_path:
            return file_path.replace("-in.wav", "-out.wav")
        elif "-out.wav" in file_path:
            return file_path.replace("-out.wav", "-in.wav")
        return None

    def process_created_files(self, file_path, pair_path):
        """
        Process the pair of files for transcription.
        """
        if (file_path, pair_path) in self.processed_created_pairs or (pair_path, file_path) in self.processed_created_pairs:
            # Avoid processing the same pair twice.
            return

        # Ensure to mark this pair as processed to avoid re-processing.
        self.processed_created_pairs.add((file_path, pair_path))

        if "in" in file_path:
            in_path = file_path
            out_path = pair_path
        else:
            in_path = pair_path
            out_path = file_path

        unique_identifier = '-'.join(os.path.basename(file_path).split('-')[:-1])

        folder_name = generate_folder(unique_identifier)
        logging.debug(f"Generating Temporary folder : {folder_name}")

        # Merge files, if necessary.
        logging.debug(f"Merging Audio ?")
        # Run transcription.
        logging.debug(f"Creating associated transcriber object")
        transcription_manager = AudioTranscriptionManager(in_path, out_path, folder_name)

        self.atm_data[unique_identifier] = transcription_manager

        logging.debug(f"Transcribing conversation between {file_path} and {pair_path}.")

        logging.debug(f"Starting conversation renderer watchdog")


    def on_modified(self, event):
        if event.is_directory:
            return None

        logging.debug(f"Received modified event - {event.src_path}.")
        file_path = event.src_path
        pair_path = self.get_pair_path(file_path)

        if pair_path is None or not os.path.exists(pair_path):
            logging.debug(f"Waiting for associated file for {file_path}.")
        else:
            self.process_modified_files(file_path, pair_path)
            logging.debug(f"Associated file found, processing pair")


    def process_modified_files(self, file_path, pair_path):
        """
        Process the pair of files for transcription.
        """
        if (file_path, pair_path) in self.processed_modified_pairs or (pair_path, file_path) in self.processed_modified_pairs:
            # Avoid processing the same pair twice.
            return


        if "in" in file_path:
            in_path = file_path
            out_path = pair_path
        else:
            in_path = pair_path
            out_path = file_path

        # Locks both files
        self.processed_modified_pairs.add((file_path, pair_path))

        unique_identifier = '-'.join(os.path.basename(file_path).split('-')[:-1])

        folder_name = generate_folder(unique_identifier)
        logging.debug(f"Getting Temporary folder name : {folder_name}")

        # Merge files, if necessary.
        logging.debug(f"Merging Audio ?")

        try:
            transcription_manager = self.atm_data[unique_identifier]
        except KeyError:
            transcription_manager = self.atm_data[unique_identifier] = AudioTranscriptionManager(in_path, out_path, folder_name)

        logging.debug(f"Running transcription handler")
        inbound, outbound = transcription_manager.transcribe()
    
        pprint.pprint(inbound)
        pprint.pprint(outbound)

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        else:
            logging.debug(f"No action associated with event {event.event_type}")
            return None
