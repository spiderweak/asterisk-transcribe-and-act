import time
import os
import pprint
import logging
import threading

from typing import Optional

from watchfiles import awatch, Change

from .transcriber import AudioTranscriptionManager
from ..utils import  generate_folder, get_pair_path


class Watcher:
    def __init__(self, watch_directory):
        self.watch_directory = watch_directory

    async def run(self):
        handler = Handler()
        logging.debug(f"Starting to monitor {self.watch_directory} for new and updated files...")
        async for changes in awatch(self.watch_directory):
            for change_type, src_path in changes:
                await handler.handle_event(src_path, change_type)

    async def process_event(self, src_path, change_type):
        # Implement the logic to handle the change. This is a placeholder for your actual logic.
        # Note: This method should now be asynchronous.
        logging.debug(f"Processing {change_type.name} event for {src_path}.")
        # Example: You might want to initiate asynchronous transcription here.

class Handler:
    def __init__(self):
        self.processed_created_pairs = set()
        self.processed_modified_pairs = set()
        self.atm_data = dict()

    async def handle_event(self, src_path, change_type):
        """Asynchronously handle file change events."""
        if not src_path.endswith('.wav'):
            return

        logging.debug(f"Processing {change_type.name} event for {src_path}.")
        pair_path = get_pair_path(src_path)  # Adapted to be an async or sync utility function.

        if pair_path and os.path.exists(pair_path):
            await self.process_files(src_path, pair_path, change_type)


    def on_modified(self, src_path, change_type):
        """Asynchronously handle file change events."""
        if not src_path.endswith('.wav'):
            return

        logging.debug(f"Processing {change_type.name} event for {src_path}.")
        pair_path = get_pair_path(src_path)  # Adapted to be an async or sync utility function.

        if pair_path and os.path.exists(pair_path):
            transcription_manager  = await self.process_files(file_path, pair_path, event.event_type)

            if transcription_manager is None:
                # Pair was already processed recently
                logging.debug(f"No action for this event, action already done or currently processing")
                return
            logging.debug(f"Running transcription handler")

            # Create and start a new thread for the transcription process
            inbound, outbound = transcription_manager.transcribe()
        
            pprint.pprint(inbound)
            pprint.pprint(outbound)

            self.processed_modified_pairs.discard((file_path, pair_path))
            self.processed_modified_pairs.discard((pair_path, file_path))



    async def process_files(self, file_path, pair_path, event_type) -> Optional[AudioTranscriptionManager]:

        # Check if this pair has already been processed to avoid duplication
        processed_pairs = self.processed_created_pairs if event_type == 'created' else self.processed_modified_pairs

        if (file_path, pair_path) in processed_pairs or (pair_path, file_path) in processed_pairs:
            return  # This pair has already been processed

        processed_pairs.add((file_path, pair_path))  # Mark this pair as processed

        # Determine in_path and out_path based on file naming
        in_path, out_path = (file_path, pair_path) if "in" in file_path else (pair_path, file_path)

        # Extract unique identifier from the file name (assuming a certain naming convention)
        unique_identifier = '-'.join(os.path.basename(file_path).split('-')[:-1])

        # Generate or retrieve the temporary folder for this conversation
        folder_name = generate_folder(unique_identifier)
        logging.debug(f"Temporary folder for conversation: {folder_name}")

        # Initialize or retrieve the AudioTranscriptionManager for this conversation
        if unique_identifier not in self.atm_data:
            self.atm_data[unique_identifier] = AudioTranscriptionManager(in_path, out_path, folder_name)

        transcription_manager = self.atm_data[unique_identifier]

        return transcription_manager
