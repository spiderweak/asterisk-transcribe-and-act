import subprocess
import logging
import wave

def check_ffmpeg_installed():
    """Check if ffmpeg is installed on the system."""
    try:
        # Run 'ffmpeg -version' command and capture its output
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("ffmpeg is not installed or not in PATH.")
        return False
    except FileNotFoundError:
        logging.error("ffmpeg command not found.")
        return False


def get_wav_duration(filename):
    with wave.open(filename, 'r') as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
    return duration


def cut_beginning(input_filename, output_filename, cut_seconds):
    with wave.open(input_filename, 'rb') as infile:
        # Get audio parameters
        n_channels, sampwidth, framerate, n_frames, comptype, compname = infile.getparams()

        # Calculate the number of frames to skip
        start_index = int(cut_seconds * framerate)

        # Set position to the desired start index
        infile.setpos(start_index)

        # Read the remaining frames
        remaining_frames = infile.readframes(n_frames - start_index)

        with wave.open(output_filename, 'wb') as outfile:
            # Set parameters for the output file
            outfile.setparams((n_channels, sampwidth, framerate, 0, comptype, compname))

            # Write the remaining frames to the output file
            outfile.writeframes(remaining_frames)
