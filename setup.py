"""Watchdog entrypoint

Installs the application on the system or in the docker container
"""


import asyncio
import time
import logging
import argparse
from dotenv import load_dotenv


from .app.transcriber.watcher import Watcher
from .app.utils import Config


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


async def main_async():

    options = parse_arguments()
    config = Config(options = options)

    #watch_directory = "/path/to/your/asterisk/monitor/folder"

    watcher = Watcher(config.parsed_yaml["watch_directory"])
    logging.debug(f"Starting to monitor {config.parsed_yaml['watch_directory']} for new and updated files...")

    # Start the watcher
    await watcher.run()


def main():
    """Entry point for running the asynchronous main function."""
    asyncio.run(main_async())

if __name__ == '__main__':
    main()


