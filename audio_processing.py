# ./audio_processing.py
import requests
import os
from pydub import AudioSegment

chunk_length_ms = 10 * 60 * 1000

response_format = "srt"


def make_chunks(audio):
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunks.append(audio[i : i + chunk_length_ms])
    return chunks


def split_audio(audio_path, token):
    print(f"Reading audio file: {audio_path}")
    audio = AudioSegment.from_file(audio_path)
    print("Creating audio chunks")
    chunks = make_chunks(audio)
    print(f"Created {len(chunks)} chunks")
    return chunks


def process_audio(audio_path, action, token):
    print(f"Processing audio file: {audio_path}")
    url = f"https://api.openai.com/v1/audio/{action}s"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "model": "whisper-1",
        "response_format": response_format,
    }
    with open(audio_path, "rb") as audio_file:
        files = {"file": audio_file}
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response: {response.text}")

    if response_format in ["json", "verbose_json"]:
        return response.json().get("data")
    else:
        return response.text


def process_audio_chunks(action, audio_chunks, token):
    results = []
    total_time = 0
    for i, chunk in enumerate(audio_chunks):
        print(f"Processing chunk {i+1}/{len(audio_chunks)}")
        chunk.export(f"temp/temp_chunk_{i}.mp3", format="mp3")
        result = process_audio(f"temp/temp_chunk_{i}.mp3", action, token)
        print(f"Finished processing chunk {i+1}/{len(audio_chunks)}")
        # Adjust the time in the result
        if response_format == "srt":
            result = adjust_srt_time(result, total_time)
        results.append(result)
        total_time += len(chunk) / 1000  # Add the length of the chunk in seconds
        os.remove(f"temp/temp_chunk_{i}.mp3")
    return results


def adjust_srt_time(srt_text, time_offset):
    print(f"Adjusting SRT time with offset: {time_offset} seconds")
    lines = srt_text.split("\n")
    for i in range(len(lines)):
        if "-->" in lines[i]:
            start_time, end_time = lines[i].split(" --> ")
            start_time = add_time(start_time, time_offset)
            end_time = add_time(end_time, time_offset)
            lines[i] = f"{start_time} --> {end_time}"
    return "\n".join(lines)


def add_time(time_str, time_offset):
    hours, minutes, rest = time_str.split(":")
    seconds, milliseconds = rest.split(",")
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + time_offset
    new_hours = total_seconds // 3600
    total_seconds %= 3600
    new_minutes = total_seconds // 60
    total_seconds %= 60
    new_seconds = total_seconds
    return f"{int(new_hours):02}:{int(new_minutes):02}:{int(new_seconds):02},{milliseconds}"
