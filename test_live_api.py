#!/usr/bin/env python3
"""
Test script for the live Railway GDPR Anonymizer API
"""

import requests
import json
import time

# Your Railway API URL
API_BASE_URL = "https://anonymizer-classla-production.up.railway.app"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing Root Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_anonymization(text, use_descriptive_masks=True):
    """Test the anonymization endpoint"""
    print(f"\n🔒 Testing Anonymization (descriptive={use_descriptive_masks})...")
    print(f"Input: {text}")
    
    payload = {
        "text": text,
        "use_descriptive_masks": use_descriptive_masks
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/anonymize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        processing_time = time.time() - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Anonymized: {result['anonymized_text']}")
            print(f"📊 Entities masked: {result['total_entities_masked']}")
            print(f"⚠️  Privacy risk: {result['privacy_risk']}")
            print(f"🔍 Detection methods: {result['detection_methods']}")
        else:
            print(f"❌ Error: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Anonymization failed: {e}")
        return False

def test_info_endpoint():
    """Test the info endpoint"""
    print("\nℹ️  Testing Info Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/info")
        print(f"Status: {response.status_code}")
        info = response.json()
        print(f"Service: {info['service']}")
        print(f"Version: {info['version']}")
        print(f"Capabilities: {list(info['capabilities'].keys())}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Info endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Live Railway GDPR Anonymizer API")
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health_check()
    root_ok = test_root_endpoint()
    info_ok = test_info_endpoint()
    
    if not all([health_ok, root_ok, info_ok]):
        print("\n❌ Basic endpoints failed. Stopping tests.")
        return
    
    # Test anonymization with different scenarios
    test_cases = [
        # Slovenian text with personal data
        "Pozdravljen, jaz sem Janez Novak iz Ljubljane. Moj email je janez.novak@email.com in telefon +386 31 123 456.",
        
        # English text with sensitive data
        "Hello, I'm John Smith from London. My email is john.smith@company.com and phone is +44 20 7946 0958.",
        
        # Text with credit card and other sensitive data
        "My credit card number is 4532 1234 5678 9012 and my IBAN is SI56 1910 0000 0123 438.",
        
        # Text with dates and IDs
        "I was born on 15.03.1985, my EMŠO is 1503850500999 and my tax number is 12345678."
    ]
    
    print("\n🧪 Testing Anonymization Scenarios...")
    for i, text in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        success = test_anonymization(text, use_descriptive_masks=True)
        if success:
            # Also test with asterisk masking
            test_anonymization(text, use_descriptive_masks=False)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 