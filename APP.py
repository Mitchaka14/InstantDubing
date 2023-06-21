from vTranslate import VTranslator
import config
import os


def main():
    openaiKey = config.Token1
    xi_api_key = config.Token2
    out_dir = "downloads/frenchSlowspeech"
    mha = "https://www.youtube.com/watch?v=XyyqoeaiuUM&ab_channel=Herryjee"
    vinlandsaga = "https://www.youtube.com/watch?v=HmEt4s-BugA&ab_channel=CrunchyrollFR"
    frenchSlowspeech = "https://www.youtube.com/watch?v=3NwEYhSTk74"
    depressingCHineseAd = "https://www.youtube.com/watch?v=v-cJDV-BfP4"
    link = frenchSlowspeech
    processor = VTranslator(
        out_dir,
        link,
        openaiKey,
        xi_api_key,
    )
    processor.process_video()


if __name__ == "__main__":
    main()
