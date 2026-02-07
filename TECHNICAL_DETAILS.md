onep# CallPilot: Technical Architecture & Implementation Details

## System Overview
CallPilot is a hybrid voice-first AI orchestration engine designed to bridge the gap between natural African languages (specifically Amharic) and structured digital productivity tools. The system utilizes a **FastAPI** backend to mediate between a vanilla JavaScript frontend, **Hasab.ai’s** cognitive services, and the **Google Workspace** ecosystem.

## Technology Stack
*   **Backend Runtime:** Python 3.13
*   **Web Framework:** FastAPI (Asynchronous) served via Uvicorn
*   **Frontend:** HTML5, CSS3 (Flexbox/Animations), Vanilla JavaScript (ES6+), MediaRecorder API
*   **AI Provider:** Hasab.ai (STT, LLM, TTS)
*   **Infrastructure:** Linux (Fedora environment), FFmpeg audio processing

## Core Architecture Design

### 1. The Interaction Layer (Frontend)
The client application is built without heavy frameworks to ensure performance on low-end devices.
*   **Audio Capture:** Uses the browser's `MediaRecorder` API to capture standard `audio/webm`.
*   **State Management:** Generates and persist a unique `session_id` to maintain conversation context across HTTP requests.
*   **Hybrid Input:** Supports seamless switching between voice recording and text input, harmonizing them into a single chat stream.

### 2. The Orchestration Layer (Backend)
The Python backend uses a modular Service-Oriented Architecture (SOA):

*   **`services/transcriber.py` (The Ear):**
    *   **Audio Normalization:** Intercepts browser WEBM uploads and uses `ffmpeg` via subprocess to convert them to standardized 44.1kHz mono MP3s, ensuring compatibility with Hasab's strict input requirements.
    *   **WAF Bypass:** Implements custom `User-Agent` headers to successfully negotiate with Hasab's LiteSpeed servers, preventing 403 Forbidden errors.

*   **`services/brain.py` (The Cortex):**
    *   **Context Window:** Maintains an in-memory sliding window (last 10 turns) of conversation history keyed by `session_id`.
    *   **Intent Recognition:** Uses a system prompt engineering strategy to force the LLM into a "Receptionist" persona.
    *   **Action Parsing:** Implements a dual-strategy parser (Strict Regex `[Name] [Email]` + Fallback Heuristics) to reliably extract structured booking data from unstructured natural language responses.

*   **`services/voice.py` (The Mouth):**
    *   Sends text responses to Hasab's TTS engine using the `amh` (Amharic) language code.
    *   Implements UUID-based file naming (`response_{uuid}.mp3`) to defeat aggressive browser audio caching.

### 3. The Integration Layer (External)
*   **Google Calendar:** The system implements a robust OAuth 2.0 flow (`credentials.json` -> `token.json`). When a booking intent is confirmed, it constructs an API payload injecting the user's email as an attendee and the host's email (configurable via `HOST_EMAIL`) as a supervisor, creating a real-time calendar event.

## Data Flow Pipeline
1.  **Ingest:** User audio -> generic WEBM -> Server-side FFmpeg -> MP3.
2.  **Transcribe:** MP3 -> Hasab API (field: `audio`) -> Amharic Text.
3.  **Process:** Text + History -> LLM -> Response Text + `ACTION: BOOK_MEETING` tag.
4.  **Execute:** Regex Parse -> Google Calendar API (`events.insert`).
5.  **Synthesize:** Response Text -> Hasab TTS -> MP3 Audio.
6.  **deliver:** Audio URL + Transcript JSON -> Frontend Playback & UI Update.