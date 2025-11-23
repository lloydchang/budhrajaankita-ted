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

def test_single_endpoint(endpoint, data, description):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=120  # Increased timeout
        )
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            response_text = response.text
            print(f"Response Length: {len(response_text)} characters")
            print(f"Response Preview: {response_text[:300]}...")
            return True
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

# Test each endpoint individually with user confirmation
print("\n" + "="*60)
print("INDIVIDUAL API ENDPOINT TESTING")
print("Testing with 15-second delays to avoid rate limiting")
print("="*60)

endpoints_to_test = [
    ("/investors", "Get Investors Information"),
    ("/grantInfo", "Get Grant Information"),
    ("/getGrantProposal", "Generate Grant Proposal"),
    ("/generatePitchText", "Generate Pitch Text"),
    ("/business_plan_roadmap", "Generate Business Plan Roadmap"),
]

results = {}

for endpoint, description in endpoints_to_test:
    success = test_single_endpoint(endpoint, {"idea": test_idea}, description)
    results[endpoint] = success
    print(f"\nWaiting 15 seconds before next test to avoid rate limiting...")
    time.sleep(15)

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

successful = sum(1 for v in results.values() if v)
total = len(results)

print(f"\nSuccess Rate: {successful}/{total} ({successful/total*100:.1f}%)")
print("\nDetailed Results:")
for endpoint, success in results.items():
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"  {status} - {endpoint}")

print("\n" + "="*60)
print("TESTING COMPLETE")
print("="*60)
