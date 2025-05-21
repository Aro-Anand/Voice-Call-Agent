# web/config.py
import os
from dotenv import load_dotenv
from shared.config import IS_PRODUCTION

load_dotenv()

# LiveKit connection settings
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

# Agent configuration
AGENT_NAME = os.getenv("AGENT_NAME", "FRAN-TIGER")