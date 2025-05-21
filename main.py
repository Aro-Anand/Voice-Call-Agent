# main.py
import os
import logging
from agent import setup_logging
from shared.config import IS_PRODUCTION, PORT, HOST

logger = setup_logging(level=logging.INFO if IS_PRODUCTION else logging.DEBUG)

if __name__ == "__main__":
    from web.app import app
    logger.info(f"Starting FRAN-TIGER call agent service on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=not IS_PRODUCTION)