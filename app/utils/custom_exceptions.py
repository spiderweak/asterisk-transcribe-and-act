"""
This module defines custom exceptions for the asterisk-transcribe-and-act project.

Classes:

* MissingPackageError: Exception raised when a required package is missing.
"""

class MissingPackageError(Exception):
    """
    Exception raised when a required package is missing.

    Currently, this exception is only checked for ffmpeg.

    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="Required package is missing."):
        self.message = message
        super().__init__(self.message)
