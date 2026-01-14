#!/usr/bin/env python3
"""
Test script to verify backend can start without errors.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("Testing Backend Startup")
print("=" * 60)

# Test 1: Environment variables
print("\n[1] Checking environment variables...")
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"  [OK] GEMINI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
else:
    print("  [WARN] GEMINI_API_KEY not set (server will start but API calls may fail)")

# Test 2: Import FastAPI
print("\n[2] Testing FastAPI import...")
try:
    from fastapi import FastAPI
    print("  [OK] FastAPI imported successfully")
except Exception as e:
    print(f"  [ERROR] Failed to import FastAPI: {e}")
    sys.exit(1)

# Test 3: Import routes
print("\n[3] Testing route imports...")
try:
    from backend.routes import chat
    print("  [OK] Chat routes imported successfully")
except Exception as e:
    print(f"  [ERROR] Failed to import chat routes: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Import graph
print("\n[4] Testing graph import...")
try:
    from src.graph import app as graph_app
    print("  [OK] Graph imported successfully")
except Exception as e:
    print(f"  [ERROR] Failed to import graph: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Create FastAPI app
print("\n[5] Testing FastAPI app creation...")
try:
    from backend.app import app
    print("  [OK] FastAPI app created successfully")
except Exception as e:
    print(f"  [ERROR] Failed to create FastAPI app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All startup tests passed!")
print("=" * 60)
print("\nYou can now start the server with:")
print("  python backend/app.py")
print("  OR")
print("  uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload")
