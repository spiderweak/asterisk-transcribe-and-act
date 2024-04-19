import time
from queue import Queue

class SpeechProcessor:
    def __init__(self) -> None:
        self.processing_queue = Queue()
        pass

    def run(self):
        while True:
            event = self.processing_queue.get()
            if event is not None:
                time.sleep(event['delay'])
            event['action']()

    def schedule_event(self, delay, action):
        self.processing_queue.put({'delay': delay, 'action': action})