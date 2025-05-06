# backend/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Podcast Generator Backend!"}

@app.get("/api/health")
async def health_check():
    return {"status": "Backend is running!"}