# agent/entrypoint.py
from dotenv import load_dotenv
from livekit import agents, api, rtc
from .agent import CallAgent
from livekit.plugins import openai, deepgram
from livekit.agents import AgentSession, RoomInputOptions
import json
import os
import logging
import asyncio

load_dotenv()
logger = logging.getLogger("call_assistant")

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    
    # Parse metadata
    try:
        if ctx.job.metadata:
            dial_info = json.loads(ctx.job.metadata)
            logger.info(f"Parsed dial info: {dial_info}")
        else:
            dial_info = {"phone_number": os.getenv("DEFAULT_PHONE_NUMBER")}
            logger.warning("No metadata provided, using default dial info")

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing metadata: {e}")
        logger.error(f"Raw metadata: '{ctx.job.metadata}'")
        dial_info = {"phone_number": os.getenv("DEFAULT_PHONE_NUMBER")}
    
    # Create agent with dial info
    agent = CallAgent(
        name=os.getenv("AGENT_NAME", "AI_Assistant"),
        dial_info=dial_info
    )
    
    # Create session
    session = AgentSession(
        stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"), model="nova-2"),
        llm = openai.LLM(model=os.getenv("MODEL_NAME", "gpt-4o")),
        tts = openai.TTS(model=os.getenv("TTS_MODEL", "gpt-4o-mini-tts"), voice=os.getenv("TTS_VOICE", "ash"))
    )
    
    # Handle SIP participant creation and start session
    try:
        phone_number = dial_info["phone_number"]
        logger.info(f"Dialing phone number: {phone_number}")

        participant_identity = dial_info.get("name", "customer")
        
        # Make the outbound call
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=os.getenv("SIP_OUTBOUND_TRUNK_ID"),
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                krisp_enabled=True
            )
        )

        # Wait for participant to join and set it as the agent's participant
        participant = await ctx.wait_for_participant(identity=participant_identity)
        agent.set_participant(participant)
        logger.info("Call picked up successfully")

        # Start the session
        await session.start(
            room=ctx.room,
            agent=agent,
            room_input_options=RoomInputOptions(),
        )

        # Generate initial greeting
        greeting = agent.create_greeting()
        await session.generate_reply(instructions=f"Greet the user and say '{greeting}'")

    except api.TwirpError as e:
        logger.error(f"Error creating SIP participant: {e.message}, "
                    f"SIP status: {e.metadata.get('sip_status_code')} "
                    f"{e.metadata.get('sip_status')}")
        ctx.shutdown()
        return