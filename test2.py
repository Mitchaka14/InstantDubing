import os
import requests
import time
import shutil
from pydub import AudioSegment, effects
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
    # if response.status_code == 200:
    #     print(f"Voice with ID {voice_id} deleted successfully.")
    # else:
    #     print(
    #         f"Failed to delete voice. Status code: {response.status_code}, Response: {response.text}"
    #     )


def extract_audio_segments(audio_path, segments):
    audio = AudioSegment.from_file(audio_path)
    audio_segments = [
        audio[start_time * 1000 : end_time * 1000] for start_time, end_time in segments
    ]
    return audio_segments


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
        for _ in range(2):  # Send each file 20 times
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
    audio_data = text_to_speech(text, voice_id, xi_api_key)
    try:
        audio = AudioSegment.from_mp3(BytesIO(audio_data))
    except CouldntDecodeError:
        print(f"Could not decode audio data for text: {text}")
        return AudioSegment.empty()  # Return an empty segment if decoding fails

    intended_duration = (end_time - start_time) * 1000
    actual_duration = len(audio)

    # if the actual duration is less, pad with silence at the start
    if actual_duration < intended_duration:
        silence_duration = intended_duration - actual_duration
        silence_segment = AudioSegment.silent(duration=silence_duration)
        audio = audio + silence_segment  # Append silence to end

    # if the actual duration is more, speedup
    elif actual_duration > intended_duration:
        speedup_rate = intended_duration / actual_duration
        audio = effects.speedup(audio, speedup_rate)

    return audio


def pad_audio_end(final_audio, total_time, xi_api_key):
    actual_duration = len(final_audio)
    intended_duration = total_time * 1000
    if actual_duration < intended_duration:
        silence_duration = intended_duration - actual_duration
        silence_segment = AudioSegment.silent(duration=silence_duration)
        final_audio += silence_segment
    return final_audio


def process_audio_and_transcription_file(
    vocal_audio_path, file_path, name, output_dir, XI_API_KEY
):
    segments = []

    with open(file_path, "r", encoding="utf8") as file:
        lines = file.readlines()
        i = 0
        while i < len(lines):
            if lines[i].strip() == "":
                i += 1
                continue
            if "-->" in lines[i + 1]:
                start_time, end_time = map(
                    convert_time_to_seconds, lines[i + 1].strip().split(" --> ")
                )
                segments.append((start_time, end_time))
            i += 3

    total_segments = len(segments)

    if not os.path.exists(f"{output_dir}/temp_audio_segments"):
        os.makedirs(f"{output_dir}/temp_audio_segments")

    i = 0
    final_audio = AudioSegment.empty()
    current_timestamp = 0
    segment_count = 0
    with open(file_path, "r", encoding="utf8") as file:
        lines = file.readlines()
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

            audio_segments = extract_audio_segments(
                vocal_audio_path, [(start_time, end_time)]
            )

            temp_folder = f"{output_dir}/temp_audio_segments/{name}_{i}"
            os.makedirs(temp_folder)

            audio_path = f"{temp_folder}/temp_audio.mp3"
            audio_segments[0].export(audio_path, format="mp3")

            vID = add_voice_to_elevenlabs(audio_segments, "temp", XI_API_KEY)
            generated_speech_segment = generate_speech(
                text, start_time, end_time, vID, output_dir, XI_API_KEY
            )
            delete_voice(vID, XI_API_KEY)

            os.remove(audio_path)
            os.rmdir(temp_folder)

            # Add silence before the generated speech segment to ensure correct placement
            silence_duration = (start_time - current_timestamp) * 1000
            if silence_duration > 0:
                silence_segment = AudioSegment.silent(duration=silence_duration)
                final_audio += silence_segment

            final_audio += generated_speech_segment
            current_timestamp = end_time

            segment_count += 1
            if (
                segment_count % (total_segments // 4) == 0
                or segment_count == total_segments
            ):
                print(f"Processed {segment_count} out of {total_segments} segments.")
            i += 3
    final_audio.export(os.path.join(output_dir, f"final_audio.mp3"), format="mp3")

    print("Done processing!")


if __name__ == "__main__":
    import config

    VOCAL_AUDIO_PATH = "downloads/mha1/combined_vocals.wav"
    TRANSCRIPTION_FILE_PATH = "downloads/mha1/translation.srt"
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
