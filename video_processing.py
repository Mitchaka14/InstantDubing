# ./video_processing.py
import os
import subprocess
from pytube import YouTube


def download_youtube_video(youtube_url, output_dir):
    youtubeObject = YouTube(youtube_url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        # Download the video to the output directory
        video_path = youtubeObject.download(output_path=output_dir)
        print("Download is completed successfully")
        return video_path
    except Exception as e:
        print(f"An error has occurred: {e}")


def extract_audio_from_video(video_path, audio_path):
    # Ensure the uploads directory exists
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    command = f'ffmpeg -i "{video_path}" -ab 160k -ac 2 -ar 44100 -vn "{audio_path}"'
    subprocess.call(command, shell=True)
    # Get the length of the audio
    command = f'ffprobe -i "{audio_path}" -show_entries format=duration -v quiet -of csv="p=0"'
    result = subprocess.run(command, shell=True, capture_output=True)
    duration = float(result.stdout.decode().strip())
    return duration


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=A5DeOBKHaOg&t=37s"
    output_dir = "temp"
    video_path = download_youtube_video(youtube_url, output_dir)
    audio_path = "temp/audio"
    extract_audio_from_video(video_path, audio_path)
