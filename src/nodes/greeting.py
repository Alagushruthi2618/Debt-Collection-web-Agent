# src/nodes/greeting.py

from ..state import CallState


def greeting_node(state: CallState) -> dict:
    """
    Initial greeting.
    Handles user response - if "no" or similar, show message; if "yes", proceed silently.
    """

    # Guardrail: Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Guardrail: Validate required fields
    if "customer_name" not in state or not state.get("customer_name"):
        raise ValueError("Invalid state: customer_name is required")
    
    # Guardrail: Sanitize customer name
    customer_name = str(state["customer_name"]).strip()
    if not customer_name:
        raise ValueError("Invalid state: customer_name cannot be empty")
    
    first_name = customer_name.split()[0]
    
    # If not yet greeted, ask the question
    if not state.get("has_greeted"):
        message = (
            f"Hello {first_name}! 👋 "
            f"I'm reaching out from ABC Finance. "
            f"Are you {customer_name}?"
        )

        return {
            "has_greeted": True,
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": message
            }],
            "stage": "greeting",
            "awaiting_user": True,
            "last_user_input": None,
        }
    
    # Already greeted - check user response
    user_input = state.get("last_user_input", "").strip().lower() if state.get("last_user_input") else ""
    
    # Check for negative responses
    negative_responses = [
        "no", "nope", "not me", "wrong person", "that's not me", "that is not me",
        "i'm not", "i am not", "incorrect", "wrong", "no i'm not", "no i am not",
        "that's wrong", "that is wrong", "n", "nah", "no way"
    ]
    
    is_negative = any(neg in user_input for neg in negative_responses)
    
    if is_negative:
        # User said no - show message and end call
        error_message = (
            "I apologize for the confusion. It seems we've reached the wrong person. "
            "Please contact our support team if you believe this is an error. Thank you for your time."
        )
        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": error_message
            }],
            "stage": "closing",
            "awaiting_user": False,
            "is_complete": True,
            "call_outcome": "wrong_person",
            "last_user_input": None,
        }
    
    # User confirmed (yes or similar) - proceed silently
    return {
        "stage": "greeting",
        "awaiting_user": False,
        "last_user_input": None,
    }