# backend/app.py

"""
FastAPI application entry point for web-based debt collection agent.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path to allow imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Check for required environment variables
if not os.getenv("GEMINI_API_KEY"):
    print("[WARNING] GEMINI_API_KEY not set. The server will start but API calls may fail.")
    print("Please create a .env file in the project root with: GEMINI_API_KEY=your_api_key_here")

# Try to import routes with error handling
try:
    from backend.routes import chat
    print("[OK] Successfully imported chat routes")
except Exception as e:
    import traceback
    print(f"[ERROR] Failed to import chat routes: {e}")
    traceback.print_exc()
    # Create a dummy router to prevent server crash
    from fastapi import APIRouter
    chat = type('obj', (object,), {'router': APIRouter()})

app = FastAPI(
    title="Debt Collection Agent API",
    description="Web-based debt collection agent backend",
    version="1.0.0"
)

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
try:
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    print("[OK] Successfully registered chat routes")
except Exception as e:
    print(f"[ERROR] Failed to register chat routes: {e}")
    import traceback
    traceback.print_exc()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Debt Collection Agent API is running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    try:
        print("[INFO] Starting server on http://0.0.0.0:8000")
        print("[INFO] Health check: http://localhost:8000/health")
        print("[INFO] API docs: http://localhost:8000/docs")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"[FATAL] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        raise

