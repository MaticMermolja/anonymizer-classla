#!/usr/bin/env python3
"""
Simple test for the Railway API without CLASSLA initialization
"""

import requests
import json

# Your Railway API URL
API_BASE_URL = "https://anonymizer-classla-production.up.railway.app"

def test_simple_endpoint():
    """Test the simple endpoint that doesn't require CLASSLA"""
    print("🧪 Testing Simple Endpoint (no CLASSLA required)...")
    
    test_text = "Hello, my email is test@example.com and phone is +386 31 123 456."
    
    payload = {
        "text": test_text
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/test-simple",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Original: {result['original_text']}")
            print(f"✅ Anonymized: {result['anonymized_text']}")
            print(f"📊 Entities masked: {result['total_entities_masked']}")
            print(f"⚠️  Privacy risk: {result['privacy_risk']}")
            print(f"⏱️  Processing time: {result['processing_time_seconds']}s")
            print(f"📝 Note: {result['note']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_status():
    """Check if CLASSLA is initialized"""
    print("\n🔍 Checking CLASSLA Status...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            status = data.get('anonymizer_status', 'unknown')
            print(f"CLASSLA Status: {status}")
            return status == 'initialized'
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Railway API - Simple Endpoint")
    print("=" * 50)
    
    # Test simple endpoint first
    simple_ok = test_simple_endpoint()
    
    # Check CLASSLA status
    classla_ready = test_health_status()
    
    if simple_ok:
        print("\n✅ Simple endpoint works! Basic functionality is available.")
    else:
        print("\n❌ Simple endpoint failed.")
    
    if classla_ready:
        print("✅ CLASSLA is initialized and ready for full anonymization.")
    else:
        print("⏳ CLASSLA is not yet initialized. Full anonymization will take time on first request.")
    
    print("\n💡 Tip: The simple endpoint works immediately, while full CLASSLA anonymization")
    print("   will be available after the first request (may take 1-2 minutes to initialize).") 