# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse # For streaming audio
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import google.generativeai as genai

from elevenlabs import Voice, VoiceSettings 
from elevenlabs.client import ElevenLabs 
# import io # For handling byte streams

# load env variables
load_dotenv()

# get api key
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


# config Google Gemini and create the model
if GOOGLE_GEMINI_API_KEY:
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    print("CRITICAL: GOOGLE_GEMINI_API_KEY not found. Script generation will fail.")
    gemini_model = None 
    
# Configure ElevenLabs Client
elevenlabs_client = None
if ELEVENLABS_API_KEY:
    try:
        elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        print("ElevenLabs client initialized.")
    except Exception as e:
        print(f"Error initializing ElevenLabs client: {e}")
else:
    print("CRITICAL: ELEVENLABS_API_KEY not found. Audio generation will fail.")

    
app = FastAPI()

# Pydantic model for request body
class ScriptRequest(BaseModel):
    topic: str

# Pydantic model for response
class ScriptResponse(BaseModel):
    topic_received: str
    script: str
    
    
class AudioRequest(BaseModel):
    script_text: str
    voice_id: str | None = "Rachel" # Default voice, or allow user to specify. Find IDs via API or ElevenLabs website.
    # You can add more voice settings here later from VoiceSettings


class VoiceInfo(BaseModel):
    voice_id: str
    name: str
    category: str | None
    # Add other relevant fields from ElevenLabs Voice object

class VoicesListResponse(BaseModel):
    voices: list[VoiceInfo]
    

# --- End Points ---
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Podcast Generator Backend! - By Shubham Shinde"}

@app.get("/api/health")
async def health_check():
    return {"status": "Backend is running!"}

@app.post("/api/generate-script", response_model=ScriptResponse) # Use POST for sending data
async def generate_script_endpoint(request: ScriptRequest):
    print(f"Received topic for script generation: {request.topic}")
    
    if not request.topic or request.topic.strip() == "":
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    
    if not gemini_model:
        raise HTTPException(status_code=500, detail="OpenAI client not initialized. Check API key.")

    try:
        # Prompt for the chatGPT
        prompt_instructions = f"""
        You are a creative, engaging and self-motivated podcast scriptwriter.
        Your task is to generate a concise podcast script based on the topic: "{request.topic}".

        The script should include:
        1. A catchy introduction with a hook to grab the listener's attention (like youtuber Beerbiseps)
        2. One or two main segments exploring different aspects of the topic. Keep it focused and easy to follow.
        3. A brief concluding summary and perhaps a thought-provoking question or a call to action (e.g., "What are your thoughts? Let us know!").
        4. Clear speaker labels if you imagine multiple speakers (e.g., Host:, Guest:), but for now, assume a single host and single guest.

        The tone should be informative yet engaging and accessible to a general audience.
        The desired length for the spoken podcast is approximately 2-3 minutes. Aim for around 300-450 words for the script.
        Do not include any pre-amble or post-amble like "Here's the script:". Just provide the script content itself.
        Start directly with the script content (e.g., "Host: Welcome to...").
        
        Topic to write about: {request.topic}
        """
        
        print("Sending request to Google Gemini...")
        
        response = gemini_model.generate_content(prompt_instructions)
        
        if not response.text:
            print(f"Gemini response was empty. Prompt feedback: {response.prompt_feedback}")
            raise HTTPException(status_code=500, detail="Failed to generate script. The response from Gemini was empty or blocked. Check safety settings or prompt.")
        
        generated_script = response.text.strip()
        print("Received script from Google Gemini.")
        
        return ScriptResponse(
            topic_received=request.topic,
            script=generated_script
            # model_used=chat_completion.model # If you want to return model info
        )

    except Exception as e: # General exception for Gemini or other issues
        print(f"An unexpected error occurred: {e}")
        error_detail = str(e)
        if hasattr(e, 'message'): # Some Google API errors have a 'message' attribute
            error_detail = e.message
        raise HTTPException(status_code=500, detail=f"An error occurred during script generation with Gemini: {error_detail}")


@app.post("/api/generate-audio")
async def generate_audio_endpoint(request: AudioRequest):
    """
    Generates audio from script text using ElevenLabs.
    Streams the audio back as an MP3.
    """
    print(f"Received script for audio generation. Voice ID: {request.voice_id or 'default'}")
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured.")
    if not request.script_text or request.script_text.strip() == "":
        raise HTTPException(status_code=400, detail="Script text cannot be empty.")

    try:
        voice_setting = VoiceSettings(
            stability=0.71, # Lower is more expressive, higher is more consistent
            similarity_boost=0.5, # How much to resemble the base voice
            style=0.0, # For style-exaggeration if the voice supports it
            use_speaker_boost=True
        )

        selected_voice_id = request.voice_id if request.voice_id else "Rachel" # Default to Rachel if none provided
        
        if selected_voice_id == "Rachel":
            selected_voice_id = "21m00Tcm4TlvDq8ikWAM"
        
        print(f"Generating audio with ElevenLabs using voice: {selected_voice_id}...")
        
        audio_stream_iterator = elevenlabs_client.text_to_speech.convert(
            text=request.script_text,
            voice_id=selected_voice_id, 
            output_format="mp3_44100_128",
            model_id="eleven_multilingual_v2",
            voice_settings = voice_setting # Or other models
            # VoiceSettings can be passed directly to some methods or set on a Voice object
            # voice_settings=VoiceSettings(stability=0.71, similarity_boost=0.5) # Example
        )
        
        print("Streaming audio response...")
        return StreamingResponse(audio_stream_iterator, media_type="audio/mpeg")

        
    except Exception as e:
        print(f"Error during ElevenLabs audio generation: {e}")
        # Check if the error is an APIError from elevenlabs for more specific messages
        if hasattr(e, 'message') and "Unauthenticated" in e.message:
             raise HTTPException(status_code=401, detail=f"ElevenLabs Authentication Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")
    

@app.get("/api/list-voices", response_model=VoicesListResponse)
async def list_voices_endpoint():
    """
    Lists available voices from ElevenLabs.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured.")
    try:
        print("Fetching voices from ElevenLabs...")
        eleven_voices_list = elevenlabs_client.voices.get_all().voices # Gets all voices (premade, cloned, etc.)
        
        formatted_voices = []
        for v in eleven_voices_list:
            # Access attributes directly as they are usually Pydantic models in newer SDKs
            formatted_voices.append(VoiceInfo(
                voice_id=v.voice_id, 
                name=v.name, 
                category=v.category if hasattr(v, 'category') else None
            ))
            
        print(f"Found {len(formatted_voices)} voices.")
        return VoicesListResponse(voices=formatted_voices)
    except Exception as e:
        print(f"Error fetching ElevenLabs voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch voices: {str(e)}")
