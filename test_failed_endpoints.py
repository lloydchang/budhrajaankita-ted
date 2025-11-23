import requests
import time

BASE_URL = "http://127.0.0.1:8000"

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

print("\n" + "="*60)
print("RE-TESTING FAILED ENDPOINTS")
print("Testing with 30-second delays")
print("="*60)

failed_endpoints = [
    ("/getGrantProposal", "Generate Grant Proposal"),
    ("/business_plan_roadmap", "Generate Business Plan Roadmap"),
]

results = {}

for endpoint, description in failed_endpoints:
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Endpoint: POST {endpoint}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json={"idea": test_idea},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            print(f"Response Length: {len(response.text)} characters")
            print(f"Response Preview: {response.text[:300]}...")
            results[endpoint] = True
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            results[endpoint] = False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        results[endpoint] = False
    
    print(f"\nWaiting 30 seconds before next test...")
    time.sleep(30)

print("\n" + "="*60)
print("RE-TEST SUMMARY")
print("="*60)

for endpoint, success in results.items():
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {endpoint}")

print("\n" + "="*60)
