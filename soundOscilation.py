import soundfile as sf
import numpy as np
import librosa


def print_speech_segment(start_time, end_time):
    # Convert start and end times to minutes and seconds
    start_minutes, start_seconds = divmod(start_time, 60)
    end_minutes, end_seconds = divmod(end_time, 60)

    print(
        f"Speaking detected from {int(start_minutes):02d}:{int(start_seconds):05.2f} to {int(end_minutes):02d}:{int(end_seconds):05.2f}."
    )


# Set the threshold for speech detection
threshold = 0.1

# Set the minimum duration for a speech segment in seconds
min_speech_duration = 1

# Set the chunk size
chunk_size = 1024

# Load the audio file
audio_path = "downloads/videofile4/combined_vocals.wav"
audio, sample_rate = sf.read(audio_path)

# Convert the audio to mono if it has multiple channels
if len(audio.shape) > 1:
    audio = audio.mean(axis=1)

# Calculate the number of chunks based on the chunk size
num_chunks = len(audio) // chunk_size

# Initialize variables for tracking speech segments
is_speech = False
speech_start_time = 0
rms_buffer = []

# Iterate over the audio chunks and detect speech segments
for i in range(num_chunks + 1):
    # Extract the current chunk of audio
    chunk = audio[i * chunk_size : min((i + 1) * chunk_size, len(audio))]

    # Calculate the root mean square (RMS) of the audio chunk
    rms = np.sqrt(np.mean(np.square(chunk)))
    rms_buffer.append(rms)

    # Apply moving average smoothing if we have enough chunks
    if len(rms_buffer) > 10:
        rms = np.mean(rms_buffer[-10:])

    # Check if the RMS exceeds the threshold and start/end speech accordingly
    if rms > threshold:
        if not is_speech:
            is_speech = True
            speech_start_time = i * chunk_size / sample_rate
    else:
        if (
            is_speech
            and (i * chunk_size / sample_rate) - speech_start_time
            >= min_speech_duration
        ):
            is_speech = False
            speech_end_time = i * chunk_size / sample_rate
            print_speech_segment(speech_start_time, speech_end_time)

# Handle case where audio ends during a speech segment
if is_speech:
    speech_end_time = len(audio) / sample_rate
    print_speech_segment(speech_start_time, speech_end_time)
