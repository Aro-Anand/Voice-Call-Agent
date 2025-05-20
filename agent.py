## Main.py
from __future__ import annotations
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, RunContext, BackgroundAudioPlayer,AudioConfig ,BuiltinAudioClip
from livekit.plugins import openai, deepgram
from openai.types.beta.realtime.session import TurnDetection
from prompts import INSTRUCTIONS
from livekit import api, rtc
import json
import os
import asyncio
from datetime import datetime
import logging
from typing import Any
load_dotenv()

logger = logging.getLogger("call_assistant")


class Assistant(Agent):
    def __init__(self, *, name: str, dial_info: dict[str, Any] = None):
        super().__init__(instructions=INSTRUCTIONS)
        self.name = name        ## SheraAI_Assistant
        self.dial_info = dial_info or {}  ##{}
        self.participant = None
        logger.info(f"Assistant initialized with name: {name}")

    def set_participant(self, participant: rtc.RemoteParticipant):
        self.participant = participant

    def get_time_based_greeting(self) -> str:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"
    def create_greeting(self) -> str:
        customer_name = self.dial_info.get("name", "")
        customer_query = self.dial_info.get("query", "")
        time_greeting = self.get_time_based_greeting()
        if customer_query:
            return f"Hey {customer_name}, {time_greeting.lower()}! You’re speaking with FRAN-TIGER — your friendly AI on a mission to help! I heard you’ve got a question about {customer_query}, and I’m all ears. Let’s sort it out together — how can I assist you today?"

        else:
            return f"Hey {customer_name}, {time_greeting}! I’m FRAN-TIGER, your smart assistant. What can I help you tackle today?"
        

    async def on_session_started(self, ctx: RunContext) -> None:
        """Called when the session starts"""
        logger.info("Session started, speaking welcome message...")

        try:
            greeting = self.create_greeting()
            # await ctx.session.say(greeting)
            logger.info(f"Generated greeting: {greeting}")
            
            # No need to manually speak here as this will be handled by the session.generate_reply
            logger.info("Greeting ready")
        except Exception as e:
            logger.error(f"Error generating welcome speech: {e}")
            import traceback
            traceback.print_exc()

## EntryPoint of the Function:

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()        ## It connect the room for agent and participant.
    
    # Parse metadata from app.py
    try:
        if ctx.job.metadata:
            dial_info = json.loads(ctx.job.metadata)
            logger.info(f"Parsed dial info: {dial_info}")
        else:
            dial_info = {"phone_number": os.getenv("MY_PHONE_NUMBER")}
            logger.warning("No metadata provided, using default dial info")

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing metadata: {e}")
        logger.error(f"Raw metadata: '{ctx.job.metadata}'")
        dial_info = {"phone_number": os.getenv("MY_PHONE_NUMBER")}
    
    # Create agent with dial info
    agent = Assistant(
        name="SheraAI_Assistant",
        dial_info=dial_info
    )
    
    # Create session
    session = AgentSession(
        stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"), model="nova-2"),
        llm = openai.LLM(model=os.getenv("MODEL_NAME")),
        tts = openai.TTS(model="gpt-4o-mini-tts", voice="ash")
    )
    
    # Handle SIP participant creation and start session
    try:
        phone_number = dial_info["phone_number"]
        logger.info(f"Dialing phone number: {phone_number}")

        partcipant_identity = dial_info.get("name", "customer")
        
        # Make the outbound call
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
                sip_call_to=phone_number,
                participant_identity=partcipant_identity,
                krisp_enabled=True
            )
        )

        # Wait for participant to join and set it as the agent's participant
        participant = await ctx.wait_for_participant(identity=partcipant_identity)
        agent.set_participant(participant)
        logger.info("Call picked up successfully")

        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(),
        )

        # # ### Greeting
        obj = Assistant(name="SheraAI_Assistant", dial_info=dial_info)
        greet = obj.create_greeting()
        # print(f"=========***********{greet}********************==============")
        # await session.say(allow_interruptions=True, text=f"{greet}")
        # await session.say(f"{greet}")
        await session.generate_reply(instructions=f"Greet the user and say '{greet}")

    except api.TwirpError as e:
        logger.error(f"Error creating SIP participant: {e.message}, "
                    f"SIP status: {e.metadata.get('sip_status_code')} "
                    f"{e.metadata.get('sip_status')}")
        ctx.shutdown()
        return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint, agent_name="SheraAI_Assistant"))