# Asterisk Transcribe and Act

This software aims to design a service that transcribe and act based on keywords from an audio conversation backed by the asterisk VoIP solution.

There is two possibilities for this to work, the first is to mount the monitor folder read only in a docker container, the second is to install the service.

This software is provided as is, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

## Features

Listener on the monitor folder (customizable in the config file) with watchdog

Creates a tmp folder associated with the conversation as long as the file keeps being updated for the past minute.

Archives everything under asterisk folder, content of the folder include a copy of the audio files as well as two separate transcript and a unified transcription

Plug the unified transcription on a web interface

Docker container can be plugged in read mode on asterisk monitor folder for process isolation.

# Todo

- Plug on monitor interface
- Transcribe
- Parse transcription


Improve transcriptions.
 - Unified file with signal processing to work with interruptions


Also:
- Fix unsafe Wekzeug usage for production

## Getting Started

### Prerequisites

What things you need to install the software and how to install them:

- python3
- pip

Also, for optional dependencies:

- virtualenv
- ffmpeg (for the audio processing (both this project and openai-whisper))
- Docker (optional for containerization)

And for the audio outputs (dependencies from pyttsx3, see [Synthesizer support](https://pyttsx3.readthedocs.io/en/latest/support.html)):

- sapi5 (Windows)
- nsss (Mac OS)
- espeak (Linux)

## Contributing

This project does not accept exterior contributions for now.

## Authors

Antoine ["Spiderweak"](https://github.com/spiderweak) BERNARD

## License

Unless part of the system is incompatible with it, consider this project under CC BY-NC-SA and mostly used for research purposes and teaching.

## Acknowledgments

Thanks to these project, that make most of the project run
- OpenAI for the Whisper model and for the disclaimer in the opening statement of this README.
- Flask
