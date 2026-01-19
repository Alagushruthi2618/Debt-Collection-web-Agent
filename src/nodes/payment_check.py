# src/nodes/payment_check.py

from ..state import CallState
from ..utils.llm import classify_intent


def payment_check_node(state: CallState) -> dict:
    """
    Classify customer's payment intent using Azure OpenAI-powered classification.
    
    This node determines the customer's response to the debt disclosure
    and routes them to the appropriate next step.
    """

    # Guardrail: Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Guardrail: Validate verification status
    if not state.get("is_verified"):
        raise ValueError("Invalid state: User must be verified before payment check")
    
    user_input = state.get("last_user_input")

    # If no input yet, wait for user response
    if not user_input or user_input.strip() == "":
        return {
            "stage": "payment_check",
            "awaiting_user": True,
        }
    
    # Guardrail: Ignore date-like inputs (DOB format: DD-MM-YYYY)
    # These are from verification, not payment responses
    import re
    date_pattern = r'^\d{2}-\d{2}-\d{4}$'
    if re.match(date_pattern, user_input.strip()):
        # This is a DOB, not a payment response - wait for actual input
        return {
            "stage": "payment_check",
            "awaiting_user": True,
            "last_user_input": None,  # Clear it so we don't process it again
        }

    # Classify intent using improved Azure OpenAI-based classifier
    print(f"\n[PAYMENT_CHECK] Analyzing user input: '{user_input}'")
    intent = classify_intent(user_input).strip().lower()
    print(f"[PAYMENT_CHECK] Classified intent: {intent}\n")

    # Normalize any spelling variations (just in case)
    alias_map = {
        "dispute": "disputed",
        "call_back": "callback",
        "call back": "callback",
    }

    payment_status = alias_map.get(intent, intent)

    # Validate that we got a valid status
    valid_statuses = ["paid", "disputed", "callback", "unable", "willing", "unknown"]
    if payment_status not in valid_statuses:
        print(f"[WARNING] Unexpected payment status: {payment_status}, defaulting to 'unknown'")
        payment_status = "unknown"

    return {
        "payment_status": payment_status,
        "stage": "payment_check",
        "awaiting_user": False,
        "last_user_input": None,
    }