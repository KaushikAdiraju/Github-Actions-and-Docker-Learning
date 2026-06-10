import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (Make sure GROQ_API_KEY is in your .env)
load_dotenv()

# Initialize the Groq client
client = Groq()

def transcribe_audio(file_path):
    """Takes an audio file path, transcribes it using Groq Whisper, and returns the text."""
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
              file=(file_path, file.read()),
              # whisper-large-v3 is the industry standard for fast, accurate STT
              model="whisper-large-v3", 
              response_format="json",
              language="en", # You can change this or remove it for auto-detect
            )
        return transcription.text
    except Exception as e:
        print(f"Transcription error: {e}")
        return None