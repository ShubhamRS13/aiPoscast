# 🎙️ AI Podcast Generator: Project Documentation 🎙️

Version: 1.0.0
Date: 07/05/2025
Author(s): Shubham Shinde

## 1. Project Overview

The AI Podcast Generator is a full-stack web application that empowers users to create short, engaging podcasts from a simple topic input. It leverages cutting-edge AI for script generation (Google Gemini) and multi-voice audio synthesis (ElevenLabs). The application features a two-step process: first generating a conversational script between a Host and a Guest, and then rendering that script into a combined audio file with distinct voices for each speaker.

### Core Features:

Topic-to-Script Generation: Users input a topic.

AI-Powered Scriptwriting: Google Gemini generates a structured, conversational script (approx. 3-4 minutes, ~500 words) with distinct "Host" and "Guest" roles.

Script Display: The generated script is presented to the user for review.

Multi-Voice Audio Synthesis:

Fixed female voice (ElevenLabs) for the Host.

Fixed male voice (ElevenLabs) for the Guest.

Individual audio segments are generated and seamlessly concatenated.

Audio Playback: An integrated HTML5 audio player allows users to listen to the generated podcast.

User-Friendly Interface: Built with React and Vite for a responsive experience.

Robust Backend: Python FastAPI backend orchestrates AI service calls and audio processing.

## 2. Architecture

The application follows a client-server architecture:

Frontend (Client-Side): A React single-page application (SPA) built with Vite. It handles user input, displays results, and interacts with the backend API.

Backend (Server-Side): A Python API built with FastAPI. It manages:

Communication with the Google Gemini API for script generation.

Communication with the ElevenLabs API for text-to-speech (TTS) synthesis.

Parsing of the generated script into speaker segments.

Concatenation of individual audio segments into a single podcast file using pydub.

Serving API endpoints for the frontend.

### Technology Stack:

### Frontend:

Framework/Library: React (with JavaScript + SWC via Vite)

Build Tool: Vite

HTTP Client: fetch API (built-in)

Styling: Plain CSS

### Backend:

Framework: FastAPI (Python)

AI - Script Generation: Google Gemini API (via google-generativeai SDK)

AI - Voice Synthesis: ElevenLabs API (via elevenlabs SDK)

Audio Processing: pydub (requires ffmpeg system dependency)

Environment Variables: python-dotenv

ASGI Server (for development): Uvicorn

### Version Control: Git & GitHub

## Diagrammatic Flow (High-Level): 
### (for proper visibility see it in vs code or in code format)

User (Browser - React Frontend)
    |
    1. Enters Topic, Clicks "Generate Script"
    |
    v
Backend API (FastAPI - Python) --- /api/generate-script ---> Google Gemini API
    |                                                           | (Generates Script Text)
    <---------------------------- (Returns JSON: {raw_script, segments}) <--- (Parses Script)
    |
Frontend
    |
    2. Displays Script, User Clicks "Generate Podcast Audio" (sends segments)
    |
    v
Backend API (FastAPI - Python) --- /api/generate-podcast-audio (Iterates Segments)
    |                                 |
    |                                 +--- (For each segment) ---> ElevenLabs API (Host/Guest Voice)
    |                                 |                            | (Returns Audio Chunk)
    |                                 <--- (Collects Audio Chunks) <---
    |                                 |
    |                                 +--- (Concatenates Audio Chunks with pydub)
    |
    <------------------------------------ (Returns MP3 Audio Stream)
    |
Frontend
    |
    3. Plays Audio

## 3. Project Structure
### (for proper visibility see it in vs code or in code format)
ai-podcast-generator/
├── backend/
│   ├── .env                    # Stores API keys (GITIGNORED)
│   ├── .gitignore
│   ├── main.py                 # FastAPI application, API endpoints, core logic
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Python virtual environment (GITIGNORED)
│
├── frontend/
│   ├── .gitignore
│   ├── index.html              # Main HTML entry point
│   ├── package.json            # Node.js project metadata & dependencies
│   ├── package-lock.json (or yarn.lock)
│   ├── vite.config.js          # Vite configuration
│   ├── public/                 # Static assets
│   └── src/
│       ├── App.css             # Main styles for App component
│       ├── App.jsx             # Main React application component
│       ├── main.jsx            # React entry point
│       └── assets/             # Frontend assets (e.g., images, if any)
│
├── .git/                       # Git repository data
├── .gitignore                  # Root .gitignore
└── README.md                   # This document (or a link to it)
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
IGNORE_WHEN_COPYING_END

## 4. Setup and Installation

Prerequisites:

Node.js and npm (or yarn)

Python (3.8+ recommended)

Git

ffmpeg installed and accessible in system PATH (for pydub audio processing).

### A. API Keys:

You will need API keys from the following services:

Google AI Studio (for Gemini API):

Go to https://aistudio.google.com/

Create an API key.

ElevenLabs (for Text-to-Speech):

Go to https://elevenlabs.io/

Obtain your API key from your profile.

### B. Backend Setup:

Clone the repository (if applicable):

git clone [repository_url]
cd ai-podcast-generator/backend
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Create and activate a Python virtual environment:

python -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
# venv\Scripts\activate   # Windows
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Install Python dependencies:

pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Create .env file:
In the backend/ directory, create a file named .env and add your API keys:

GOOGLE_GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY_HERE"
ELEVENLABS_API_KEY="YOUR_ELEVENLABS_API_KEY_HERE"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Env
IGNORE_WHEN_COPYING_END

(Note: This file is gitignored and should never be committed.)

Define Fixed Voices (Optional Modification):
The fixed Host and Guest voice IDs for ElevenLabs are defined directly in backend/main.py. You can change these constants if desired:

HOST_VOICE_ID = "YOUR_CHOSEN_FEMALE_VOICE_ID"
GUEST_VOICE_ID = "YOUR_CHOSEN_MALE_VOICE_ID"
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Python
IGNORE_WHEN_COPYING_END

## C. Frontend Setup:

Navigate to the frontend directory:

cd ../frontend  # If you are in the backend directory
OR
cd ai-podcast-generator/frontend # From project root
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Install Node.js dependencies:

npm install
OR
yarn install
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

## 5. Running the Application (Development)

Start the Backend Server:

Open a terminal, navigate to the backend/ directory.

Ensure your virtual environment is activated.

Run:

uvicorn main:app --reload
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The backend API will typically be available at http://localhost:8000.

Start the Frontend Development Server:

Open a new terminal, navigate to the frontend/ directory.

Run:

npm run dev
OR
yarn dev
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

The frontend application will typically be available at http://localhost:5173 (or another port shown in the terminal). Open this URL in your browser.

## 6. API Endpoints (Backend)

POST /api/generate-script

Description: Generates a podcast script based on a topic and parses it into speaker segments.

Request Body (JSON):

{
    "topic": "string (user's input topic)"
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Response Body (JSON - StructuredScriptResponse):

{
    "raw_script_text": "string (full script as text)",
    "segments": [
        {"speaker": "Host|Guest", "text": "string (dialogue part)"},
        // ... more segments
    ]
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

POST /api/generate-podcast-audio

Description: Generates a combined multi-voice MP3 audio file from structured script segments.

Request Body (JSON - PodcastAudioRequest):

{
    "segments": [
        {"speaker": "Host|Guest", "text": "string (dialogue part)"},
        // ... more segments
    ]
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END

Response Body: MP3 audio stream (audio/mpeg).

GET /api/list-voices (Maintained for debugging/reference, not used by current frontend flow)

Description: Lists available voices from ElevenLabs associated with the API key.

Response Body (JSON): Array of voice objects.

GET /api/health

Description: Health check endpoint.

Response Body (JSON): {"status": "Backend is running!"}

CORS Configuration:
The backend uses FastAPI's CORSMiddleware to allow requests from the frontend development server (http://localhost:5173). This needs to be updated with the deployed frontend URL for production.

## 7. Core Logic Walkthrough

### A. Script Generation & Parsing (_generate_script_logic & _parse_script_into_segments in backend/main.py):

A detailed prompt is constructed, instructing Google Gemini to create a conversational script (Host/Guest roles), adhere to a specific structure (intro, mid-conversation, outro), length, and formatting (speaker labels on new lines).

The gemini_model.generate_content() method is called.

The raw text response from Gemini is then processed by _parse_script_into_segments.

This parsing function iterates through the script lines, using regular expressions (re.match(r"^(Host|Guest):(.*)", line)) to identify speaker changes and accumulate text for each speaker's segment.

It returns both the original raw script (for display) and the list of structured segments [{speaker, text}, ...].

### B. Multi-Voice Audio Generation & Concatenation (/api/generate-podcast-audio in backend/main.py):

The endpoint receives the list of segments.

It initializes an empty pydub.AudioSegment object (combined_audio).

For each segment:

The appropriate ElevenLabs voice_id (fixed HOST_VOICE_ID or GUEST_VOICE_ID) is selected based on the segment.speaker.

The elevenlabs_client.text_to_speech.convert() method generates audio (MP3 bytes) for the segment's text.

These audio bytes are loaded into a new pydub.AudioSegment object.

This new segment is appended to combined_audio (combined_audio += segment_audio).

After processing all segments, the combined_audio object (now containing the full podcast) is exported as an MP3 into an in-memory buffer (io.BytesIO).

This buffer is then streamed back to the client as the HTTP response.

## 8. Frontend Interaction Flow (frontend/src/App.jsx):

Topic Input: User types a topic.

"Generate Script" Click (handleGenerateScript):

Sets isLoadingScript to true.

Sends a POST request to /api/generate-script with the topic.

On response, updates generatedScriptText (for display) and scriptSegments (for later audio generation) states.

Enables the "Generate Podcast Audio" button.

"Generate Podcast Audio" Click (handleGenerateAudio):

Sets isLoadingAudio to true.

Sends a POST request to /api/generate-podcast-audio with the scriptSegments array.

On response (which is an audio blob):

Creates an object URL using URL.createObjectURL(audioBlob).

Sets the audioUrl state, which updates the src of an <audio> tag, making the podcast playable.

State Management: React's useState hook manages all dynamic data (inputs, loading states, results, errors).

Cleanup: useEffect hook with URL.revokeObjectURL() is used to release memory allocated for audio blob URLs when they are no longer needed.

## 9. Deployment Considerations

### A. Backend (FastAPI):

Platform Choices: Render, Railway, Fly.io, Heroku (with limitations), Google Cloud Run, AWS Lambda (Serverless).

Dockerfile: Create a Dockerfile to containerize the backend for easier deployment.

### backend/Dockerfile (Example)
FROM python:3.11-slim

WORKDIR /app

### Install ffmpeg (essential for pydub)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

### COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

### Expose port (default Uvicorn port)
EXPOSE 8000

### Command to run the application using Gunicorn with Uvicorn workers
CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Dockerfile
IGNORE_WHEN_COPYING_END

Production Server: Use a production-grade ASGI server like Gunicorn managing Uvicorn workers (as shown in Dockerfile CMD).

Environment Variables: API keys MUST be set as environment variables on the hosting platform, not hardcoded or in a committed .env file.

CORS: Update allow_origins in CORSMiddleware to include your deployed frontend's URL.

### B. Frontend (React/Vite):

Build for Production:

cd frontend
npm run build
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

This creates a static dist/ folder.

Platform Choices (Static Hosting): Netlify, Vercel, GitHub Pages, AWS S3 + CloudFront.

API URL: Ensure the frontend code (in App.jsx fetch calls) points to the deployed backend API URL, not http://localhost:8000. This can be managed with an environment variable (e.g., VITE_API_BASE_URL in a .env file for Vite).

## 10. Future Enhancements & Known Limitations

Enhancements:

User-selectable voices (if plan allows more/cloning).

Background music/SFX.

Script editing before audio generation.

Downloadable script files.

User accounts and saved podcasts.

More robust error handling and specific user feedback.

Progress indicators for audio generation.

Limitations:

Reliability of LLM script formatting (parser might need adjustments if Gemini output varies).

Fixed voices (current implementation).

ElevenLabs/Gemini API rate limits and costs.

ffmpeg dependency can sometimes be tricky for users to set up locally if not packaged with a deployment.

Audio generation for very long scripts can be slow and resource-intensive.

## 11. Troubleshooting Tips

### Backend:

Check Uvicorn/Gunicorn logs for errors.

Verify API keys in .env (local) or environment variables (deployed).

Ensure ffmpeg is installed and in PATH if pydub errors occur.

Test individual API endpoints with Postman/Insomnia.

### Frontend:

Use browser Developer Tools (Console, Network tab).

Check for CORS errors in the console.

Verify API request/response payloads in the Network tab.

AI Services:

Check dashboards for Gemini and ElevenLabs for API errors, usage, and quota status.
