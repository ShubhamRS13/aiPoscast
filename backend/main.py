# backend/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
import os

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


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Podcast Generator Backend! - By Shubham Shinde"}

@app.get("/api/health")
async def health_check():
    return {"status": "Backend is running!"}