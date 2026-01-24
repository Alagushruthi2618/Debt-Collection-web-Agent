# src/nodes/verification.py

from ..state import CallState


def verification_node(state: CallState) -> dict:
    """
    Verify customer identity.
    Phone verification happens at session init, so we mark as verified automatically.
    """
    # Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Validate required fields
    if "customer_phone" not in state:
        raise ValueError("Invalid state: customer_phone is required")
    
    # Skip if already verified
    if state.get("is_verified"):
        return {
            "stage": "verified",
            "awaiting_user": False,
        }

    # Validate phone number
    phone = state.get("customer_phone", "").strip()
    if not phone:
        raise ValueError("Invalid state: customer_phone cannot be empty")
    
    # Phone verification done at session init - auto-verify here
    return {
        "is_verified": True,
        "verification_attempts": 1,
        "stage": "verified",
        "awaiting_user": False,
        "last_user_input": None,
    }
