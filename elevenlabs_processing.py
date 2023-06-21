# elevenlabs_processing
import os
import requests
import time
from pydub import AudioSegment


def split_audio_into_chunks(audio_path, max_chunk_size_mb=9):
    print("Loading audio file...")
    audio = AudioSegment.from_file(audio_path)
    total_size_mb = len(audio) / (1024 * 1024)
    num_chunks = int(total_size_mb / max_chunk_size_mb)
    num_chunks = max(1, num_chunks)  # ensure num_chunks is never less than 1
    print(f"Splitting audio into {num_chunks} chunks...")
    chunk_length_ms = len(audio) // num_chunks
    chunks = make_chunks(audio, chunk_length_ms)
    return chunks[:19]  # return only the first 19 chunks


def make_chunks(audio, chunk_length_ms):
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunks.append(audio[i : i + chunk_length_ms])
    return chunks


def add_voice_to_elevenlabs(audio_chunks, name, XI_API_KEY):
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "accept": "application/json",
        "xi-api-key": XI_API_KEY,
    }
    data = {"name": name}
    files = []
    file_objects = []
    print(f"Creating {len(audio_chunks)} chunks...")
    for i, chunk in enumerate(audio_chunks):
        chunk.export(f"temp_chunk_{i}.mp3", format="mp3")
    print("All chunks created.")
    for i in range(len(audio_chunks)):
        file_object = open(f"temp_chunk_{i}.mp3", "rb")
        files.append(("files", (f"temp_chunk_{i}.mp3", file_object, "audio/mpeg")))
        file_objects.append(file_object)
    voice_id = None
    try:
        print("Sending request to Eleven Labs API...")
        response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code == 200:
            voice_id = response.json()["voice_id"]
            print(f"Voice added successfully. Voice ID: {voice_id}")
        else:
            print(
                f"Failed to add voice. Status code: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        print(f"Error sending request: {e}")
    finally:
        for file_object in file_objects:
            file_object.close()
        for i in range(len(audio_chunks)):
            os.remove(f"temp_chunk_{i}.mp3")
    time.sleep(1)  # delay between requests
    return voice_id


def process_vocal_audio(vocal_audio_path, name, XI_API_KEY):
    print("Starting audio processing...")
    audio_chunks = split_audio_into_chunks(vocal_audio_path)
    vID = add_voice_to_elevenlabs(audio_chunks, name, XI_API_KEY)
    print("Audio processing completed.")
    return vID
