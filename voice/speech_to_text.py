import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


def speech_to_text(audio_file):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in .env")

    client = Groq(api_key=api_key)

    transcription = client.audio.transcriptions.create(
        file=("audio.wav", audio_file),
        model="whisper-large-v3-turbo",
        language="en",
        response_format="text",
        temperature=0
    )

    return transcription