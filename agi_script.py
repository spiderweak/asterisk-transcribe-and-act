import sys
import logging

import speech_recognition as sr 
import azure.cognitiveservices.speech as speechsdk

from .app.utils import upload_to_mission_planner
from .app.transcriber.asterisk_interco import AsteriskInterop

IP_MISSIONPLANER = '10.11.0.8'
PORT_MISSIONPLANER = 5200

KEY_WORDS = ["Hello Chronos", "Chronos stop"]
key_words_prompt = "Key words to detect: {}.".format(", ".join(KEY_WORDS))

def main():
    asterisk = AsteriskInterop()
    asterisk.connection_asterisk()
    #print(asterisk.start_chanspy())
    asterisk.wait_for_conference()
    while True:
        try:
            channel = asterisk.wait_for_start()
            logging.debug(f"User is talking on {channel}")
            response = asterisk.wait_for_stop()
            if 'Hello Chronos' in response:
                asterisk.text_to_speech(f"I'm ready to hear your request")
                asterisk.play_audio()
                logging.debug(asterisk.start_record_request(channel))
            if 'Chronos stop' in response:
                logging.debug(asterisk.stop_recording_request(channel))
                asterisk.text_to_speech(f"I heard your request and answer you in a few seconde")
                logging.debug('Transcription of input.wav')
                question = asterisk.speech_to_text(prompt=key_words_prompt)
                if question is not None:
                    for keyword in KEY_WORDS:
                        question = question.replace(keyword, "")
                    asterisk.save_string_to_file(question, "question.txt")
                    response = upload_to_mission_planner(url=IP_MISSIONPLANER, port=PORT_MISSIONPLANER,  filepath="question.txt")
                    asterisk.text_to_speech(response)
                    asterisk.play_audio()
        except KeyboardInterrupt:
            break
    asterisk.disconnect_asterisk()
    sys.exit(0)

if __name__ == "__main__":
    main()