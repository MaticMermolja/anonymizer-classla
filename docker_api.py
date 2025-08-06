#!/usr/bin/env python3
"""
Docker API Server for GDPR Anonymizer

Simple Flask API that receives text and returns anonymized results.
"""

from flask import Flask, request, jsonify
from comprehensive_gdpr_anonymizer import ComprehensiveGDPRAnonymizer
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Global anonymizer instance (initialized once)
anonymizer = None

def initialize_anonymizer():
    """Initialize the anonymizer once at startup."""
    global anonymizer
    if anonymizer is None:
        logger.info("Initializing GDPR Anonymizer...")
        start_time = time.time()
        
        # Initialize with Slovenian language (can be made configurable)
        anonymizer = ComprehensiveGDPRAnonymizer(language='sl', use_gpu=False)
        
        init_time = time.time() - start_time
        logger.info(f"✓ Anonymizer initialized in {init_time:.2f} seconds")
    
    return anonymizer

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'GDPR Anonymizer API',
        'version': '1.0.0'
    })

@app.route('/anonymize', methods=['POST'])
def anonymize_text():
    """
    Anonymize text endpoint.
    
    Expected JSON payload:
    {
        "text": "Text to anonymize",
        "language": "sl",  # optional, default: "sl"
        "use_descriptive_masks": true,  # optional, default: false
        "preserve_types": ["LOC"]  # optional, default: []
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Missing required field: text'
            }), 400
        
        text = data['text']
        language = data.get('language', 'sl')
        use_descriptive_masks = data.get('use_descriptive_masks', False)
        preserve_types = data.get('preserve_types', [])
        
        # Validate text
        if not isinstance(text, str) or len(text.strip()) == 0:
            return jsonify({
                'error': 'Text must be a non-empty string'
            }), 400
        
        # Initialize anonymizer if needed
        anonymizer = initialize_anonymizer()
        
        # Process the text
        start_time = time.time()
        result = anonymizer.anonymize_text(
            text=text,
            use_descriptive_masks=use_descriptive_masks,
            preserve_types=preserve_types
        )
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'original_text': result['original_text'],
            'anonymized_text': result['anonymized_text'],
            'total_entities_masked': result['total_entities_masked'],
            'privacy_risk': result['privacy_risk'],
            'detection_methods': result['detection_methods'],
            'processing_time_seconds': round(processing_time, 3),
            'masked_entities': []
        }
        
        # Add masked entities (limit to first 10 for performance)
        for entity in result['masked_entities'][:10]:
            response['masked_entities'].append({
                'original': entity['original'],
                'type': entity['type'],
                'mask': entity['mask'],
                'detection_method': entity['detection_method'],
                'confidence': entity['confidence']
            })
        
        if len(result['masked_entities']) > 10:
            response['masked_entities'].append({
                'note': f"... and {len(result['masked_entities']) - 10} more entities"
            })
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/anonymize/batch', methods=['POST'])
def anonymize_batch():
    """
    Batch anonymize multiple texts.
    
    Expected JSON payload:
    {
        "texts": ["Text 1", "Text 2", "Text 3"],
        "language": "sl",  # optional, default: "sl"
        "use_descriptive_masks": true,  # optional, default: false
        "preserve_types": ["LOC"]  # optional, default: []
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'texts' not in data:
            return jsonify({
                'error': 'Missing required field: texts'
            }), 400
        
        texts = data['texts']
        language = data.get('language', 'sl')
        use_descriptive_masks = data.get('use_descriptive_masks', False)
        preserve_types = data.get('preserve_types', [])
        
        # Validate texts
        if not isinstance(texts, list) or len(texts) == 0:
            return jsonify({
                'error': 'Texts must be a non-empty list'
            }), 400
        
        # Initialize anonymizer if needed
        anonymizer = initialize_anonymizer()
        
        # Process all texts
        results = []
        total_processing_time = 0
        
        for i, text in enumerate(texts):
            if not isinstance(text, str) or len(text.strip()) == 0:
                results.append({
                    'index': i,
                    'error': 'Text must be a non-empty string'
                })
                continue
            
            try:
                start_time = time.time()
                result = anonymizer.anonymize_text(
                    text=text,
                    use_descriptive_masks=use_descriptive_masks,
                    preserve_types=preserve_types
                )
                processing_time = time.time() - start_time
                total_processing_time += processing_time
                
                results.append({
                    'index': i,
                    'original_text': result['original_text'],
                    'anonymized_text': result['anonymized_text'],
                    'total_entities_masked': result['total_entities_masked'],
                    'privacy_risk': result['privacy_risk'],
                    'processing_time_seconds': round(processing_time, 3)
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total_processing_time_seconds': round(total_processing_time, 3),
            'batch_size': len(texts)
        })
        
    except Exception as e:
        logger.error(f"Error processing batch request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/info', methods=['GET'])
def get_info():
    """Get information about the anonymizer capabilities."""
    return jsonify({
        'service': 'GDPR Anonymizer API',
        'version': '1.0.0',
        'capabilities': {
            'classla_ner': {
                'description': 'Natural language entity recognition',
                'supported_entities': ['PER', 'LOC', 'ORG', 'MISC'],
                'supported_languages': ['sl', 'hr', 'sr', 'bg', 'mk']
            },
            'google_phonenumbers': {
                'description': 'International phone number validation',
                'supported_formats': ['International', 'National', 'Mobile'],
                'validation': 'Luhn algorithm and country-specific rules'
            },
            'presidio_patterns': {
                'description': 'Microsoft Presidio regex patterns',
                'supported_types': ['EMAIL', 'CREDIT_CARD', 'IP_ADDRESS', 'DATE', 'URL', 'IBAN']
            },
            'regional_patterns': {
                'description': 'Country-specific sensitive data patterns',
                'supported_countries': {
                    'sl': ['EMŠO', 'Davčna številka', 'TRR', 'ID za DDV'],
                    'hr': ['OIB', 'ID za PDV'],
                    'sr': ['JMBG', 'PIB'],
                    'bg': ['EGN', 'VAT']
                }
            }
        },
        'masking_options': {
            'asterisk': 'Traditional asterisk masking (*)',
            'descriptive': 'Descriptive tags (<MASKED_EMAIL>, <MASKED_PHONE>, etc.)'
        }
    })

if __name__ == '__main__':
    # Initialize anonymizer at startup
    initialize_anonymizer()
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get('PORT', 8000))
    
    # Run the Flask app
    logger.info(f"Starting GDPR Anonymizer API server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False) 