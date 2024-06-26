Asterisk Transcribe and Act
===========================

This software aims to design a service that transcribe and act based on keywords from an audio conversation backed by the asterisk VoIP solution.

There is two possibilities for this to work, the first is to mount the monitor folder read only in a docker container, the second is to run the project as is.

This software is provided as is, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

This project does not aim to teach you to deploy you own asterisk server, you will need a working asterisk server with monitoring enable for this project to work, please refer to `Asterisk <https://www.asterisk.org/get-started/>`_ documentation if you need help deploying your own asterisk server.

This project is composed of two parts:

* run.py is an entrypoint for a transcriber that transcribes a conversation between two users (INbound and OUTbound) and sends the transcript to our mission planner based on a keyword detection and after waiting some time (1 minute by default)
* agi_script directly uses the asterisk.ami library to plug onto an audio conference, transcribe and send the request to the mission planner, it does not support parallel audio conferences for now.

Features
--------

Listener on the monitor folder (customizable in the config file) with watchdog

Creates a tmp folder associated with the conversation as long as the file keeps being updated for the past minute.

Archives everything under asterisk folder, content of the folder include a copy of the audio files as well as two separate transcript files. and a unified transcription

Plug the unified transcription on a web interface

Docker container can be plugged in read mode on asterisk monitor folder for process isolation.

Todo
----

* Generate a web page (frontend similar to a chat interface) to review transcriptions
* Parse transcription to support actions
* Document
* Signal processing to support callout and reduce processing needs, and support interruption (Complex task, don't underestimate)

Getting Started
---------------

Prerequisites
^^^^^^^^^^^^^

What things you need to install the software and how to install them:

- python3
- pip
- ffmpeg (for the audio processing (both this project and openai-whisper))
- espeak

Also, for optional dependencies:

- virtualenv
- Docker (optional for containerization)

Running this project
^^^^^^^^^^^^^^^^^^^^

Install the packages from requirements.txt, customize the config.yaml, run with::

    python3 run.py

With Docker, edit config.yaml, if necessary, build with::

    docker build -t asterisk-transcribe-and-act .

run with::

    docker run -v $(ASTERISK_FOLDER):$(ASTERISK_FOLDER_FROM_CONFIG) asterisk-transcribe-and-act:latest

Contributing
------------

This project does not accept exterior contributions for now.

Authors
-------

Antoine `Spiderweak <https://github.com/spiderweak/>`_ BERNARD

David Communier

License
-------

Unless part of the system is incompatible with it, consider this project under CC BY-NC-SA and mostly used for research purposes and teaching.

Acknowledgments
---------------

Thanks to these project, that make most of the project run:


* OpenAI for the Whisper model and for the disclaimer in the opening statement of this README.
