import os
import sys

# Ensure the root directory and relevant source folders are in the Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

# Import the FastAPI app from the existing backend location
from src.phase5_backend.main import app

# This allows deployment services to find the 'app' object in the root main.py
if __name__ == "__main__":
    import uvicorn
    # Use environmental port if provided (for Render/Railway/Heroku)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
