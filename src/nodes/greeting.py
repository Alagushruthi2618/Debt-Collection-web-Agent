# src/nodes/greeting.py

from ..state import CallState


def greeting_node(state: CallState) -> dict:
    """
    Initial greeting.
    Checks if user confirms or denies being the person.
    """

    # First time - ask for confirmation
    if not state.get("has_greeted"):
        first_name = state["customer_name"].split()[0]

        message = (
            f"Hello {first_name}, good day. "
            f"This is a call from ABC Finance. "
            f"Am I speaking with {state['customer_name']}?"
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

    # Check user's response
    user_input = state.get("last_user_input", "").lower().strip()
    
    # If no input yet, wait
    if not user_input:
        return {
            "stage": "greeting",
            "awaiting_user": True,
        }

    # Check for denial phrases
    denial_phrases = [
        "no",
        "nope",
        "not",
        "wrong",
        "incorrect",
        "that's not me",
        "that is not me",
        "i'm not",
        "i am not",
        "i am not the person",
        "i'm not the person",
        "wrong person",
        "not me",
        "different person",
        "you have the wrong number",
        "wrong number",
    ]
    
    # Check if user denied being the person
    is_denial = any(phrase in user_input for phrase in denial_phrases)
    
    # Also check for explicit confirmations
    confirmation_phrases = [
        "yes",
        "yeah",
        "yep",
        "correct",
        "that's me",
        "that is me",
        "speaking",
        "this is",
    ]
    
    is_confirmation = any(phrase in user_input for phrase in confirmation_phrases)
    
    # If user denied, end the call
    if is_denial and not is_confirmation:
        return {
            "is_verified": False,
            "call_outcome": "wrong_person",
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": (
                    "I apologize for the confusion. "
                    "Thank you for your time. Have a good day."
                )
            }],
            "is_complete": True,
            "stage": "closing",
            "awaiting_user": False,
            "last_user_input": None,
        }
    
    # If confirmed (or ambiguous), proceed to verification
    if is_confirmation or not is_denial:
        # Add acknowledgment message if user confirmed
        if is_confirmation:
            return {
                "messages": state["messages"] + [{
                    "role": "assistant",
                    "content": "Thank you for confirming. Let me verify your identity."
                }],
                "stage": "verification",
                "awaiting_user": False,
                "last_user_input": None,
            }
    
    # Default: proceed to verification
    return {
        "stage": "verification",
        "awaiting_user": False,
        "last_user_input": None,
    }