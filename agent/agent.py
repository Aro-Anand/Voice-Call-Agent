# agent/agent.py
from __future__ import annotations
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RunContext, AudioConfig
from livekit.plugins import openai, deepgram
from shared.prompts import get_agent_instructions
import json
import os
import logging
from typing import Any

load_dotenv()
logger = logging.getLogger("call_assistant")

class CallAgent(Agent):
    def __init__(self, *, name: str, dial_info: dict[str, Any] = None):
        instructions = get_agent_instructions()
        super().__init__(instructions=instructions)
        self.name = name
        self.dial_info = dial_info or {}
        self.participant = None
        logger.info(f"Assistant initialized with name: {name}")

    def set_participant(self, participant):
        self.participant = participant

    def create_greeting(self) -> str:
        """Create a personalized greeting for the customer"""
        from shared.prompts import get_time_greeting, get_welcome_message
        
        customer_name = self.dial_info.get("name", "")
        customer_query = self.dial_info.get("query", "")
        
        return get_welcome_message(customer_name, customer_query)
        
    async def on_session_started(self, ctx: RunContext) -> None:
        """Called when the session starts"""
        logger.info("Session started, preparing welcome message...")
        
        try:
            # Greeting will be handled by the session.generate_reply in the entry point
            greeting = self.create_greeting()
            logger.info(f"Generated greeting: {greeting}")
        except Exception as e:
            logger.error(f"Error generating welcome speech: {e}")
            import traceback
            traceback.print_exc()