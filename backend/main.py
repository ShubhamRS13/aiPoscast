# backend/main.py
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import google.generativeai as genai


# load env variables
load_dotenv()

# get api key
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# debug - check for keys are loaded 
if not GOOGLE_GEMINI_API_KEY:
    print("CRITICAL: GOOGLE_GEMINI_API_KEY not found. The script generation will fail.")
if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY not found in .env file.")


# config Google Gemini and create the model
if GOOGLE_GEMINI_API_KEY:
    genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
else:
    print("CRITICAL: GOOGLE_GEMINI_API_KEY not found. Script generation will fail.")
    gemini_model = None 
    
app = FastAPI()

# Pydantic model for request body
class ScriptRequest(BaseModel):
    topic: str
    # You can add more parameters later, like 'tone', 'length', etc.

# Pydantic model for response (good practice)
class ScriptResponse(BaseModel):
    topic_received: str
    script: str
    # You can add more fields like 'estimated_duration', etc.


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
