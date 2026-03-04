import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse

# Add project root to path (parent directory of 'api')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.phase4_generation.generator import NextLeapGenerator

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Generator
generator = None
try:
    generator = NextLeapGenerator()
except Exception as e:
    print(f"GenError: {e}")

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    if not generator:
        raise HTTPException(status_code=500, detail="GenAI engine not initialized.")
    
    def event_generator():
        for part in generator.generate_stream(request.query):
            if "|||" in part:
                text_part, sources_part = part.split("|||", 1)
                if text_part:
                    yield f"data: {json.dumps({'text': text_part})}\n\n"
                try:
                    sources = json.loads(sources_part)
                except:
                    sources = []
                yield f"data: {json.dumps({'sources': sources})}\n\n"
            else:
                yield f"data: {json.dumps({'text': part})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Catch-all for Vercel
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    return {"message": "NextLeap API is active. Use /api/v1/chat/stream for AI queries."}
