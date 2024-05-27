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

class AsteriskInterop:
    def __init__(self):
        self.model : whisper.Whisper = audio_model
        self.conference_name = None
        self.start = False
        self.stop = False
        self.start_time = None
        self.talkerId_recorded = None
        self.ami = None

    def connection_asterisk(self):
        self.ami = AMIClient(address=HOST, port=PORT, timeout=None)
        self.ami.login(username=USERNAME, secret=PASSWORD)
        self.ami.add_event_listener(on_event=self.on_event)

    def disconnect_asterisk(self):
        if self.ami:
            self.ami.logoff()

    def activate_spy(self, file_name = "input.wav"):
        if self.ami:
            action = SimpleAction(
                'ConfbridgeStartRecord',
                ActionID = 'StartRecording',
                Conference = self.conference_name,
                RecordFile = f"/var/spool/asterisk/monitor/{file_name}",
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
        if self.ami:
            action = SimpleAction(
                'ConfbridgeStopRecord',
                ActionID = 'StopRecording',
                Conference = self.conference_name,
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
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        sound = AudioSegment.silent(duration=4000) + AudioSegment.from_mp3("output.mp3")
        sound = sound.set_frame_rate(8000)
        sound = sound.set_channels(1)
        sound.export("output.gsm", format="gsm", bitrate="13k")
        shutil.copy("output.gsm", "/usr/share/asterisk/sounds/en")

    def speech_to_text(self, file_name = "r_input.wav", prompt = ""):
        response = self.model.transcribe(f"/var/spool/asterisk/monitor/{file_name}", temperature=0.0, language="En", initial_prompt=prompt)
        print(response)
        return response["text"]

    def wait_for_conference(self):
        while self.conference_name == None:
            time.sleep(0.25)
        logging.info("Conference found")
        return True

    def wait_for_start(self):
        while self.start is False:
            time.sleep(0.05)
        logging.info("Start monitor")
        logging.info(self.activate_spy('monitor.wav'))
        self.start = False
        while self.talkerChannel is None:
            time.sleep(0.05)
        return self.talkerChannel

    def wait_for_stop(self):
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
        with open(file_path, 'w') as file:
            file.write(string)

    def on_event(self, source, event):
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
