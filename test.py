import os
import requests
import time
import shutil
from pydub import AudioSegment, silence
from io import BytesIO
from pydub.exceptions import CouldntDecodeError


def text_to_speech(text, voice_id, xi_api_key):
    print(f"Converting text to speech for text: {text}")

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
            "stability": 0.8,
            "similarity_boost": 0.9,
        },
    }
    response = requests.post(url, json=data, headers=headers)
    # Check if the response was successful
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}")
    return response.content


def convert_time_to_seconds(time_str):
    h, m, s = time_str.split(":")
    s, ms = s.split(",")
    return int(h) * 3600 + int(m) * 60 + float(f"{s}.{ms}")


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


def split_audio_into_chunks(audio_path, max_chunk_size_mb=10):
    audio = AudioSegment.from_file(audio_path)

    # Calculate average bit rate (in kbps)
    audio_kbps = audio.frame_rate * audio.frame_width * 8 / 1024
    # Calculate chunk length in milliseconds that would keep its size under max_chunk_size_mb
    chunk_length_ms = ((max_chunk_size_mb * 1024 * 8) / audio_kbps) * 1000

    chunks = []
    for i in range(0, len(audio), int(chunk_length_ms)):
        chunks.append(audio[i : i + int(chunk_length_ms)])
    return chunks


def add_voice_to_elevenlabs(audio_chunks, name, XI_API_KEY):
    print(f"Adding voice to ElevenLabs for name: {name}")
    for i, chunk in enumerate(audio_chunks):
        print(f"Processing audio chunk {i}")

    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "accept": "application/json",
        "xi-api-key": XI_API_KEY,
    }
    data = {"name": name}
    files = []
    file_objects = []
    for i, chunk in enumerate(audio_chunks):
        chunk.export(f"temp_chunk_{i}.mp3", format="mp3")
    for i in range(len(audio_chunks)):
        file_object = open(f"temp_chunk_{i}.mp3", "rb")
        files.append(("files", (f"temp_chunk_{i}.mp3", file_object, "audio/mpeg")))
        file_objects.append(file_object)
    voice_id = None
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        if response.status_code == 200:
            voice_id = response.json()["voice_id"]
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
    time.sleep(1)
    return voice_id


def generate_speech(text, start_time, end_time, voice_id, output_dir, xi_api_key):
    print(
        f"Generating speech for text: {text}, start_time: {start_time}, end_time: {end_time}"
    )

    audio_data = text_to_speech(text, voice_id, xi_api_key)
    try:
        audio = AudioSegment.from_mp3(BytesIO(audio_data))
    except CouldntDecodeError:
        print(f"Could not decode audio data for text: {text}")
        return AudioSegment.empty()  # Return an empty segment if decoding fails

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
        silence_segment = AudioSegment.silent(duration=silence_duration)
        audio += silence_segment
    elif actual_duration > intended_duration:
        audio = audio[:intended_duration]
    return audio


def process_audio_and_transcription_file(
    vocal_audio_path, file_path, name, output_dir, XI_API_KEY
):
    audio_chunks = split_audio_into_chunks(vocal_audio_path)
    vID = add_voice_to_elevenlabs(audio_chunks, name, XI_API_KEY)
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
                    i += 1
                    continue
                text += " " + lines[i + 2].strip()
            final_audio += generate_speech(
                text, start_time, end_time, vID, output_dir, XI_API_KEY
            )
            i += 3
        final_audio.export(os.path.join(output_dir, "final_audio.mp3"), format="mp3")
        shutil.rmtree(f"{output_dir}/temp_audio_segments")
        delete_voice(vID, XI_API_KEY)


if __name__ == "__main__":
    import config

    VOCAL_AUDIO_PATH = "downloads/painspeech/combined_vocals.wav"
    TRANSCRIPTION_FILE_PATH = "downloads/painspeech/translation.srt"
    VOICE_NAME = "temp"
    OUTPUT_DIRECTORY_PATH = "temp"
    YOUR_XI_API_KEY = config.Token2

    process_audio_and_transcription_file(
        VOCAL_AUDIO_PATH,
        TRANSCRIPTION_FILE_PATH,
        VOICE_NAME,
        OUTPUT_DIRECTORY_PATH,
        YOUR_XI_API_KEY,
    )
