# agent/utils.py
import logging
import random
import string

def setup_logging(level=logging.INFO):
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("call_assistant")

def generate_room_name(prefix="outbound"):
    """Generate a random room name for LiveKit sessions"""
    random_suffix = ''.join(random.choice(string.digits) for _ in range(10))
    return f"{prefix}-{random_suffix}"