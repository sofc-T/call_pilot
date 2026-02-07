import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from services.process import process_conversation, process_text
from services.calendar import HOST_EMAIL

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatInput(BaseModel):
    text: str
    session_id: str = "default"

@app.get("/config")
def get_config():
    return {"host_email": HOST_EMAIL}

@app.post("/chat")
async def chat(input: ChatInput):
    response_audio_path, user_text, ai_text = await process_text(input.text, input.session_id)
    
    if response_audio_path is None:
        return {"user_text": user_text, "ai_text": ai_text, "error": "AI could not generate audio"}

    return {
        "user_text": user_text,
        "ai_text": ai_text,
        "audio_url": f"/static/audio/{os.path.basename(response_audio_path)}"
    }

@app.post("/talk")
async def talk(file: UploadFile = File(...), session_id: str = Form("default")):
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # We are passing the local filename again
        response_audio_path, user_text, ai_text = await process_conversation(temp_filename, session_id)
        
        if response_audio_path is None:
            return {"user_text": user_text, "ai_text": ai_text, "error": "AI could not generate audio"}

        return {
            "user_text": user_text,
            "ai_text": ai_text,
            "audio_url": f"/static/audio/{os.path.basename(response_audio_path)}"
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)