"""
This module provides the AsteriskInterco class to handle interactions with the Asterisk server. 
It includes methods for connecting and disconnecting from Asterisk, starting and stopping recordings, 
playing audio, converting text to speech, and handling Asterisk events.

Classes:
    AsteriskInterco: A class to manage Asterisk server interactions.

Functions:

* connection_asterisk: Establishes a connection to the Asterisk server.
* disconnect_asterisk: Disconnects from the Asterisk server.
* activate_spy: Activates spying on the conference.
* stop_spy: Stops spying on the conference.
* play_audio: Plays audio in the conference.
* start_record_request: Starts recording on a specified channel.
* stop_recording_request: Stops recording on a specified channel.
* text_to_speech: Converts text to speech and saves it as an audio file.
* speech_to_text: Converts speech to text using the Whisper model.
* wait_for_conference: Waits for a conference to start.
* wait_for_start: Waits for the start of the conference.
* wait_for_stop: Waits for the stop of the conference.
* save_string_to_file: Saves a string to a file.
* on_event: Handles Asterisk events.
"""

import logging
import whisper
import requests
import json
import shutil
import time
import subprocess

from ..utils import AudioModel
from gtts import gTTS
from pydub import AudioSegment
from asterisk.ami import AMIClient, SimpleAction, EventListener


HOST = '127.0.0.1'
PORT = 5038
USERNAME = 'admin'
PASSWORD = 'mysecretpassword'

KEY_WORDS = ["Hello Chronos", "Chronos stop"]
key_words_prompt = "Key words to detect: {}.".format(", ".join(KEY_WORDS))

audio_model = AudioModel().get_model()

class AsteriskInterco:
    """
    A class to handle interactions with the Asterisk server.

    Attributes:
        model (whisper.Whisper): The Whisper model used for transcription.
        conference_name (str): The name of the current conference.
        start (bool): Flag to indicate the start of an event.
        stop (bool): Flag to indicate the stop of an event.
        start_time (float): The start time of an event.
        talkerId_recorded (str): The ID of the recorded talker.
        ami (AMIClient): The AMI client for connecting to Asterisk.
    """

    def __init__(self) -> None:
        """
        Initializes the AsteriskInterco class.
        """
        self.model : whisper.Whisper = audio_model
        self.conference_name = None
        self.start = False
        self.stop = False
        self.start_time = None
        self.talkerId_recorded = None
        self.ami = None

    def connection_asterisk(self):
        """
        Establishes a connection to the Asterisk server.
        """
        self.ami = AMIClient(address=HOST, port=PORT, timeout=None)
        self.ami.login(username=USERNAME, secret=PASSWORD)
        self.ami.add_event_listener(on_event=self.on_event)

    def disconnect_asterisk(self):
        """
        Disconnects from the Asterisk server.
        """
        if self.ami:
            self.ami.logoff()

    def activate_spy(self, file_name="input.wav"):
        """
        Activates spying on the conference.

        Args:
            file_name (str): The name of the file to save the recording.

        Returns:
            dict: The response from the Asterisk server.
        """
        if self.ami:
            action = SimpleAction(
                'ConfbridgeStartRecord',
                ActionID='StartRecording',
                Conference=self.conference_name,
                RecordFile=f"/var/spool/asterisk/monitor/{file_name}",
            )
            future = self.ami.send_action(action)
            try:
                print("Spy started")
                return future.get_response()
            except:
                return "Error"
        else:
            raise ValueError("AMI Client Error")

    def stop_spy(self):
        """
        Stops spying on the conference.

        Returns:
            dict: The response from the Asterisk server.
        """
        if self.ami:
            action = SimpleAction(
                'ConfbridgeStopRecord',
                ActionID='StopRecording',
                Conference=self.conference_name,
            )
            future = self.ami.send_action(action)
            try:
                print("Spy stopped")
                return future.get_response()
            except:
                return "Error"
        else:
            raise ValueError("AMI Client Error")

    def play_audio(self):
        """
        Plays audio in the conference.

        Returns:
            dict: The response from the Asterisk server.
        """
        if self.ami:
            action = SimpleAction(
                'originate',
                Channel='local/playaudio@playback',
                Application='Playback',
                Data='output',
            )
            future = self.ami.send_action(action)
            try:
                return future.get_response()
            except:
                return "Error"
        else:
            raise ValueError("AMI Client Error")

    def start_record_request(self, channel):
        """
        Starts recording on a specified channel.

        Args:
            channel (str): The channel to start recording on.

        Returns:
            dict: The response from the Asterisk server.
        """
        if self.ami:
            logging.info(f"Starting recording of {channel}")
            action = SimpleAction(
                'MixMonitor',
                Channel= channel,
                File='/var/spool/asterisk/monitor/input.wav',
                Options='br(r_input.wav)'
            )
            future = self.ami.send_action(action)
            try:
                self.talkerChannel_recorded = channel
                return future.get_response()
            except:
                return "Error"
        else:
            raise ValueError("AMI Client Error")

    def stop_recording_request(self, channel):
        """
        Stops recording on a specified channel.

        Args:
            channel (str): The channel to stop recording on.

        Returns:
            dict: The response from the Asterisk server.
        """
        if self.ami:
            logging.info(f"Stopping recording of {channel}")
            action = SimpleAction(
                'StopMonitor',
                Channel=channel
            )
            future = self.ami.send_action(action)
            try:
                self.talkerId_recorded = None
                return future.get_response()
            except:
                return "Error"
        else:
            raise ValueError("AMI Client Error")

    def text_to_speech(self, text):
        """
        Converts text to speech and saves it as an audio file.

        Args:
            text (str): The text to convert to speech.
        """
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        sound = AudioSegment.silent(duration=4000) + AudioSegment.from_mp3("output.mp3")
        sound = sound.set_frame_rate(8000)
        sound = sound.set_channels(1)
        sound.export("output.gsm", format="gsm", bitrate="13k")
        shutil.copy("output.gsm", "/usr/share/asterisk/sounds/en")

    def speech_to_text(self, file_name="r_input.wav", prompt=""):
        """
        Converts speech to text using the Whisper model.

        Args:
            file_name (str): The name of the audio file to transcribe.
            prompt (str): The initial prompt for the transcription.

        Returns:
            str: The transcribed text.
        """
        response = self.model.transcribe(f"/var/spool/asterisk/monitor/{file_name}", temperature=0.0, language="En", initial_prompt=prompt)
        print(response)
        return response["text"]

    def wait_for_conference(self):
        """
        Waits for a conference to start.

        Returns:
            bool: True when a conference is found.
        """
        while self.conference_name == None:
            time.sleep(0.25)
        logging.info("Conference found")
        return True

    def wait_for_start(self):
        """
        Waits for the start of the conference.

        Returns:
            str: The channel of the talker.
        """
        while self.start is False:
            time.sleep(0.05)
        logging.info("Start monitor")
        logging.info(self.activate_spy('monitor.wav'))
        self.start = False
        while self.talkerChannel is None:
            time.sleep(0.05)
        return self.talkerChannel

    def wait_for_stop(self):
        """
        Waits for the stop of the conference.

        Returns:
            str: The transcribed text of the conference.
        """
        while self.stop is False:
            time.sleep(0.05)
        logging.info("Stop monitor")
        logging.info(self.stop_spy())
        try:
            logging.info('Transcription of monitor.wav')
            transcrib = self.speech_to_text("monitor.wav", key_words_prompt)
            subprocess.run(["cp", "/var/spool/asterisk/monitor/monitor.wav", "/home/humanitas/Music/monitor.wav"])
            subprocess.run(["rm", "/var/spool/asterisk/monitor/monitor.wav"])
            self.stop = False
            return transcrib
        except Exception as e:
            return e

    def save_string_to_file(self, string, file_path):
        """
        Saves a string to a file.

        Args:
            string (str): The string to save.
            file_path (str): The path to the file.
        """
        with open(file_path, 'w') as file:
            file.write(string)

    def on_event(self, source, event):
        """
        Handles Asterisk events.

        Args:
            source: The source of the event.
            event: The event data.
        """
        if event.name == 'ConfbridgeStart' or event.name == 'ConfbridgeJoin' and self.conference_name == None:
            # React to conference start event
            logging.info("Conference name:", event.keys['Conference'])
            self.conference_name = event.keys['Conference']
        elif event.name == 'ChannelTalkingStart' and self.conference_name is not None:
            logging.debug(event.keys)
            logging.info("Start talk:", event.keys['CallerIDNum'])
            self.talkerChannel = event.keys['Channel']
            self.start = True
            self.stop = False
            while self.start_time is not None:
                time.sleep(0.05)
            self.start_time = time.time()
        elif event.name == 'ChannelTalkingStop' and self.conference_name is not None:
            logging.info("Stop talk", event.keys['Duration'])
            self.stop = True
            self.start_time = None
        else:
            #print("Event:", event.name)
            pass
