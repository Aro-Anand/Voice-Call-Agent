# shared/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Environment detection
ENV = os.getenv("NODE_ENV", "development")
IS_PRODUCTION = ENV == "production"

# Shared logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if IS_PRODUCTION else "DEBUG")

# Shared server configuration
PORT = int(os.getenv("PORT", "8080"))
HOST = os.getenv("HOST", "0.0.0.0")