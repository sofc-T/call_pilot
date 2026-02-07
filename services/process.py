import os
import requests
import uuid
import re
from pathlib import Path
from dotenv import load_dotenv

from services.transcriber import transcribe_audio
from services.voice import synthesize_speech
from services.calendar import schedule_event 

load_dotenv()

AUDIO_DIR = Path("static/audio")
AUDIO_DIR.mkdir(exist_ok=True)

# In-Memory Conversation Store
# Structure: { session_id: [ {"role": "user", "content": "..."}, ... ] }
CONVERSATIONS = {}

def get_chat_response(session_id, user_text):
    api_key = os.getenv("HASAB_API_KEY")
    base_url = os.getenv("HASAB_BASE_URL")
    url = f"{base_url}/chat"

    headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Retrieve History
    history = CONVERSATIONS.get(session_id, [])
    history.append({"role": "user", "content": user_text})
    
    # Construct System Prompt / Context
    # Since specific Hasab model capability is unknown, we inject instructions into the message stream or as a system prefix
    system_instruction = """
You are a helpful AI receptionist for CallPilot. 
Your goal is to schedule a meeting. 
You MUST ask for the user's Name and Email before booking.
If the user wants to book, and provides Name and Email, reply exactly with: "ACTION: BOOK_MEETING [Name] [Email]"
Otherwise, respond naturally to the user.
Keep responses short and conversational.
"""
    
    # Format Prompt: System + History + Latest
    # If the API only supports a single string 'message', we construct a transcript.
    transcript = f"{system_instruction}\n\nConversation History:\n"
    for msg in history[-10:]: # Keep last 10 turns
        transcript += f"{msg['role'].title()}: {msg['content']}\n"
    
    transcript += f"User: {user_text}\nAI:"

    payload = {
        "message": transcript,
        "model": "hasab-1-main"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            ai_content = data.get("message", {}).get("content", "I am sorry, I could not understand that.")
            
            # Save AI response to history
            history.append({"role": "ai", "content": ai_content})
            CONVERSATIONS[session_id] = history
            
            return ai_content
        else:
            print(f"Chat Error: {response.status_code} - {response.text}")
            return "I am experiencing some trouble thinking right now."
    except Exception as e:
        print(f"Chat Exception: {e}")
        return "I am having trouble connecting to my brain."

async def process_text(user_text, session_id="default"):
    # 2. BRAIN (Chat)
    raw_response = get_chat_response(session_id, user_text)
    
    # Check for Booking Action
    if "ACTION: BOOK_MEETING" in raw_response:
        # Extract details
        try:
            name = None
            email = None

            # Strategy 1: Look for brackets [Name] [Email]
            matches = re.findall(r"\[(.*?)\]", raw_response)
            if len(matches) >= 2:
                name = matches[0]
                email = matches[1]

            # Strategy 2: Relaxed parsing if brackets failed
            if not name or not email:
                # Remove the command prefix
                clean_content = raw_response.replace("ACTION: BOOK_MEETING", "").strip()
                # Try to find an email address
                email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", clean_content)
                if email_match:
                    email = email_match.group(0)
                    # Assume name is everything before the email (cleaning up brackets if any remain and are valid)
                    possible_name = clean_content.split(email)[0].strip()
                    name = re.sub(r"[\[\]]", "", possible_name).strip()

            if name and email:
                # Perform Booking
                schedule_event(f"Meeting with {name}", description=f"Booked via CallPilot AI. Contact: {email}", attendee_email=email)
                
                # Cleanup response for user
                ai_response_text = f"I have scheduled the meeting for you, {name}. I sent an invite to {email}."
            else:
                ai_response_text = "I tried to book the meeting, but I missed the exact details. Could you please confirm your name and email again?"
        except Exception as e:
            print(f"Booking Parse Error: {e}")
            ai_response_text = "I encountered an error while accessing the calendar."
    else:
        ai_response_text = raw_response

    # 3. MOUTH (Text to Speech)
    # Use unique filename to prevent browser caching issues
    unique_filename = f"response_{uuid.uuid4().hex[:8]}.mp3"
    speech_file_path = AUDIO_DIR / unique_filename
    
    success = synthesize_speech(ai_response_text, speech_file_path)

    if success:
        return speech_file_path, user_text, ai_response_text
    else:
        return None, user_text, ai_response_text

async def process_conversation(audio_file_path, session_id="default"):
    # 1. EAR (Speech to Text)
    user_text = transcribe_audio(audio_file_path)
    
    if not user_text:
        return None, "Error", "The STT service did not return any text."

    # Process text using the shared logic
    return await process_text(user_text, session_id)