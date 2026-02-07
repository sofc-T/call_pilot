# CallPilot: Revolutionizing African Digital Access via Native AI

## Executive Summary
**CallPilot** is a voice-first AI orchestration engine designed to bridge the gap between natural African languages and the global digital economy. By leveraging **Hasab.ai’s** localized speech models, CallPilot empowers users to interact with complex productivity tools—like Google Calendar and Email—using natural, conversational Amharic. This project addresses the critical "language barrier" that excludes millions of non-English speakers from participation in the formal digital sector.

## The Challenge: "Why Always English?"
The dominant digital infrastructure of the world is English-centric. For millions of entrepreneurs, traders, and service providers in Africa, the inability to speak English fluently equates to an inability to use basic digital organization tools. This digital divide stifles economic growth, limiting market access and operational efficiency for local businesses.

## The Solution: A Native-Speaking AI Receptionist
CallPilot dismantles this barrier by acting as an intelligent intermediary. It is not just a translation layer; it is an **action-oriented agent**.
*   **Voice-First Interface:** Users speak naturally in their mother tongue (Amharic).
*   **Context-Aware Automation:** The system parses intent (e.g., "Schedule a meeting with Abebe") and executes backend API calls.
*   **Hybrid Accessibility:** Supports both voice and text, allowing seamless interaction for users with varying levels of literacy and connectivity.

## Technical Architecture

The system is built on a robust Service-Oriented Architecture (SOA) optimized for reliability:

### 1. The Interaction Layer
*   **Frontend:** A lightweight, vanilla JavaScript client captures audio via the `MediaRecorder` API. It maintains conversation state via unique Session IDs, ensuring specific user contexts are preserved.
*   **Smart Input:** Users can switch between voice and text dynamically.

### 2. The Intelligence Core (Backend)
*   **FastAPI & Python:** Orchestrates the flow of data between the user, the AI models, and external services.
*   **Audio Pipeline:** `FFmpeg` normalizes disparate browser audio formats into standardized MP3s strictly compliant with Hasab's input requirements.
*   **Brain Service:** An advanced logic module that utilizes sliding-window context management (Memory) and engineered system prompts (Persona) to prevent hallucinations and ensure accurate intent extraction.

### 3. Integration & Action
*   **Hasab.ai Ecosystem:** Powers the STT (Speech-to-Text), LLM (Language Logic), and TTS (Text-to-Speech) specifically tuned for Ethiopian languages.
*   **Calendar Automation:** A custom Google OAuth implementation creates real-time calendar events (with `.ics` invites) based on recognized intents, handling timezone conversions and attendee management automatically.

## Impact & Vision
CallPilot is an infrastructure for inclusion. By enabling a user to say *“Book a meeting”* in Amharic and have the system handle the complex API interactions, we are converting technological complexity into accessible utility. This prototype lays the groundwork for scaling to other African languages, creating a future where technology adapts to the people, rather than people forcing themselves to adapt to the technology.