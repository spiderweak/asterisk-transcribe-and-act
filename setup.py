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

    processing_queue = EventQueue()

    #watch_directory = "/path/to/your/asterisk/monitor/folder"
    watcher = Watcher(config.parsed_yaml["watch_directory"], processing_queue)

    # Start the file watcher in a separate thread

    logging.debug(f"Starting to monitor {config.parsed_yaml['watch_directory']} for new and updated files...")

    watcher_thread = Thread(target=watcher.run, daemon=True)
    watcher_thread.start()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()
