"""Watchdog entrypoint

Installs the application on the system or in the docker container
"""

import time
import logging
import argparse

from threading import Thread
from dotenv import load_dotenv

from app.transcriber.watcher import Watcher
from app.transcriber.queuehandler import EventQueue
from app.utils import Config


def load_environment_variables():
    """Load environment variables from the .env file."""

    load_dotenv()

    logging.debug("Environment variables loaded")


def parse_arguments():
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description='Run the Flask application with Socket.IO support.')
    parser.add_argument('--log-level', type=str, default='INFO', help='Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-file', type=str, default='log.txt', help='Set the log file location')
    parser.add_argument('--config', type=str, default='config.yaml', help='Config file')

    return parser.parse_args()


def main():
    """Run the Flask application with Socket.IO support."""

    options = parse_arguments()
    config = Config(options = options)

    audio_processing_queue = EventQueue()
    conversation_processing_queue = EventQueue()

    #watch_directory = "/path/to/your/asterisk/monitor/folder"
    text_watcher = Watcher(config.parsed_yaml["text_watch_directory"], conversation_processing_queue, "csv")
    audio_watcher = Watcher(config.parsed_yaml["audio_watch_directory"], audio_processing_queue, "wav")

    # Start the file watcher in a separate thread

    logging.debug("Starting to monitor folders for new and updated files...")

    audio_watcher_thread = Thread(target=audio_watcher.run, daemon=True)
    audio_watcher_thread.start()

    text_watcher_thread = Thread(target=text_watcher.run, daemon=True)
    text_watcher_thread.start()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
