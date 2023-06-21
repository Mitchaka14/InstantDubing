# ./InstantDubing/vocal_separation.py
import os
import sys
import shutil
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from spleeter.separator import Separator


def merge_chunks(vocal_audio_path, chunk_prefix="chunk"):
    vocals = AudioSegment.empty()
    accompaniments = AudioSegment.empty()

    chunk_index = 0
    while True:
        vocal_path = f"{vocal_audio_path}/{chunk_prefix}_{chunk_index}/chunk/vocals.wav"
        accompaniment_path = (
            f"{vocal_audio_path}/{chunk_prefix}_{chunk_index}/chunk/accompaniment.wav"
        )

        print(f"Checking for files: '{vocal_path}' and '{accompaniment_path}'")

        if not os.path.isfile(vocal_path) or not os.path.isfile(accompaniment_path):
            break

        # Load chunk as AudioSegment and append to existing vocals and accompaniments
        vocals += AudioSegment.from_wav(vocal_path)
        accompaniments += AudioSegment.from_wav(accompaniment_path)

        chunk_index += 1

    # Export combined vocals and accompaniments
    if not vocals.duration_seconds == 0:
        vocals.export(f"{vocal_audio_path}/combined_vocals.wav", format="wav")
    else:
        print("No vocals files found.")

    if not accompaniments.duration_seconds == 0:
        accompaniments.export(
            f"{vocal_audio_path}/combined_accompaniments.wav", format="wav"
        )
    else:
        print("No accompaniments files found.")

    # Ask user if they want to delete chunks
    delete_chunks = "y"
    # Delete chunks if user answered 'y'
    if delete_chunks == "y":
        chunk_index = 0
        while True:
            # Construct chunk directory path
            chunk_dir = f"{vocal_audio_path}/{chunk_prefix}_{chunk_index}"

            print(f"Checking for directory: '{chunk_dir}'")

            # Check if chunk directory exists
            if not os.path.isdir(chunk_dir):
                break  # No more chunks

            # Remove chunk directory
            shutil.rmtree(chunk_dir)

            # Go to next chunk
            chunk_index += 1


def separate_vocals(input_audio_path, vocal_audio_path):
    separator = Separator("spleeter:2stems")

    # Load audio file
    audio = AudioSegment.from_file(input_audio_path)

    # Duration of audio file in milliseconds
    duration = len(audio)

    # Duration of each chunk
    chunk_duration = (
        5 * 60 * 1000
    )  # 5 minutes * 60 seconds/minute * 1000 milliseconds/second

    # Process each chunk
    for i in range(0, duration, chunk_duration):
        # Create chunk
        chunk = audio[i : i + chunk_duration]

        # Save chunk to temporary file
        chunk_filename = "chunk.wav"
        chunk.export(chunk_filename, format="wav")

        # Use separator
        separator.separate_to_file(
            chunk_filename, f"{vocal_audio_path}/chunk_{i//chunk_duration}"
        )

        # Delete temporary file
        os.remove(chunk_filename)

    # Merge chunks and handle chunk deletion
    merge_chunks(vocal_audio_path)


def get_audio_start_time(reference_audio_path, audio_path):
    audio = AudioSegment.from_wav(audio_path)
    reference_audio = AudioSegment.from_wav(reference_audio_path)
    # Get the array representation of the audio files
    audio_array = np.array(audio.get_array_of_samples())
    reference_audio_array = np.array(reference_audio.get_array_of_samples())
    # Find the start time of the audio by comparing the audio array to the reference audio array
    audio_start_index = np.argmax(audio_array != reference_audio_array)
    audio_start_time = audio_start_index / audio.frame_rate
    return audio_start_time, len(audio)
