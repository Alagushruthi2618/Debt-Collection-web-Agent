# backend/routes/chat.py

"""
Chat endpoint for web-based agent.
Handles user input and invokes LangGraph agent.
"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import with error handling
try:
    from src.graph import app as graph_app
    print("[OK] Successfully imported graph")
except Exception as e:
    import traceback
    print(f"[ERROR] Failed to import graph: {e}")
    traceback.print_exc()
    graph_app = None

from backend.session_store import get_session, create_session, update_session


router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for /chat endpoint."""
    session_id: str
    user_input: str


class ChatResponse(BaseModel):
    """Response model for /chat endpoint."""
    messages: list[dict]
    stage: str
    awaiting_user: bool
    offered_plans: list[dict]
    is_complete: bool
    payment_status: Optional[str] = None
    # Customer info for header
    is_verified: Optional[bool] = False
    customer_name: Optional[str] = None
    outstanding_amount: Optional[float] = None
    days_past_due: Optional[int] = None
    loan_id: Optional[str] = None


def sanitize_user_input(user_input: str) -> str:
    """
    Sanitize user input to prevent injection attacks and ensure safe processing.
    """
    if not user_input:
        return ""
    
    # Strip whitespace
    sanitized = user_input.strip()
    
    # Guardrail: Check maximum length (prevent DoS)
    MAX_INPUT_LENGTH = 5000
    if len(sanitized) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message is too long. Maximum length is {MAX_INPUT_LENGTH} characters."
        )
    
    # Guardrail: Check minimum length (prevent empty/spam)
    if len(sanitized) == 0:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty. Please enter a message."
        )
    
    return sanitized


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle user chat input.
    
    Flow:
    1. Get or create session
    2. Add user message to state
    3. Update state with user input
    4. Invoke LangGraph
    5. Return response
    """
    
    # Guardrail: Validate request object
    if not request:
        raise HTTPException(
            status_code=400,
            detail="Invalid request. Request body is required."
        )
    
    session_id = request.session_id
    
    # Guardrail: Validate session_id
    if not session_id or not isinstance(session_id, str):
        raise HTTPException(
            status_code=400,
            detail="Session ID is required. Please start a new chat."
        )
    
    # Guardrail: Validate session_id format (UUID-like)
    if len(session_id) < 10 or len(session_id) > 100:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format. Please start a new chat."
        )
    
    # Sanitize user input
    user_input = sanitize_user_input(request.user_input if request.user_input else "")
    
    # Get session state
    state = get_session(session_id)
    
    # Guardrail: Session existence check
    if not state:
        raise HTTPException(
            status_code=404, 
            detail="Session not found. Your session may have expired. Please start a new chat."
        )
    
    # Guardrail: Validate state structure
    if not isinstance(state, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid session state. Please start a new chat."
        )
    
    # Guardrail: Check if call is already complete
    if state.get("is_complete"):
        raise HTTPException(
            status_code=400,
            detail="This conversation has already ended. Please start a new chat to continue."
        )
    
    # Guardrail: Validate required state fields
    if "messages" not in state:
        raise HTTPException(
            status_code=500,
            detail="Invalid session state: missing messages. Please start a new chat."
        )
    
    if "stage" not in state:
        raise HTTPException(
            status_code=500,
            detail="Invalid session state: missing stage. Please start a new chat."
        )
    
    # Guardrail: Check if agent is awaiting user input
    if not state.get("awaiting_user"):
        # This might happen if frontend sends input when agent isn't ready
        # We'll allow it but log a warning for debugging
        print(f"[WARNING] Received input when not awaiting user. Stage: {state.get('stage')}")
    
    # Add user message to state
    state["messages"].append({
        "role": "user",
        "content": user_input
    })
    
    # Update state with user input (nodes read from last_user_input)
    state["last_user_input"] = user_input
    state["awaiting_user"] = False
    
    try:
        # Check if graph is available
        if graph_app is None:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: Graph not initialized. Please check server logs."
            )
        
        # Invoke LangGraph agent
        # The graph will process the input and update state
        config = {"recursion_limit": 25}
        updated_state = graph_app.invoke(state, config)
        
        # Validate that we got a valid state back
        if not updated_state:
            raise ValueError("Graph returned empty state")
        
        # Update session store with new state
        update_session(session_id, updated_state)
        
        # Extract response data with defaults
        messages = updated_state.get("messages", [])
        stage = updated_state.get("stage", "unknown")
        awaiting_user = updated_state.get("awaiting_user", False)
        offered_plans = updated_state.get("offered_plans", [])
        is_complete = updated_state.get("is_complete", False)
        payment_status = updated_state.get("payment_status")
        
        # Extract customer info for header
        is_verified = updated_state.get("is_verified", False)
        customer_name = updated_state.get("customer_name")
        outstanding_amount = updated_state.get("outstanding_amount")
        days_past_due = updated_state.get("days_past_due")
        loan_id = updated_state.get("loan_id")
        
        # Ensure messages list is valid
        if not isinstance(messages, list):
            messages = []
        
        return ChatResponse(
            messages=messages,
            stage=stage,
            awaiting_user=awaiting_user,
            offered_plans=offered_plans,
            is_complete=is_complete,
            payment_status=payment_status,
            is_verified=is_verified,
            customer_name=customer_name,
            outstanding_amount=outstanding_amount,
            days_past_due=days_past_due,
            loan_id=loan_id
        )
        
    except ValueError as e:
        # Handle validation errors
        print(f"[ERROR] Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Chat endpoint error: {e}")
        print(error_trace)
        
        # Provide user-friendly error message
        error_detail = "An error occurred while processing your message. Please try again."
        error_str = str(e).lower()
        
        if "gemini_api_key" in error_str or "api_key" in error_str:
            error_detail = "Server configuration error: GEMINI_API_KEY is not set. Please configure the API key in the .env file."
        elif "timeout" in error_str:
            error_detail = "Request timed out. Please try again."
        elif "connection" in error_str:
            error_detail = "Connection error. Please check your internet connection."
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


class InitRequest(BaseModel):
    """Request model for /init endpoint."""
    phone: str


class FeedbackRequest(BaseModel):
    """Request model for /feedback endpoint."""
    session_id: str
    rating: int
    feedback: Optional[str] = None


def validate_phone_number(phone: str) -> str:
    """
    Validate and sanitize phone number.
    Returns sanitized phone number or raises HTTPException.
    """
    if not phone:
        raise HTTPException(
            status_code=400, 
            detail="Phone number is required. Please enter a valid phone number."
        )
    
    # Sanitize: remove whitespace and common separators
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Guardrail: Check minimum length
    if len(phone) < 10:
        raise HTTPException(
            status_code=400,
            detail="Please enter a valid phone number (at least 10 digits)."
        )
    
    # Guardrail: Check maximum length (reasonable limit)
    if len(phone) > 20:
        raise HTTPException(
            status_code=400,
            detail="Phone number is too long. Please enter a valid phone number."
        )
    
    # Guardrail: Check for valid characters (digits and + only)
    if not phone.replace("+", "").replace(" ", "").isdigit():
        raise HTTPException(
            status_code=400,
            detail="Phone number contains invalid characters. Please use only digits and +."
        )
    
    # Guardrail: Ensure + is only at the start if present
    if "+" in phone and not phone.startswith("+"):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. The + sign must be at the beginning."
        )
    
    return phone


@router.post("/init")
async def init_session(request: InitRequest):
    """
    Initialize a new session for a phone number.
    Returns session_id and initial state.
    """
    # Guardrail: Validate request object
    if not request or not hasattr(request, 'phone'):
        raise HTTPException(
            status_code=400,
            detail="Invalid request. Phone number is required."
        )
    
    # Validate and sanitize phone number
    phone = validate_phone_number(request.phone)
    
    session_id, state = create_session(phone)
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with phone number {phone} not found. Please use a valid test phone number (e.g., +919876543210, +919876543211, +919876543212)."
        )
    
    # Invoke graph to get initial greeting
    try:
        # Check if graph is available
        if graph_app is None:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error: Graph not initialized. Please check server logs."
            )
        
        config = {"recursion_limit": 25}
        initial_state = graph_app.invoke(state, config)
        
        # Validate state
        if not initial_state:
            raise ValueError("Graph returned empty state during initialization")
        
        update_session(session_id, initial_state)
        
        # Extract and validate response data
        messages = initial_state.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        
        # Return session info
        return {
            "session_id": session_id,
            "messages": messages,
            "stage": initial_state.get("stage", "init"),
            "awaiting_user": initial_state.get("awaiting_user", False),
            "offered_plans": initial_state.get("offered_plans", []),
            "is_complete": initial_state.get("is_complete", False),
            "payment_status": initial_state.get("payment_status"),
            "is_verified": initial_state.get("is_verified", False),
            "customer_name": initial_state.get("customer_name"),
            "outstanding_amount": initial_state.get("outstanding_amount"),
            "days_past_due": initial_state.get("days_past_due"),
            "loan_id": initial_state.get("loan_id")
        }
    except ValueError as e:
        print(f"[ERROR] Validation error during init: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Init session error: {e}")
        print(error_trace)
        
        # Provide user-friendly error message
        error_detail = "An error occurred while starting the chat. Please try again."
        error_str = str(e).lower()
        
        if "gemini_api_key" in error_str or "api_key" in error_str:
            error_detail = "Server configuration error: GEMINI_API_KEY is not set. Please configure the API key in the .env file."
        elif "timeout" in error_str:
            error_detail = "Request timed out. Please try again."
        elif "connection" in error_str:
            error_detail = "Connection error. Please check your internet connection."
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.post("/upload-screenshot")
async def upload_screenshot(
    session_id: str = Form(...),
    screenshot: UploadFile = File(...)
):
    """
    Handle screenshot upload for payment disputes.
    Saves the screenshot and adds a note to the session.
    """
    
    if not session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required"
        )
    
    # Accept any file type for now (as per user requirement)
    # File type validation can be added later if needed
    
    # Get session state
    state = get_session(session_id)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path(project_root) / "uploads" / "screenshots"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = screenshot.filename.split('.')[-1] if '.' in screenshot.filename else 'png'
    filename = f"{session_id}_{timestamp}.{file_extension}"
    file_path = uploads_dir / filename
    
    try:
        # Save the file
        with open(file_path, "wb") as f:
            content = await screenshot.read()
            f.write(content)
        
        # Add message to state about screenshot upload
        screenshot_message = {
            "role": "user",
            "content": f"[Screenshot uploaded: {screenshot.filename}]"
        }
        
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append(screenshot_message)
        
        # If payment_status is "paid" and we're in closing stage, trigger graph to complete
        # This will generate the final closing message
        if state.get("payment_status") == "paid" and state.get("stage") == "closing":
            print(f"[UPLOAD] Payment status is 'paid' and stage is 'closing' - triggering graph")
            try:
                # Set last_user_input to trigger graph processing
                state["last_user_input"] = f"[Screenshot uploaded: {screenshot.filename}]"
                state["awaiting_user"] = False
                
                print(f"[UPLOAD] Invoking graph with state: payment_status={state.get('payment_status')}, stage={state.get('stage')}, awaiting_user={state.get('awaiting_user')}")
                
                # Invoke graph to process and complete
                if graph_app is not None:
                    config = {"recursion_limit": 25}
                    updated_state = graph_app.invoke(state, config)
                    
                    print(f"[UPLOAD] Graph returned. Updated state: is_complete={updated_state.get('is_complete')}, stage={updated_state.get('stage')}, messages_count={len(updated_state.get('messages', []))}")
                    
                    # Validate state
                    if updated_state:
                        state = updated_state
                        update_session(session_id, state)
                        print(f"[UPLOAD] Session updated with final state")
                else:
                    print(f"[UPLOAD] ERROR: graph_app is None!")
            except Exception as e:
                import traceback
                print(f"[ERROR] Error processing screenshot upload in graph: {e}")
                traceback.print_exc()
                # Continue with manual state update if graph fails
                update_session(session_id, state)
        else:
            print(f"[UPLOAD] Not triggering graph - payment_status={state.get('payment_status')}, stage={state.get('stage')}")
            # Update session normally
            update_session(session_id, state)
        
        # Return updated state in same format as chat endpoint
        return {
            "success": True,
            "message": "Screenshot uploaded successfully. Our team will review it.",
            "filename": filename,
            "file_path": str(file_path),
            "messages": state.get("messages", []),
            "stage": state.get("stage", "unknown"),
            "awaiting_user": state.get("awaiting_user", False),
            "offered_plans": state.get("offered_plans", []),
            "is_complete": state.get("is_complete", False),
            "payment_status": state.get("payment_status"),
            "is_verified": state.get("is_verified", False),
            "customer_name": state.get("customer_name"),
            "outstanding_amount": state.get("outstanding_amount"),
            "days_past_due": state.get("days_past_due"),
            "loan_id": state.get("loan_id")
        }
    except Exception as e:
        print(f"[ERROR] Screenshot upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to upload screenshot. Please try again."
        )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Handle feedback submission after conversation completion.
    Stores feedback with session information.
    """
    
    if not request.session_id:
        raise HTTPException(
            status_code=400,
            detail="Session ID is required"
        )
    
    if not (1 <= request.rating <= 5):
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )
    
    # Get session state to include customer info in feedback
    state = get_session(request.session_id)
    
    # Prepare feedback data
    feedback_data = {
        "session_id": request.session_id,
        "rating": request.rating,
        "feedback": request.feedback,
        "customer_id": state.get("customer_id") if state else None,
        "customer_name": state.get("customer_name") if state else None,
        "stage": state.get("stage") if state else None,
        "payment_status": state.get("payment_status") if state else None,
        "call_outcome": state.get("call_outcome") if state else None,
        "timestamp": datetime.now().isoformat()
    }
    
    # In production, save to database
    # For now, just log it
    print(f"[FEEDBACK] Received feedback: {feedback_data}")
    
    # TODO: Save to database or external service
    # Example:
    # feedback_db.save(feedback_data)
    
    return {
        "success": True,
        "message": "Thank you for your feedback!",
        "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

