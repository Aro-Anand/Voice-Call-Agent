# web/app.py
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import logging
from shared.config import LOG_LEVEL, PORT, HOST, IS_PRODUCTION
from .routes import register_routes

# Setup logging
logging.basicConfig(
    level=logging.getLevelName(LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Register routes
    register_routes(app)
    
    logger.info(f"Application initialized in {IS_PRODUCTION and 'PRODUCTION' or 'DEVELOPMENT'} mode")
    return app

app = create_app()

if __name__ == '__main__':
    logger.info(f"Starting web server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=not IS_PRODUCTION)