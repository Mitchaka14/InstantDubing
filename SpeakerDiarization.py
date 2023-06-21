from pyAudioAnalysis import audioSegmentation as aS
from pydub import AudioSegment


def speaker_identification(
    audio_file_path, srt_file_path, num_speakers, output_file_path
):
    def convert_to_wav(mp3_path):
        audio = AudioSegment.from_mp3(mp3_path)
        wav_path = mp3_path.replace(".mp3", ".wav")
        audio.export(wav_path, format="wav")
        return wav_path

    def diarize_speakers(file_path, num_speakers):
        if file_path.endswith(".mp3"):
            file_path = convert_to_wav(file_path)
        flags_ind, cls_1, cls_2 = aS.speaker_diarization(file_path, num_speakers)
        return flags_ind

    def write_speaker_identified_srt(
        srt_file_path, diarization_results, output_file_path
    ):
        with open(srt_file_path, "r") as f:
            lines = f.readlines()

        with open(output_file_path, "w") as f:
            segment_index = 0
            for line in lines:
                if "-->" in line:
                    line = (
                        line.strip()
                        + f" (speaker{diarization_results[segment_index] + 1})\n"
                    )
                    segment_index += 1
                f.write(line)

    # Diarize the speakers
    diarization_results = diarize_speakers(audio_file_path, num_speakers)

    # Write the modified SRT file
    write_speaker_identified_srt(
        srt_file_path,
        diarization_results,
        output_file_path,
    )


# Example usage:
speaker_identification(
    "downloads/videofile/combined_vocals.wav",
    "downloads/videofile/translation.srt",
    2,
    "downloads/videofile/subtitle_speaker_identified.srt",
)
