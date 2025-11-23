import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

# Sample test data
test_idea = {
    "name": "Clean Water Initiative",
    "mission": "Provide clean drinking water to underserved communities",
    "goals": [
        "Install 100 water filtration systems",
        "Train local communities on water safety",
        "Reduce waterborne diseases by 50%"
    ],
    "targetMarket": {
        "region": "Sub-Saharan Africa",
        "demographics": "Rural communities without access to clean water",
        "size": "10,000 people"
    },
    "primaryProduct": "Community water filtration systems",
    "sdgs": ["SDG 6: Clean Water and Sanitation", "SDG 3: Good Health and Well-being"]
}

def test_endpoint(endpoint, data, description, delay=5):
    """Test a single endpoint and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            print(f"Response preview: {response.text[:200]}...")
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
    
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    # Add delay before next request to avoid rate limiting
    if delay > 0:
        print(f"Waiting {delay} seconds before next test...")
        time.sleep(delay)

# Test all endpoints
print("\n" + "="*60)
print("TESTING ALL API ENDPOINTS")
print("="*60)

# 1. Test /investors
test_endpoint(
    "/investors",
    {"idea": test_idea},
    "Get Investors Information",
    delay=8
)

# 2. Test /grantInfo
test_endpoint(
    "/grantInfo",
    {"idea": test_idea},
    "Get Grant Information",
    delay=8
)

# 3. Test /getGrantProposal
test_endpoint(
    "/getGrantProposal",
    {"idea": test_idea},
    "Generate Grant Proposal",
    delay=8
)

# 4. Test /generatePitchText
test_endpoint(
    "/generatePitchText",
    {"idea": test_idea},
    "Generate Pitch Text",
    delay=8
)

# 5. Test /generatePitchAudio
# First generate pitch text, then use it for audio
print(f"\n{'='*60}")
print("Testing: Generate Pitch Audio")
print(f"Endpoint: POST /generatePitchAudio")
print(f"{'='*60}")
print("Note: This requires pitch text from previous endpoint")

sample_pitch = "Welcome to our Clean Water Initiative. We're on a mission to provide clean drinking water to underserved communities in Sub-Saharan Africa."

try:
    response = requests.post(
        f"{BASE_URL}/generatePitchAudio",
        json={"pitch_text": sample_pitch},
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS")
        print(f"Audio file generated successfully")
    else:
        print("❌ FAILED")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ EXCEPTION: {str(e)}")

print(f"Waiting 8 seconds before next test...")
time.sleep(8)

# 6. Test /business_plan_roadmap
test_endpoint(
    "/business_plan_roadmap",
    {"idea": test_idea},
    "Generate Business Plan Roadmap",
    delay=0  # Last test, no delay needed
)

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)

