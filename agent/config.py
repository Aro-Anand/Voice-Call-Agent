# agent/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Agent configuration
AGENT_NAME = os.getenv("AGENT_NAME", "AI_Assistant")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
TTS_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
TTS_VOICE = os.getenv("TTS_VOICE", "ash")

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
SIP_OUTBOUND_TRUNK_ID = os.getenv("SIP_OUTBOUND_TRUNK_ID")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Default settings
DEFAULT_PHONE_NUMBER = os.getenv("DEFAULT_PHONE_NUMBER", "")