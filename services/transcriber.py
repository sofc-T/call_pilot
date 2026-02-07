import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_file_path):
    api_key = os.getenv("HASAB_API_KEY")
    base_url = os.getenv("HASAB_BASE_URL")
    url = f"{base_url}/upload-audio"

    if not api_key:
        print("Error: HASAB_API_KEY not found.")
        return None

    converted_path = None
    upload_path = audio_file_path
    mime_type = "audio/mpeg"

    # Convert WEBM to MP3 because Hasab API supports MP3, WAV, M4A
    if audio_file_path.endswith(".webm"):
        try:
            converted_path = audio_file_path.replace(".webm", ".mp3")
            print(f"Converting {audio_file_path} to {converted_path}...")
            subprocess.run([
                "ffmpeg", "-i", audio_file_path, 
                "-vn", "-ar", "44100", "-ac", "1", "-b:a", "128k", 
                converted_path, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            upload_path = converted_path
            mime_type = "audio/mpeg"
        except Exception as e:
            print(f"Conversion Error: {e}")
            # Try sending original if conversion fails, though it might fail API validation
            pass

    try:
        print(f"Sending file to Hasab via {url}...")
        
        with open(upload_path, "rb") as audio_file:
            # Correct field name is 'audio' (despite docs saying 'file')
            files = {
                "audio": (os.path.basename(upload_path), audio_file, mime_type)
            }
            data = {
                "transcribe": "true",
                "language": "auto" 
            }
            # Add User-Agent to mimic browser and bypass 403 Forbidden
            headers = {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                transcription = result.get("transcription", "")
                if not transcription:
                    # Fallback: sometimes empty string is returned if audio is silent
                    print(f"STT Warning: Transcription is empty. Valid response: {result}")
                return transcription
            else:
                print(f"STT Error: {response.status_code} - {response.text[:200]}")
                return None
                
    except Exception as e:
        print(f"STT Exception: {e}")
        return None
    finally:
        # Cleanup converted file
        if converted_path and os.path.exists(converted_path):
            os.remove(converted_path)