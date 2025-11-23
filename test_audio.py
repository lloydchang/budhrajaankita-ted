import requests
import time

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("TESTING AUDIO GENERATION ENDPOINT")
print("="*60)

# Sample pitch text
sample_pitch = """Imagine a world where every community has access to clean drinking water, 
a fundamental human right yet a luxury for millions in Sub-Saharan Africa. 
Our Clean Water Initiative is dedicated to making this a reality for rural communities 
without access to clean water."""

print(f"\nPitch Text Length: {len(sample_pitch)} characters")
print(f"Pitch Text Preview: {sample_pitch[:100]}...")

try:
    print("\nSending request to /generatePitchAudio...")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/generatePitchAudio",
        json={"pitch_text": sample_pitch},
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    
    elapsed = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Audio generated!")
        print(f"Content Type: {response.headers.get('content-type')}")
        print(f"Content Length: {len(response.content)} bytes")
        
        # Save the audio file
        with open("test_pitch_audio.wav", "wb") as f:
            f.write(response.content)
        print("✅ Audio saved to: test_pitch_audio.wav")
    else:
        print("❌ FAILED")
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ EXCEPTION: {str(e)}")

print("\n" + "="*60)
print("AUDIO TEST COMPLETE")
print("="*60)
