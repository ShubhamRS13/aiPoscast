# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse # For streaming audio
from dotenv import load_dotenv
import os
import re 
from pydantic import BaseModel
import google.generativeai as genai

from pydub import AudioSegment # Import AudioSegment from pydub
import io 

from elevenlabs import Voice, VoiceSettings 
from elevenlabs.client import ElevenLabs 

import json # For putting script into header
from urllib.parse import quote # For safely encoding script text for header

HOST_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # female
GUEST_VOICE_ID = "pNInz6obpgDQGcFmaJgB" # male

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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173", # Your Vite dev server default port
    "http://localhost:3000", # Common React dev port
    # Add your deployed frontend URL later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
    expose_headers=["X-Podcast-Script", "Content-Disposition"]
)

# Pydantic model for request body
class ScriptRequest(BaseModel):
    topic: str
    
class Segment(BaseModel):
    speaker: str
    text: str

class StructuredScriptResponse(BaseModel):
    raw_script_text: str
    segments: list[Segment]

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

class PodcastAudioRequest(BaseModel):
    segments: list[Segment]

# --- End Points ---
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Podcast Generator Backend! - By Shubham Shinde"}

@app.get("/api/health")
async def health_check():
    return {"status": "Backend is running!"}


@app.post("/api/generate-script", response_model=StructuredScriptResponse)
async def generate_script_endpoint(request: ScriptRequest):
    """
    Generates a podcast script based on the provided topic,
    parses it into speaker segments, and returns both.
    """
    print(f"API: Received topic for script generation: {request.topic}")

    if not request.topic or request.topic.strip() == "":
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    try:
        # Call the refactored logic which now returns raw text and segments
        raw_script, parsed_segments = await _generate_script_logic(request.topic)

        if not parsed_segments:
            print("API Warning: Script generation resulted in no usable segments.")

        return StructuredScriptResponse(
            raw_script_text=raw_script,
            segments=parsed_segments
        )

    except ValueError as ve: # Catch input validation errors from _generate_script_logic
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re: # Catch internal processing errors from _generate_script_logic
        print(f"API: Runtime error during script generation: {re}")
        if "Gemini" in str(re): # Be more specific about upstream errors
            raise HTTPException(status_code=502, detail=f"Error with script generation service: {str(re)}")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error during script generation: {str(re)}")
    except Exception as e: # Generic catch-all
        print(f"API: Unexpected error in /generate-script: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/api/generate-podcast-audio")
async def generate_podcast_audio_endpoint(request: PodcastAudioRequest):
    """
    Generates a single podcast audio file from structured script segments,
    using different voices for Host and Guest.
    """
    print(f"API: Received request to generate podcast audio for {len(request.segments)} segments.")

    if not request.segments:
        raise HTTPException(status_code=400, detail="No script segments provided.")
    if not elevenlabs_client:
        raise HTTPException(status_code=500, detail="ElevenLabs client not configured.")

    try:
        combined_audio = AudioSegment.empty() # Initialize an empty AudioSegment
        
        eleven_voice_settings = VoiceSettings(
            stability=0.71,
            similarity_boost=0.5, # Adjust for desired similarity to base voice
            style=0.0, # Set to > 0 if using a voice with style exaggeration
            use_speaker_boost=True
        )
        # Default model for ElevenLabs TTS
        eleven_model_id = "eleven_multilingual_v2" # Or your preferred model

        segment_count = 0
        for i, segment_data in enumerate(request.segments):
            segment_count = i + 1
            speaker = segment_data.speaker
            text_to_speak = segment_data.text

            if not text_to_speak.strip():
                print(f"Segment {segment_count} for {speaker} is empty, skipping audio generation for it.")
                continue

            print(f"Processing segment {segment_count}/{len(request.segments)}: Speaker: {speaker}")

            if speaker.lower() == "host":
                voice_id_to_use = HOST_VOICE_ID
            elif speaker.lower() == "guest":
                voice_id_to_use = GUEST_VOICE_ID
            else:
                print(f"Warning: Unknown speaker '{speaker}' in segment {segment_count}. Using default host voice.")
                voice_id_to_use = HOST_VOICE_ID # Fallback or could raise error

            # Generate audio for the current segment's text
            print(f"  Generating audio for '{text_to_speak[:50]}...' with voice {voice_id_to_use}")
            
            # `elevenlabs_client.text_to_speech.convert` returns an iterator of bytes
            audio_bytes_iterator = elevenlabs_client.text_to_speech.convert(
                voice_id=voice_id_to_use,
                output_format="mp3_44100_128", # Consistent high-quality MP3 format
                text=text_to_speak,
                model_id=eleven_model_id,
                voice_settings=eleven_voice_settings,
            )
            
            # Accumulate all bytes from the iterator
            segment_audio_bytes = b"".join([chunk for chunk in audio_bytes_iterator])

            if not segment_audio_bytes:
                print(f"Warning: No audio data received from ElevenLabs for segment {segment_count} ({speaker}).")
                continue # Skip if no audio was generated

            # Load the MP3 bytes into a pydub AudioSegment
            # pydub needs to know the format of the input bytes.
            # We use BytesIO to treat the bytes like a file.
            try:
                segment_audio = AudioSegment.from_file(io.BytesIO(segment_audio_bytes), format="mp3")
                combined_audio += segment_audio
                print(f"  Segment {segment_count} audio ({len(segment_audio_bytes)} bytes) appended.")
            except Exception as pydub_err:
                print(f"Error processing audio for segment {segment_count} with pydub: {pydub_err}. Skipping segment.")
                # Potentially log more details about segment_audio_bytes here if it's consistently failing
                continue
        
        if len(combined_audio) == 0:
            print("API Error: No audio was combined. All segments might have failed or were empty.")
            raise HTTPException(status_code=500, detail="Failed to generate any audio content from the provided segments.")

        # Export the combined audio to an in-memory MP3 file (BytesIO buffer)
        final_audio_buffer = io.BytesIO()
        combined_audio.export(final_audio_buffer, format="mp3")
        final_audio_buffer.seek(0) # Rewind the buffer to the beginning for reading

        print("API: Successfully combined audio segments. Streaming final MP3.")
        
        # Suggest a filename for the download
        # For simplicity, not making filename dynamic based on topic here as topic isn't passed to this endpoint
        headers = {
            "Content-Disposition": "attachment; filename=\"generated_podcast.mp3\""
        }
        return StreamingResponse(final_audio_buffer, media_type="audio/mpeg", headers=headers)

    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        print(f"API: Unexpected error in /generate-podcast-audio: {e}")
        # Check for specific ElevenLabs errors if possible, e.g., quota
        error_message = str(e)
        if "quota" in error_message.lower() or "limit" in error_message.lower() or "exceeded" in error_message.lower():
            raise HTTPException(status_code=429, detail=f"ElevenLabs API Error (Quota/Limit): {error_message}")
        if "Unauthenticated" in error_message or "Authentication" in error_message:
             raise HTTPException(status_code=401, detail=f"ElevenLabs Authentication Error: {error_message}")
        raise HTTPException(status_code=500, detail=f"Failed to generate podcast audio: {error_message}")


def _parse_script_into_segments(raw_script_text: str) -> list[dict[str, str]]:
    segments = []
    # Regex to find "Speaker:" followed by text.
    # It captures the speaker (Host or Guest) and the subsequent text until the next speaker label or end of string.
    
    # Pattern looks for "Host:" or "Guest:", captures the name, then captures all text
    # until the next "Host:" or "Guest:" or the end of the string.
    # We'll split by lines first to handle multi-line text for a single speaker.
    # [ {'speker ': H|G, "text": "script"}, {}, {}]
    current_speaker = None
    current_lines = []
    
    # Split the raw script into lines to process
    script_lines = raw_script_text.strip().split('\n')

    for line in script_lines:
        line = line.strip() # Remove leading/trailing whitespace from the line
        if not line: # Skip empty lines
            continue

        # Check if the line starts with a speaker label
        match = re.match(r"^(Host|Guest):(.*)", line, re.IGNORECASE)
        if match:
            # If we have a current speaker and accumulated lines, save the previous segment
            if current_speaker and current_lines:
                segments.append({
                    "speaker": current_speaker,
                    "text": "\n".join(current_lines).strip() # Join lines and strip again
                })
            
            # Start a new segment
            current_speaker = match.group(1).strip().capitalize() # "Host" or "Guest"
            current_lines = [match.group(2).strip()] # Start with the text on the same line as the label
        elif current_speaker:
            # This line belongs to the current speaker
            current_lines.append(line)
       
    # Add the last segment if any
    if current_speaker and current_lines:
        segments.append({
            "speaker": current_speaker,
            "text": "\n".join(current_lines).strip()
        })
        
    # Filter out any segments with empty text, just in case
    segments = [seg for seg in segments if seg.get("text")]

    print(f"Internal: Parsed into {len(segments)} segments.")
    return segments


async def _generate_script_logic(topic: str)-> tuple[str, list[dict[str, str]]]: # Removed type hint for return for now, will add later
    if not topic or topic.strip() == "":
        raise ValueError("Topic cannot be empty for script generation.")
    if not gemini_model:
        raise RuntimeError("Gemini model not initialized.")
    print("step1")
    try:
        prompt_for_gemini = f"""
        You are an expert podcast scriptwriter tasked with creating an engaging and well-structured conversational script.
        The podcast features a Host and a Guest discussing the topic: "{topic}".

        Script Requirements:

        1.  Overall Length: The entire podcast should be approximately 3-4 minutes long when spoken (aim for around 450-550 words total for the script).
        2.  Speaker Labels: Clearly label each line with either "Host:" or "Guest:". Ensure there's a natural back-and-forth.
        3.  Structure:
                Start (Host Introduction - approx. 30-60 seconds / 75-100 words):**
                    Host introduces the podcast show (you can invent a catchy show name related to general topics or the input topic).
                    Host briefly introduces the main topic.
                    Host introduces the Guest (you can invent a plausible expert name/title for the Guest based on the topic).
                Mid (Host & Guest Conversation - approx. 2-3 minutes / 350-400 words):**
                    A dynamic conversation between the Host and Guest exploring 2-3 key aspects of the topic.
                    Host should ask insightful questions.
                    Guest should provide clear, informative, and engaging answers/perspectives.
                    Ensure a balanced dialogue.
                End (Host Summary & Call to Action - approx. 30-60 seconds / 50-60 words):**
                    Host thanks the Guest for their insights.
                    Host provides a brief summary of the key takeaways from the discussion.
                    Host includes a call to action (e.g., "What are your thoughts? Find us on social media @[YourPodcastHandle]", "Don't forget to subscribe for more discussions like this.", "Visit our website at [yourwebsite.com] for more resources.").
                    Host signs off.
        4.  Readability and Formatting:
                Use clear, concise language.
                Ensure each speaker's line starts on a new line after their label (e.g., "Host:\nWelcome to...").
                Use proper paragraph breaks within longer spoken segments for better visual organization if needed, but primarily focus on the speaker turns.
                Avoid any meta-commentary about the script itself (e.g., "Here's the script:", "[Transition Music]"). Just provide the raw dialogue with speaker labels.

        Example Snippet of Expected Format:

        Host:
        Welcome back to "Future Forward," the podcast that decodes tomorrow's trends today! I'm your host, Alex.
        Today, we're diving deep into {topic}. And to help us navigate this complex subject, we're thrilled to have Dr. Evelyn Reed, a leading researcher in [Guest's relevant field]. Evelyn, welcome to the show!

        Guest:
        Thanks for having me, Alex! It's a pleasure to be here.

        Host:
        Evelyn, to start us off, could you give our listeners a foundational understanding of "a key aspect of the topic"?

        Guest:
        Absolutely. Essentially, "Guest explains key aspect...""
        It's quite fascinating because...

        ---

        Please generate the full script based on these requirements for the topic: "{topic}"
        """

        print(f"Internal: Sending script request to Google Gemini for topic: {topic} with new prompt.")

        generation_config = genai.types.GenerationConfig(
            # max_output_tokens=1500, # Ensure enough tokens for ~500 words
            temperature=0.7 # Adjust for creativity vs. factuality
        )
        
        # Make sure your gemini_model instance can take generation_config
        # If gemini_model = genai.GenerativeModel('gemini-pro'), it should.
        response = gemini_model.generate_content(
            prompt_for_gemini,
            generation_config=generation_config # Add this
        )

        if not response.text:
            print(f"Internal: Gemini response was empty. Prompt feedback: {response.prompt_feedback}")
            # You can inspect response.candidates[0].finish_reason and safety_ratings here
            finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
            raise RuntimeError(f"Failed to generate script from Gemini (empty response). Finish reason: {finish_reason}")
            
        raw_script_text = response.text.strip()
        print("Internal: Received raw script from Google Gemini.")
        
        parsed_segments = _parse_script_into_segments(raw_script_text)
        
        if not parsed_segments:
            print("Warning: Script parsing resulted in no segments. The LLM output might be malformed.")
        # We will parse this `generated_script_text` into segments in the next step (B3)
        # For now, this function will just return the raw script text.
        # The calling endpoint will handle parsing.
        return  raw_script_text, parsed_segments # Return raw script text for now

    except Exception as e:
        print(f"Internal: An unexpected error occurred during script generation: {e}")
        raise RuntimeError(f"Internal Gemini Error: {str(e)}")
    