#!/usr/bin/env python3
"""
Test script for multi-provider LLM setup
Tests both Google Gemini and OpenRouter providers
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the provider functions
from main import call_gemini_api, call_openrouter_api, call_cloudflare_api, make_openrouter_request

def test_gemini():
    """Test Google Gemini API directly"""
    print("\n" + "="*60)
    print("Testing Google Gemini API")
    print("="*60)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not configured - skipping test")
        return False
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}
        ]
        
        print("📤 Sending test request to Gemini...")
        result = call_gemini_api(messages)
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Gemini response: {content}")
            return True
        else:
            print("❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ Gemini test failed: {str(e)}")
        return False


def test_openrouter():
    """Test OpenRouter API directly"""
    print("\n" + "="*60)
    print("Testing OpenRouter API")
    print("="*60)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not configured - skipping test")
        return False
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from OpenRouter!' and nothing else."}
        ]
        
        print("📤 Sending test request to OpenRouter...")
        result = call_openrouter_api(messages, max_retries=1)
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"✅ OpenRouter response: {content}")
            return True
        else:
            print("❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ OpenRouter test failed: {str(e)}")
        return False


def test_cloudflare():
    """Test Cloudflare Workers AI directly"""
    print("\n" + "="*60)
    print("Testing Cloudflare Workers AI")
    print("="*60)
    
    if not os.getenv("CLOUDFLARE_API_KEY"):
        print("❌ CLOUDFLARE_API_KEY not configured - skipping test")
        return False
    
    if not os.getenv("CLOUDFLARE_ACCOUNT_ID"):
        print("❌ CLOUDFLARE_ACCOUNT_ID not configured - skipping test")
        return False
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Cloudflare!' and nothing else."}
        ]
        
        print("📤 Sending test request to Cloudflare...")
        result = call_cloudflare_api(messages, max_retries=1)
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Cloudflare response: {content}")
            return True
        else:
            print("❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ Cloudflare test failed: {str(e)}")
        return False


def test_multi_provider():
    """Test the multi-provider fallback system"""
    print("\n" + "="*60)
    print("Testing Multi-Provider Fallback System")
    print("="*60)
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from multi-provider!' and nothing else."}
        ]
        
        print("📤 Sending test request through multi-provider system...")
        result = make_openrouter_request(messages, endpoint_name="test_multi_provider", use_cache=False)
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Multi-provider response: {content}")
            return True
        else:
            print("❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"❌ Multi-provider test failed: {str(e)}")
        return False


def test_caching():
    """Test that caching works correctly"""
    print("\n" + "="*60)
    print("Testing Cache System")
    print("="*60)
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from cache test!' and nothing else."}
        ]
        
        print("📤 First request (should hit API)...")
        result1 = make_openrouter_request(messages, endpoint_name="test_cache", use_cache=True)
        
        print("📤 Second request (should hit cache)...")
        result2 = make_openrouter_request(messages, endpoint_name="test_cache", use_cache=True)
        
        if result1 == result2:
            print("✅ Cache working correctly - both responses match")
            return True
        else:
            print("❌ Cache not working - responses differ")
            return False
            
    except Exception as e:
        print(f"❌ Cache test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🧪 " + "="*58)
    print("🧪 Multi-Provider LLM Test Suite")
    print("🧪 " + "="*58)
    
    # Check which API keys are configured
    print("\n📋 Configuration Check:")
    print(f"   GEMINI_API_KEY: {'✅ Configured' if os.getenv('GEMINI_API_KEY') else '❌ Not configured'}")
    print(f"   OPENROUTER_API_KEY: {'✅ Configured' if os.getenv('OPENROUTER_API_KEY') else '❌ Not configured'}")
    print(f"   CLOUDFLARE_API_KEY: {'✅ Configured' if os.getenv('CLOUDFLARE_API_KEY') else '❌ Not configured'}")
    print(f"   CLOUDFLARE_ACCOUNT_ID: {'✅ Configured' if os.getenv('CLOUDFLARE_ACCOUNT_ID') else '❌ Not configured'}")
    
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("OPENROUTER_API_KEY") and not os.getenv("CLOUDFLARE_API_KEY"):
        print("\n❌ ERROR: No API keys configured!")
        print("   Please add at least one of: GEMINI_API_KEY, OPENROUTER_API_KEY, or CLOUDFLARE_API_KEY to your .env file")
        sys.exit(1)
    
    # Run tests
    results = {
        "Gemini API": test_gemini(),
        "OpenRouter API": test_openrouter(),
        "Cloudflare Workers AI": test_cloudflare(),
        "Multi-Provider System": test_multi_provider(),
        "Cache System": test_caching()
    }
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    # Calculate pass rate
    total_tests = len([r for r in results.values() if r is not False])
    passed_tests = sum(1 for r in results.values() if r is True)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
