🎥 InstantDubing: AI Video Translator 🌐

Welcome to InstantDubing, an innovative AI Video Translator! This project uses cutting-edge AI technology to transcribe, translate, and then re-voice a video into English in the original speaker's voice. 🎙️🌍

🚀 How to Use

InstantDubing is designed to be straightforward to use. Here is a step-by-step guide:

Prerequisites: Make sure all the required Python dependencies listed in requirements.txt are installed in your environment. You can install these using pip:

Copy code
pip install -r requirements.txt
API Keys: You will need to provide API keys for the speech-to-text, translation, and text-to-speech services used by the application. These keys should be placed in the config.py file in the format:

python
Copy code
Token1 = "Your_Speech_to_Text_and_Translation_API_Key"
Token2 = "Your_Text_to_Speech_API_Key"
Running the Application: Run the main application file APP.py to start the video translation process. You can do this from the command line:

Copy code
python APP.py
By default, APP.py is set up to translate a specific YouTube video. If you want to translate a different video, replace the YouTube link assigned to the link variable in APP.py.

The final translated video will be saved in the downloads/frenchSlowspeech directory (or another directory specified in the out_dir variable in APP.py).

Please note that the exact results and processing times may vary depending on the video length, internet speed, and the performance of the underlying services.

🐞 Known Bugs and Issues

While InstantDubing aims to provide accurate and natural-sounding video translations, there are a few known issues that we are working to improve:

Emotion: The AI-generated voice might not accurately capture the emotional nuances of the original speaker. We are working on improving the emotion preservation in the AI voice. 😃😟

Context: Sometimes, the translations might lack context, leading to less accurate or natural sounding translations. We are working to enhance the translation model to better handle context. 📝🌐

Short Videos: The system might not perform well on very short videos. We are optimizing the process to improve performance on shorter video clips. 🎥⏱️

We appreciate your patience and understanding as we work to resolve these issues and improve the system. If you encounter any other issues or have suggestions for improvements, please feel free to open an issue on the repository.

🤝 Contributing
As a solo developer, I'm always open to contributions and suggestions! If you have any ideas or want to contribute to the project, feel free to make a pull request or open an issue. Let's make InstantDubing the best it can be, together! 🤗🙌
