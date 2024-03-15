import yaml
import logging
import os
from typing import Any, Dict, Union

import argparse


class Config:
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_LOG_FILENAME: str = 'log.txt'

    def __init__(self, *, options: argparse.Namespace):
        """Initializes the application configuration with default values or values from a YAML file.

        Args:
            options (argparse.Namespace): parsed command-line options
            env (Environment): simulation environment

        Attributes:
            parsed_yaml (Dict[str, Any]): Contains the parsed configuration YAML file, stored as a dict.
            log_level (int): Integer representation of the parsed log level.
            log_filename (str): Log file name.
        """
        self.set_defaults()

        if hasattr(options, 'config'):
            self.load_yaml(options.config)
        else:
            logging.error("config option not used, using default settings.")

        self.setup_logging()

    def set_defaults(self) -> None:
        """Sets default values for all attributes."""
        self.parsed_yaml: Dict[str, Any] = {}
        self.log_level : int = self.DEFAULT_LOG_LEVEL
        self.log_filename: str = self.DEFAULT_LOG_FILENAME


    def load_yaml(self, config_file_path: str) -> None:
        """Loads settings from a YAML file.

        Args:
            config_file_path (str): Configuration File Path
        """
        try:
            with open(config_file_path, 'r') as config_file:
                self.parsed_yaml = yaml.safe_load(config_file)
        except FileNotFoundError:
            logging.error("Configuration File Not Found, using default settings.")

    def setup_logging(self) -> None:
        """Initializes logging based on parsed YAML."""

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

        # TODO: Maybe rewrite below
        try:
            os.makedirs(self.log_filename, exist_ok=True)
        except FileExistsError:
            pass

        logging.basicConfig(filename=self.log_filename, encoding='utf-8', level=self.log_level)
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
