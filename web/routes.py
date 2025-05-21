# web/routes.py
from flask import render_template, request, jsonify
import json
import logging
import asyncio
import aiohttp
import traceback
import atexit
import signal
from livekit import api as lkapi
from agent.utilis import generate_room_name, logging, setup_logging
from .config import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, AGENT_NAME

logger = logging.getLogger(__name__)

# Create a global session that will be reused
_session = None
_lk_client = None

def get_livekit_client():
    """Get or create a LiveKit API client with a shared session"""
    global _session, _lk_client
    if _lk_client is None:
        logger.debug("Creating LiveKit API client")
        _lk_client = lkapi.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET
        )
    return _lk_client

async def cleanup_resources():
    """Clean up global resources"""
    global _session
    if _session:
        await _session.close()
        logger.debug("Closed global aiohttp session")
        _session = None

# Register cleanup on exit
def cleanup_on_exit():
    """Run cleanup in a new event loop when the application exits"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(cleanup_resources())
    finally:
        loop.close()

atexit.register(cleanup_on_exit)

# Also handle SIGINT and SIGTERM for cleaner Docker shutdowns
for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, lambda signum, frame: (cleanup_on_exit(), signal.default_int_handler(signum, frame)))

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health_check():
        """Health check endpoint for cloud providers"""
        return jsonify({"status": "ok"})

    @app.route('/submit', methods=['POST'])
    def submit():
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            email = request.form.get('email', '').strip()
            query = request.form.get('query', '').strip()
            
            # Validate required fields
            if not name or not phone:
                return jsonify({
                    "success": False,
                    "message": "Name and phone number are required."
                }), 400
            
            # Create random room name
            room_name = generate_room_name()
            
            # Prepare metadata as a JSON string
            metadata_dict = {
                "phone_number": phone,
                "name": name,
                "email": email,
                "query": query if query else None  # Only include query if it's not empty
            }
            metadata = json.dumps(metadata_dict)
            logger.debug(f"Prepared metadata: {metadata}")
            
            # Create the dispatch
            logger.info(f"Creating dispatch for {name} at {phone}")
            
            # Use nest_asyncio to handle asyncio in Flask
            import nest_asyncio
            nest_asyncio.apply()
            
            # Create a new event loop for this request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the async function
                result = loop.run_until_complete(create_dispatch(room_name, metadata))
                
                return jsonify({
                    "success": True, 
                    "message": "Your call has been scheduled. Our agent will call you shortly.",
                    "details": {
                        "room_name": room_name,
                        "dispatch_id": result.get("dispatch_id", "No dispatch ID returned")
                    }
                })
                
            except Exception as inner_e:
                logger.error(f"Error in async dispatch: {str(inner_e)}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "success": False,
                    "message": f"Error creating dispatch: {str(inner_e)}"
                }), 500
            finally:
                # Clean up the event loop
                loop.close()
            
        except Exception as e:
            logger.error(f"Error in form processing: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "message": f"Error processing your request: {str(e)}"
            }), 500

async def create_dispatch(room_name, metadata):
    """Create a LiveKit agent dispatch"""
    try:
        # Get the global LiveKit client
        lk_client = get_livekit_client()
        
        # Create dispatch request
        logger.debug(f"Creating dispatch request for agent {AGENT_NAME}")
        dispatch_request = lkapi.CreateAgentDispatchRequest(
            agent_name=AGENT_NAME,
            room=room_name,
            metadata=metadata
        )

        # Send dispatch request
        logger.debug("Sending dispatch request")
        response = await lk_client.agent_dispatch.create_dispatch(dispatch_request)
        
        # Extract dispatch_id safely
        dispatch_id = getattr(response, 'dispatch_id', None) or getattr(response, 'id', 'Unknown')
        
        return {
            "dispatch_id": dispatch_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"LiveKit dispatch error: {str(e)}")
        logger.error(traceback.format_exc())
        raise
