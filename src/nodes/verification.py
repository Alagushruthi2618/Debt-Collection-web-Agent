# src/nodes/verification.py

from ..state import CallState


def verification_node(state: CallState) -> dict:
    """
    Verify customer identity using phone number.
    Phone number verification already happened during session initialization,
    so we automatically mark the user as verified.
    """

    # Guardrail: Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Guardrail: Ensure required fields exist
    if "customer_phone" not in state:
        raise ValueError("Invalid state: customer_phone is required")
    
    # Skip if already verified
    if state.get("is_verified"):
        return {
            "stage": "verified",
            "awaiting_user": False,
        }

    # Guardrail: Validate phone number exists and is not empty
    phone = state.get("customer_phone", "").strip()
    if not phone:
        raise ValueError("Invalid state: customer_phone cannot be empty")
    
    # Phone number verification already happened at session initialization
    # If we reach here, the phone number was validated and customer exists
    # So we can automatically verify the user (silently, no message)
    return {
        "is_verified": True,
        "verification_attempts": 1,  # Track that verification occurred
        "stage": "verified",
        "awaiting_user": False,
        "last_user_input": None,
    }
