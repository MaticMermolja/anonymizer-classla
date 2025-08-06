#!/usr/bin/env python3
"""
Test script for Docker API

This script demonstrates how to use the GDPR Anonymizer Docker API.
Run this after starting the Docker container.
"""

import requests
import json
import time

# API base URL (adjust if running on different port)
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing Health Check")
    print("=" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health check error: {e}")
    
    print()

def test_info_endpoint():
    """Test the info endpoint."""
    print("ℹ️ Testing Info Endpoint")
    print("=" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/info")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Service: {data['service']}")
            print(f"✓ Version: {data['version']}")
            print("✓ Capabilities:")
            for capability, info in data['capabilities'].items():
                print(f"  - {capability}: {info['description']}")
        else:
            print(f"✗ Info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Info endpoint error: {e}")
    
    print()

def test_single_anonymization():
    """Test single text anonymization."""
    print("📝 Testing Single Text Anonymization")
    print("=" * 40)
    
    test_text = "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678, rojena 20.5.1980, EMŠO: 2005800500999"
    
    # Test with asterisk masking
    payload = {
        "text": test_text,
        "language": "sl",
        "use_descriptive_masks": False
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/anonymize", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Original: {data['original_text']}")
            print(f"Asterisk masked: {data['anonymized_text']}")
            print(f"Entities masked: {data['total_entities_masked']}")
            print(f"Privacy risk: {data['privacy_risk']}")
            print(f"Processing time: {data['processing_time_seconds']}s")
        else:
            print(f"✗ Anonymization failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Anonymization error: {e}")
    
    print()

def test_descriptive_masking():
    """Test descriptive masking."""
    print("🏷️ Testing Descriptive Masking")
    print("=" * 40)
    
    test_text = "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678, rojena 20.5.1980, EMŠO: 2005800500999"
    
    # Test with descriptive masking
    payload = {
        "text": test_text,
        "language": "sl",
        "use_descriptive_masks": True
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/anonymize", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Original: {data['original_text']}")
            print(f"Descriptive masked: {data['anonymized_text']}")
            print(f"Entities masked: {data['total_entities_masked']}")
            print(f"Privacy risk: {data['privacy_risk']}")
            print(f"Processing time: {data['processing_time_seconds']}s")
            
            print("\nMasked entities:")
            for entity in data['masked_entities']:
                print(f"  - {entity['original']} ({entity['type']}) → {entity['mask']} [{entity['detection_method']}]")
        else:
            print(f"✗ Descriptive masking failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Descriptive masking error: {e}")
    
    print()

def test_batch_anonymization():
    """Test batch anonymization."""
    print("📦 Testing Batch Anonymization")
    print("=" * 40)
    
    test_texts = [
        "Janez Novak (janez@email.com) živi v Ljubljani, telefon: 031 123 456",
        "Ana Horvat iz Zagreba, tel: +385 1 234 5678, OIB: 12345678901",
        "Contact: john.smith@microsoft.com, phone: +1 (555) 123-4567, credit card: 4111 1111 1111 1111"
    ]
    
    payload = {
        "texts": test_texts,
        "language": "sl",
        "use_descriptive_masks": True
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/anonymize/batch", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Batch size: {data['batch_size']}")
            print(f"Total processing time: {data['total_processing_time_seconds']}s")
            
            for result in data['results']:
                print(f"\nText {result['index']}:")
                print(f"  Original: {result['original_text']}")
                print(f"  Anonymized: {result['anonymized_text']}")
                print(f"  Entities: {result['total_entities_masked']}")
                print(f"  Risk: {result['privacy_risk']}")
                print(f"  Time: {result['processing_time_seconds']}s")
        else:
            print(f"✗ Batch anonymization failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Batch anonymization error: {e}")
    
    print()

def test_preserve_types():
    """Test preserving specific entity types."""
    print("🔒 Testing Preserve Types")
    print("=" * 40)
    
    test_text = "Dr. Ana Horvat (ana.horvat@gmail.com) iz Ljubljane, tel: +386 1 234 5678"
    
    # Test preserving locations
    payload = {
        "text": test_text,
        "language": "sl",
        "use_descriptive_masks": True,
        "preserve_types": ["LOC"]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/anonymize", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"Original: {data['original_text']}")
            print(f"Anonymized (preserving LOC): {data['anonymized_text']}")
            print(f"Entities masked: {data['total_entities_masked']}")
            print(f"Privacy risk: {data['privacy_risk']}")
        else:
            print(f"✗ Preserve types test failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"✗ Preserve types test error: {e}")
    
    print()

def main():
    """Run all tests."""
    print("🚀 GDPR Anonymizer Docker API Test Suite")
    print("=" * 60)
    print("Make sure the Docker container is running on port 8000")
    print("=" * 60)
    
    # Wait a moment for the container to be ready
    print("⏳ Waiting for container to be ready...")
    time.sleep(2)
    
    # Run all tests
    test_health_check()
    test_info_endpoint()
    test_single_anonymization()
    test_descriptive_masking()
    test_batch_anonymization()
    test_preserve_types()
    
    print("🎉 All tests completed!")
    print("\n📋 Usage Examples:")
    print("1. Single anonymization:")
    print("   curl -X POST http://localhost:8000/anonymize \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"text\": \"Your text here\", \"use_descriptive_masks\": true}'")
    print()
    print("2. Batch anonymization:")
    print("   curl -X POST http://localhost:8000/anonymize/batch \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"texts\": [\"Text 1\", \"Text 2\"], \"use_descriptive_masks\": true}'")

if __name__ == "__main__":
    main() 