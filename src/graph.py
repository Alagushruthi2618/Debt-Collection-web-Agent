# src/graph.py

from langgraph.graph import StateGraph, END
from src.state import CallState

from src.nodes.greeting import greeting_node
from src.nodes.verification import verification_node
from src.nodes.disclosure import disclosure_node
from src.nodes.payment_check import payment_check_node
from src.nodes.negotiation import negotiation_node
from src.nodes.closing import closing_node


def should_continue(state: CallState) -> str:
    """
    Main routing function that determines next step based on current stage.
    Handles all conversation scenarios and edge cases.
    """
    stage = state.get("stage")
    is_complete = state.get("is_complete")
    awaiting_user = state.get("awaiting_user")
    
    # End conversation if already complete
    if is_complete:
        return END
    
    # Pause execution when waiting for user input
    if awaiting_user:
        return END
    
    # Route to appropriate node based on current stage
    if stage == "init":
        return "greeting"
    
    elif stage == "greeting":
        # Move to verification after greeting
        return "verification"
    
    elif stage == "verification":
        # Proceed to disclosure if verified
        if state.get("is_verified"):
            return "disclosure"
        # End call if verification attempts exhausted
        if state.get("verification_attempts", 0) >= 4:
            return "closing"
        return "verification"
    
    elif stage == "verified":
        return "disclosure"
    
    elif stage == "disclosure":
        # Check payment intent after disclosure
        return "payment_check"
    
    elif stage == "payment_check":
        payment_status = state.get("payment_status")
        # Wait for payment classification if not yet processed
        if payment_status is None:
            return "payment_check"
        # Route to negotiation if customer is willing to pay
        if payment_status == "willing":
            return "negotiation"
        # Close for other statuses (paid, disputed, callback, unable, unknown)
        return "closing"
    
    elif stage == "negotiation":
        messages = state.get("messages", [])
        # Check if PTP was recorded (negotiation complete)
        if state.get("ptp_id"):
            return "closing"
        
        # Detect closing signals in conversation
        if messages:
            last_msg = messages[-1]
            if last_msg.get("role") == "assistant":
                content = last_msg.get("content", "").lower()
                closing_phrases = [
                    "i've documented our discussion", 
                    "we'll follow up with you",
                    "ptp reference number",
                    "thank you for working this out"
                ]
                if any(phrase in content for phrase in closing_phrases):
                    return "closing"
        
        # Continue negotiation
        return "negotiation"
    
    elif stage == "closing":
        # Continue closing if waiting for screenshot/confirmation
        if not state.get("is_complete", False):
            return "closing"
        return END
    
    # Safety fallback for unknown stages
    print(f"[WARNING] Unknown stage '{stage}', ending conversation")
    return END


def create_graph():
    """Create and configure the LangGraph state machine."""
    graph = StateGraph(CallState)

    # Register all conversation nodes
    graph.add_node("greeting", greeting_node)
    graph.add_node("verification", verification_node)
    graph.add_node("disclosure", disclosure_node)
    graph.add_node("payment_check", payment_check_node)
    graph.add_node("negotiation", negotiation_node)
    graph.add_node("closing", closing_node)

    # Set entry point with conditional routing
    graph.set_conditional_entry_point(
        should_continue,
        {
            "greeting": "greeting",
            "verification": "verification",
            "disclosure": "disclosure",
            "payment_check": "payment_check",
            "negotiation": "negotiation",
            "closing": "closing",
            END: END,
        }
    )
    
    # All nodes use the same conditional routing logic
    for node_name in ["greeting", "verification", "disclosure", "payment_check", "negotiation", "closing"]:
        graph.add_conditional_edges(
            node_name,
            should_continue,
            {
                "greeting": "greeting",
                "verification": "verification",
                "disclosure": "disclosure",
                "payment_check": "payment_check",
                "negotiation": "negotiation",
                "closing": "closing",
                END: END,
            }
        )

    return graph


app = create_graph().compile()