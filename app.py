# app.py - modified for cloud deployment
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os
import asyncio
from livekit import api as lkapi
import random
import logging
import json
import traceback
import aiohttp

# Setup more detailed logging
logging.basicConfig(level=logging.INFO if os.getenv("NODE_ENV") == "production" else logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Get LiveKit credentials from environment variables
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
AGENT_NAME = os.getenv("AGENT_NAME")

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
        room_name = f"outbound-{''.join(str(random.randint(0, 9)) for _ in range(10))}"
        
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
        
        # Use a better approach to handle asyncio with Flask
        try:
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async function and ensure proper cleanup
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
            
    except Exception as e:
        logger.error(f"Error in form processing: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": f"Error processing your request: {str(e)}"
        }), 500

async def create_dispatch(room_name, metadata):
    """Create a LiveKit agent dispatch"""
    # Create a new session explicitly for this function call
    session = aiohttp.ClientSession()
    try:
        logger.debug("Creating LiveKit API client")
        lk_client = lkapi.LiveKitAPI(
            url=LIVEKIT_URL,
            api_key=LIVEKIT_API_KEY,
            api_secret=LIVEKIT_API_SECRET,
        )
        
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
        
        # Log the full response
        logger.debug(f"Raw response: {response}")
        
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
    finally:
        # Explicitly close the session
        if not session.closed:
            await session.close()

if __name__ == '__main__':
    # Get port from environment variable (required for many cloud platforms)
    port = int(os.environ.get("PORT", 8080))
    
    # Print out some startup info
    logger.info(f"Starting app with LIVEKIT_URL: {LIVEKIT_URL}")
    logger.info(f"Agent name: {AGENT_NAME}")
    
    # In production, don't use debug mode
    debug_mode = os.environ.get("NODE_ENV") != "production"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
