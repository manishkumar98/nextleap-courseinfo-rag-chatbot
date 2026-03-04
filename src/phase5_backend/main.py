import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# Add project source to path to import generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase4_generation.generator import NextLeapGenerator

load_dotenv()

app = FastAPI(title="NextLeap RAG Chatbot API")

# Configure CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be specific to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Generator (which includes Retriever and Groq)
try:
    generator = NextLeapGenerator()
except Exception as e:
    print(f"❌ Failed to initialize NextLeapGenerator: {e}")
    generator = None

# In-memory history storage (Session ID -> List of messages)
chat_history = {}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str

@app.get("/")
async def root():
    return {"message": "NextLeap RAG Chatbot API is running", "status": "online", "version": "1.0.0"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handles user chat queries by retrieving context and generating a grounded response.
    Maintains session history for contextual awareness.
    """
    if not generator:
        raise HTTPException(status_code=500, detail="GenAI engine not correctly initialized.")
    
    try:
        session_id = request.session_id
        query = request.query
        
        # Get history for this session
        history = chat_history.get(session_id, [])
        
        # Generate response with history
        answer, sources = generator.generate_response(query, history=history)
        
        # Update history
        if session_id not in chat_history:
            chat_history[session_id] = []
        
        chat_history[session_id].append({"role": "user", "content": query})
        chat_history[session_id].append({"role": "assistant", "content": answer})
        
        # Keep only last 10 messages for context window
        if len(chat_history[session_id]) > 10:
            chat_history[session_id] = chat_history[session_id][-10:]
        
        return ChatResponse(answer=answer, sources=sources, session_id=session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse

@app.post("/v1/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streams the chat response for a more premium experience.
    """
    if not generator:
        raise HTTPException(status_code=500, detail="GenAI engine not correctly initialized.")
    
    session_id = request.session_id
    query = request.query
    history = chat_history.get(session_id, [])

    def event_generator():
        full_response = ""
        sources = []
        
        # We use a special separator '|||' to distinguish between text tokens and metadata
        for part in generator.generate_stream(query, history=history):
            if "|||" in part:
                text_part, sources_part = part.split("|||", 1)
                if text_part:
                    full_response += text_part
                    yield f"data: {json.dumps({'text': text_part})}\n\n"
                
                try:
                    sources = json.loads(sources_part)
                except:
                    sources = []
                
                yield f"data: {json.dumps({'sources': sources})}\n\n"
            else:
                full_response += part
                yield f"data: {json.dumps({'text': part})}\n\n"
        
        # Update history after full generation
        if session_id not in chat_history:
            chat_history[session_id] = []
        chat_history[session_id].append({"role": "user", "content": query})
        chat_history[session_id].append({"role": "assistant", "content": full_response})
        
        # Keep history concise
        if len(chat_history[session_id]) > 10:
            chat_history[session_id] = chat_history[session_id][-10:]
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/v1/history/{session_id}")
async def get_history(session_id: str):
    """
    Returns the chat history for a specific session.
    """
    return {"session_id": session_id, "history": chat_history.get(session_id, [])}

# Backward compatibility route
@app.post("/chat", response_model=ChatResponse)
async def chat_legacy(request: ChatRequest):
    return await chat(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
