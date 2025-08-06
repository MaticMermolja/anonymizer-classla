#!/usr/bin/env python3
"""
Quick health check for Railway deployment
Just confirms the process is running, doesn't wait for CLASSLA
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check that always passes"""
    return jsonify({
        'status': 'starting',
        'service': 'GDPR Anonymizer API',
        'message': 'Service is starting up, please wait...'
    })

@app.route('/health', methods=['GET'])
def detailed_health():
    """Detailed health check"""
    return jsonify({
        'status': 'starting',
        'service': 'GDPR Anonymizer API',
        'message': 'CLASSLA models are loading, please wait...'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Quick health check server starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False) 