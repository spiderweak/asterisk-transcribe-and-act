import logging
import time

from collections import deque
from threading import Thread


class EventQueue(deque):
    def __init__(self) -> None:
        super().__init__()
        self.processing_thread = Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()


    def _process_queue_item(self, item):
        """Process a single item from the queue.

        This method should be overridden with custom processing logic.

        Args:
            item: The item to process.
        """
        # Placeholder processing logic; override this method
        print(f"Processing item: {item}")

        logging.debug(f"Running transcription handler")
        item.transcribe()

    def _process_queue(self):
        """Continuously process items from the queue."""
        i = 0
        while True:
            if self:
                time.sleep(5)
                print(f"Processed {i} items for now")
                item = self.popleft()  # Wait for an item to be available
                print(f"Processing item {i+1}")
                try:
                    self._process_queue_item(item)
                finally:
                    # Signal that processing is complete
                    i+=1






