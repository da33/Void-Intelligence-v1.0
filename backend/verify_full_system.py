import requests
import os
import time

# Create a dummy MP3 file for testing (minimal valid MP3 header)
def create_dummy_mp3(filename):
    # Minimal MP3 frame (MPEG 1 Layer 3, 32kbps, 44100Hz, single frame)
    # This might be too short for some transcoders, but let's try.
    # Alternatively, just use a text file and let the backend error handler catch it 
    # but we want to test success path.
    # Let's use a dummy text file renamed as mp3 for now, 
    # as we just want to see if it reaches the "Transcoding" step in the logs.
    # But wait, the backend runs ffmpeg. 
    # Let's try to create a valid empty file.
    with open(filename, 'wb') as f:
        f.write(b'\xFF\xFB\x90\xC4\x00\x00\x00\x00') # Fake MP3 header

def test_backend_logic():
    url = "http://localhost:8000/api/record"
    filename = "test_audio.webm"
    
    # 1. Create Dummy File
    create_dummy_mp3(filename)
    print(f"Created test file: {filename}")

    # 2. Prepare Request
    files = {'file': (filename, open(filename, 'rb'), 'audio/webm')}
    data = {'mode': 'note'}

    print(f"Sending request to {url}...")
    try:
        # Note: This might fail at transcoding since it's fake data, 
        # BUT the goal is to reach the backend and see how it reacts.
        # If it returns 500 (transcode fail) that means it REACHED the backend.
        # If it returns 404/405, connectivity is wrong.
        res = requests.post(url, files=files, data=data)
        
        print("\n=== Response ===")
        print(f"Status Code: {res.status_code}")
        try:
            print(res.json())
        except:
            print(res.text)
            
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure backend is running locally on port 8000.")

    # Cleanup
    if os.path.exists(filename):
        os.remove(filename)

if __name__ == "__main__":
    test_backend_logic()
