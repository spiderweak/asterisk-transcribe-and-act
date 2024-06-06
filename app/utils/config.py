"""
This module provides the Config class for loading and managing the application's configuration settings from a YAML file or default values. It also sets up logging based on the loaded configuration.

Classes:

* Config: Handles loading, parsing, and applying configuration settings from a YAML file.

Functions:

* set_defaults: Sets default values for all attributes.
* load_yaml: Loads settings from a YAML file.
* setup_logging: Initializes logging based on parsed YAML.
* _set_attribute_from_yaml: Helper function to set attribute from parsed YAML.
"""

import yaml
import logging
import os
from typing import Any, Dict, Union
import argparse

class Config:
    """
    Config class to handle application configuration settings.

    Attributes:
        DEFAULT_LOG_LEVEL (int): Default log level.
        DEFAULT_LOG_FILENAME (str): Default log filename.
        parsed_yaml (Dict[str, Any]): Parsed YAML configuration data.
        log_level (int): Log level.
        log_filename (str): Log filename.
    """
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_FILENAME: str = 'log.txt'

    def __init__(self, *, options: argparse.Namespace):
        """
        Initializes the application configuration with default values or values from a YAML file.

        Args:
            options (argparse.Namespace): Parsed command-line options.
        """
        self.set_defaults()

        if hasattr(options, 'config'):
            self.load_yaml(options.config)
        else:
            logging.error("config option not used, using default settings.")

        self.setup_logging()

    def set_defaults(self) -> None:
        """
        Sets default values for all attributes.
        """
        self.parsed_yaml: Dict[str, Any] = {}
        self.log_level: int = self.DEFAULT_LOG_LEVEL
        self.log_filename: str = self.DEFAULT_LOG_FILENAME

    def load_yaml(self, config_file_path: str) -> None:
        """
        Loads settings from a YAML file.

        Args:
            config_file_path (str): Path to the configuration file.
        """
        try:
            with open(config_file_path, 'r') as config_file:
                self.parsed_yaml = yaml.safe_load(config_file)
        except FileNotFoundError:
            logging.error("Configuration File Not Found, using default settings.")

    def setup_logging(self) -> None:
        """
        Initializes logging based on parsed YAML configuration.
        """
        try:
            match self.parsed_yaml.get('loglevel', 'info'):
                case 'error':
                    self.log_level = logging.ERROR
                case 'warning':
                    self.log_level = logging.WARNING
                case 'info':
                    self.log_level = logging.INFO
                case 'debug':
                    self.log_level = logging.DEBUG
                case _:
                    self.log_level = logging.INFO
        except (KeyError, TypeError):
            self.log_level = logging.INFO

        self.log_filename = self.parsed_yaml.get('logfile', 'log.txt')

        try:
            os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
        except FileNotFoundError:
            pass

        logging.basicConfig(
            filename=self.log_filename,
            encoding='utf-8',
            level=self.log_level
        )
        logging.getLogger('whisper').setLevel(logging.INFO)
        logging.getLogger('numba').setLevel(logging.INFO)
        logging.getLogger('watchdog').setLevel(logging.INFO)
        logging.info('\n')

    def _set_attribute_from_yaml(self, attr_name: str, yaml_path: list, value_type: type) -> None:
        """
        Helper function to set attribute from parsed YAML.

        Args:
            attr_name (str): The name of the attribute to set.
            yaml_path (list): The list of keys to navigate the YAML dictionary.
            value_type (type): The type to cast the value to (e.g., int, float, str).
        """
        try:
            value = self.parsed_yaml
            for key in yaml_path:
                value = value[key]
            setattr(self, attr_name, value_type(value))
        except (KeyError, TypeError) as e:
            logging.error(f"Config Error, Default simulation value {getattr(self, attr_name)} used for entry {e}")
