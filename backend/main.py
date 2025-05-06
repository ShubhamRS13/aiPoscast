# backend/main.py
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
from pydantic import BaseModel

# load env variables
load_dotenv()

# get api key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# debug - check for keys are loaded 
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in .env file.")
if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY not found in .env file.")
if not DEEPGRAM_API_KEY:
    print("Warning: DEEPGRAM_API_KEY not found in .env file.")


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
    """
    Generates a podcast script based on the provided topic.
    (Currently returns a dummy script)
    """
    print(f"Received topic: {request.topic}")

    # --- DUMMY SCRIPT GENERATION ---
    # In the next step, we'll replace this with an actual OpenAI call
    if not request.topic or request.topic.strip() == "":
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    dummy_script = f"""
    --- DUMMY PODCAST SCRIPT ---

    **Episode Title:** Exploring {request.topic.title()}

    **Intro Music Fades In and Out**

    **Host:** Welcome, everyone, to 'AI Insights'! Today, we're diving deep into the fascinating world of {request.topic}.
    It's a subject that's been on many minds, and we're here to shed some light.

    **Segment 1: What is {request.topic.title()}?**
    **Host:** So, to start, what exactly do we mean when we talk about {request.topic}?
    Well, essentially, it's all about [brief explanation related to the topic].
    This has huge implications for [mention an area].

    **Segment 2: The Impact and Future**
    **Host:** Looking ahead, the impact of {request.topic} could be transformative.
    Imagine a world where [future scenario related to topic].
    Of course, there are challenges too, such as [mention a challenge].

    **Outro:**
    **Host:** And that's all the time we have for today on {request.topic}.
    Join us next time as we explore another exciting AI development. Thanks for tuning in!

    **Outro Music Fades In**
    --- END OF DUMMY SCRIPT ---
    """

    return ScriptResponse(
        topic_received=request.topic,
        script=dummy_script
    )