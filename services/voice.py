import os
import requests

def synthesize_speech(text, output_path):
    # Matches your provided doc: /v1/tts/synthesize
    base_url = os.getenv("HASAB_BASE_URL")
    url = f"{base_url}/tts/synthesize"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('HASAB_API_KEY')}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    payload = {
        "text": text,
        "language": "amh",
        "speaker_name": "yared" # This is a valid speaker from your doc
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"TTS Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"TTS Exception: {e}")
        return False