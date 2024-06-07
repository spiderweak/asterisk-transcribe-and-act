"""
This module handles speech processing tasks, including scheduling and processing events.
"""

import time
from queue import Queue

class SpeechProcessor:
    """
    Processes speech events using a queue for scheduling.
    """
    def __init__(self):
        """
        Initializes the SpeechProcessor with an empty processing queue.
        """
        self.processing_queue = Queue()
        pass

    def run(self):
        """
        Runs the speech processor, processing events from the queue.
        """
        while True:
            event = self.processing_queue.get()
            if event is not None:
                time.sleep(event['delay'])
                event['action']()

    def schedule_event(self, delay, action):
        """
        Schedules an event to be processed after a specified delay.

        Args:
            delay (int): The delay before processing the event.
            action (callable): The action to perform for the event.
        """
        self.processing_queue.put({'delay': delay, 'action': action})
