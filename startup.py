#!/usr/bin/env python3
"""
Optimized startup script for instant response GDPR Anonymizer API
Pre-initializes all models during startup for zero-latency requests
"""

import os
import time
import logging
from comprehensive_gdpr_anonymizer import ComprehensiveGDPRAnonymizer
from docker_api import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pre_initialize_anonymizer():
    """Pre-initialize the anonymizer during startup for instant responses."""
    logger.info("🚀 Pre-initializing GDPR Anonymizer for instant responses...")
    start_time = time.time()
    
    try:
        # Initialize the anonymizer with caching
        anonymizer = ComprehensiveGDPRAnonymizer(
            language='sl', 
            use_gpu=False,
            preload_models=True  # Pre-load for instant responses
        )
        
        # Test the anonymizer with a simple text to ensure it's working
        test_text = "Test text for initialization."
        result = anonymizer.anonymize_text(test_text)
        
        init_time = time.time() - start_time
        logger.info(f"✅ Anonymizer pre-initialized successfully in {init_time:.2f} seconds")
        logger.info(f"📊 Test result: {result['total_entities_masked']} entities masked")
        logger.info(f"💾 Models cached in volume for fast restarts")
        
        return anonymizer
        
    except Exception as e:
        logger.error(f"❌ Failed to pre-initialize anonymizer: {str(e)}")
        raise e

def main():
    """Main startup function."""
    logger.info("🚀 Starting optimized GDPR Anonymizer API...")
    
    # Pre-initialize the anonymizer
    anonymizer = pre_initialize_anonymizer()
    
    # Store the anonymizer instance globally for the API
    import docker_api
    docker_api.anonymizer = anonymizer
    
    # Get port from environment
    port = int(os.environ.get('PORT', 8000))
    
    logger.info(f"🌐 Starting Flask API server on port {port}...")
    logger.info("⚡ API is ready for instant responses!")
    logger.info("📈 Performance: Zero-latency anonymization available")
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main() 