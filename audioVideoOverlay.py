# audioVideoOverlay
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip


def overlay_audios(background_audio_path, overlay_audio_path, output_audio_path):
    # Load audio files
    background_audio = AudioSegment.from_file(background_audio_path)
    overlay_audio = AudioSegment.from_file(overlay_audio_path)

    # Convert audios to mp3
    background_audio = background_audio.export("temp_background.mp3", format="mp3")
    overlay_audio = overlay_audio.export("temp_overlay.mp3", format="mp3")

    # Reload audio files in mp3 format
    background_audio = AudioSegment.from_file("temp_background.mp3")
    overlay_audio = AudioSegment.from_file("temp_overlay.mp3")

    # Overlay audios
    combined = background_audio.overlay(overlay_audio)

    # Export to a file
    combined.export(output_audio_path, format="mp3")

    # Delete temporary files
    os.remove("temp_background.mp3")
    os.remove("temp_overlay.mp3")


def replace_video_audio(video_path, audio_path, output_video_path):
    # Load video clip
    video = VideoFileClip(video_path)

    # Load audio clip
    audio = AudioFileClip(audio_path)

    # Replace video audio
    video = video.set_audio(audio)

    # Write to a file
    video.write_videofile(output_video_path, codec="libx264")
