"""
This module provides the EventQueue class to handle asynchronous processing of queued items.
It continuously processes items from the queue using a separate thread.

Classes:
    EventQueue: A class to manage and process a queue of items.

Functions:
    __init__: Initializes the EventQueue and starts the processing thread.
    _process_queue_item: Processes a single item from the queue (override with custom logic).
    _process_queue: Continuously processes items from the queue.
"""

import logging
import time
import wave

from collections import deque
from threading import Thread

MAX_RETRIES = 5

class EventQueue(deque):
    """
    A class to manage and process a queue of items.

    This class extends deque and continuously processes items from the queue using a separate thread.

    Attributes:
        processing_thread (Thread): The thread that processes the queue.
    """

    def __init__(self) -> None:
        """
        Initializes the EventQueue and starts the processing thread.
        """
        super().__init__()
        self.processing_thread = Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

    def _process_queue_item(self, item):
        """
        Process a single item from the queue.

        This method should be overridden with custom processing logic.

        Args:
            item: The item to process.
        """
        # Placeholder processing logic; override this method
        logging.debug(f"Processing item: {item}")
        item.process()

    def _process_queue(self):
        """
        Continuously processes items from the queue.
        """
        i = 0
        while True:
            if self:
                time.sleep(1)
                print(f"Processed {i} items for now")
                item = self.popleft()  # Wait for an item to be available
                print(f"Processing item {i+1}")

                if isinstance(item, tuple):
                    item, retries = item
                else:
                    retries = 0

                try:
                    self._process_queue_item(item)
                except wave.Error:
                    if retries < MAX_RETRIES:
                        self.append((item, retries+1))
                    else:
                        raise
                finally:
                    # Signal that processing is complete
                    i += 1

