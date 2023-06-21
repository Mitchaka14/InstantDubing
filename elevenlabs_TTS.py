# elevenlabs_TTS
import os
import shutil
import requests
import time
from pydub import AudioSegment, silence
from io import BytesIO


def text_to_speech(text, voice_id, xi_api_key):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": xi_api_key,
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
        },
    }
    response = requests.post(url, json=data, headers=headers)
    return response.content


def convert_time_to_seconds(time_str):
    h, m, s = time_str.split(":")
    s, ms = s.split(",")
    return int(h) * 3600 + int(m) * 60 + float(f"{s}.{ms}")


def process_transcription_file(file_path, voice_id, output_dir, xi_api_key):
    if not os.path.exists(f"{output_dir}/temp_audio_segments"):
        os.makedirs(f"{output_dir}/temp_audio_segments")
    with open(file_path, "r") as file:
        lines = file.readlines()
        i = 0
        final_audio = AudioSegment.empty()
        while i < len(lines):
            if lines[i].strip() == "":
                i += 1
                continue
            if "-->" in lines[i + 1]:
                start_time, end_time = map(
                    convert_time_to_seconds, lines[i + 1].strip().split(" --> ")
                )
            else:
                print(f"Skipping line {i+1}: {lines[i+1]}")
                i += 1
                continue
            text = lines[i + 2].strip()
            while i + 3 < len(lines) and lines[i + 3].strip() != "":
                i += 1
                text += " " + lines[i + 2].strip()
            while (
                i + 4 < len(lines)
                and lines[i + 4].strip() != ""
                and "-->" in lines[i + 4]
                and end_time
                == convert_time_to_seconds(lines[i + 4].strip().split(" --> ")[0])
            ):
                i += 3
                if "-->" in lines[i + 1]:
                    end_time = convert_time_to_seconds(
                        lines[i + 1].strip().split(" --> ")[1]
                    )
                else:
                    print(f"Skipping line {i+1}: {lines[i+1]}")
                    i += 1
                    continue
                text += " " + lines[i + 2].strip()
            final_audio += generate_speech(
                text, start_time, end_time, voice_id, output_dir, xi_api_key
            )
            i += 3
        final_audio.export(os.path.join(output_dir, "final_audio.mp3"), format="mp3")
        shutil.rmtree(f"{output_dir}/temp_audio_segments")


def generate_speech(text, start_time, end_time, voice_id, output_dir, xi_api_key):
    audio_data = text_to_speech(text, voice_id, xi_api_key)
    audio = AudioSegment.from_mp3(BytesIO(audio_data))
    audio.export(
        os.path.join(
            output_dir, f"temp_audio_segments/audio_{start_time}_{end_time}.mp3"
        ),
        format="mp3",
    )
    intended_duration = (end_time - start_time) * 1000
    actual_duration = len(audio)
    if actual_duration < intended_duration:
        silence_duration = intended_duration - actual_duration
        silence_segment = AudioSegment.silent(
            duration=silence_duration
        )  # Corrected here
        audio += silence_segment
    elif actual_duration > intended_duration:
        audio = audio[:intended_duration]
    return audio


def delete_voice(voice_id, xi_api_key):
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {
        "Accept": "application/json",
        "xi-api-key": xi_api_key,
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print(f"Voice with ID {voice_id} deleted successfully.")
    else:
        print(
            f"Failed to delete voice. Status code: {response.status_code}, Response: {response.text}"
        )
