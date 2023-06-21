# ./InstantDubing/vTranslate.py
import os

try:
    from InstantDubing import (
        video_processing,
        audio_processing,
        vocal_separation,
        audioVideoOverlay,
        test2,
    )
except ImportError:
    import video_processing
    import audio_processing
    import vocal_separation
    import audioVideoOverlay
    import test2


class VTranslator:
    def __init__(self, base_folder, video_input, token_1, token_2):
        self.base_folder = base_folder
        self.video_input = video_input
        self.token_1 = token_1
        self.token_2 = token_2
        self.output_dir = self.base_folder
        os.makedirs(self.output_dir, exist_ok=True)

    def process_video(self):
        print("Starting video processing...")
        video_path = ""
        if "youtube.com" in self.video_input:
            print("Downloading YouTube video...")
            video_path = video_processing.download_youtube_video(
                self.video_input, self.output_dir
            )
        else:
            video_path = self.video_input

        print("Extracting audio from video...")
        audio_path = f"{self.output_dir}/audio_file.mp3"
        video_processing.extract_audio_from_video(video_path, audio_path)

        action = "translation"

        print("Separating vocals...")
        vocal_separation.separate_vocals(audio_path, self.output_dir)
        a_audio_path = f"{self.output_dir}/combined_accompaniments.wav"
        v_audio_path = f"{self.output_dir}/combined_vocals.wav"

        print("Splitting audio...")
        audio_chunks = audio_processing.split_audio(v_audio_path, self.token_1)

        print("Processing audio chunks...")
        results = audio_processing.process_audio_chunks(
            "translation",
            audio_chunks,
            self.token_1,
        )

        Actionfile = f"{self.output_dir}/{action}.srt"
        with open(Actionfile, "w", encoding="utf-8") as output_file:
            for result in results:
                if result is not None:
                    output_file.write(result + "\n")
                    print(f"Result: {result}")

        print("Processing vocal audio and transcription file...")
        test2.process_audio_and_transcription_file(
            v_audio_path,
            Actionfile,
            "tempVoiceMitch",
            self.output_dir,
            self.token_2,
        )

        print("Overlaying audios...")
        output_audio_path = f"{self.output_dir}/Cfinal_audio.mp3"
        overlay_audio_path = f"{self.output_dir}/final_audio.mp3"
        output_video_path = f"{self.output_dir}/Translated.mp4"
        audioVideoOverlay.overlay_audios(
            a_audio_path, overlay_audio_path, output_audio_path
        )
        audioVideoOverlay.replace_video_audio(
            video_path, output_audio_path, output_video_path
        )

        print("Video processing completed.")
