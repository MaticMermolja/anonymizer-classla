#!/usr/bin/env python3
"""
Startup script for GDPR Anonymizer API
Handles CLASSLA initialization before starting Flask server
"""

import os
import sys
import time
import logging
from docker_api import app, initialize_anonymizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    logger.info("🚀 Starting GDPR Anonymizer API...")
    
    # Get port from environment
    port = int(os.environ.get('PORT', 8000))
    
    # Start Flask app FIRST (so Railway can do health checks)
    logger.info("🚀 Starting Flask server immediately...")
    
    # Start Flask in a separate thread so we can initialize CLASSLA in background
    import threading
    
    def start_flask():
        app.run(host='0.0.0.0', port=port, debug=False)
    
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Now initialize CLASSLA models in background
    logger.info("📦 Pre-initializing CLASSLA models in background...")
    start_time = time.time()
    
    try:
        initialize_anonymizer()
        init_time = time.time() - start_time
        logger.info(f"✅ CLASSLA models loaded successfully in {init_time:.2f} seconds!")
        logger.info("🎯 API is now fully ready for requests!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize CLASSLA models: {str(e)}")
        logger.error("Service is running but anonymization will fail")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(60)  # Sleep for 1 minute
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == '__main__':
    main() 