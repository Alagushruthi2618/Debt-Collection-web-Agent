# src/nodes/disclosure.py

from ..state import CallState


def disclosure_node(state: CallState) -> dict:
    """
    Provide legal disclosure and explain outstanding debt amount.
    Only executes once per call.
    """
    # Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Ensure customer is verified before disclosure
    if not state.get("is_verified"):
        raise ValueError("Invalid state: User must be verified before disclosure")
    
    # Skip if already disclosed
    if state.get("has_disclosed"):
        return {
            "awaiting_user": False,
        }
    
    # Validate outstanding amount
    amount = state.get("outstanding_amount", 0)
    if not isinstance(amount, (int, float)) or amount < 0:
        raise ValueError("Invalid state: outstanding_amount must be a non-negative number")
    
    message = (
        f"Main aapke outstanding payment ke baare mein call kar raha/rahi hoon - ₹{amount:,.0f}. "
        f"Yeh ek debt collection attempt hai. "
        f"Kya aap aaj yeh payment kar sakte hain?"
    )
    
    return {
        "has_disclosed": True,
        "messages": state["messages"] + [{
            "role": "assistant",
            "content": message
        }],
        "stage": "disclosure",  # Set stage to disclosure
        "awaiting_user": True,
        "last_user_input": None,  
    }