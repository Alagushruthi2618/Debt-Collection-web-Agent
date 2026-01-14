# src/nodes/greeting.py

from ..state import CallState


def greeting_node(state: CallState) -> dict:
    """
    Initial greeting.
    Only runs once.
    """

    # Skip if already greeted
    if state.get("has_greeted"):
        return {
            "stage": "greeting",
            "awaiting_user": False,
        }

    first_name = state["customer_name"].split()[0]

    message = (
        f"Hello {first_name}! 👋 "
        f"I'm reaching out from ABC Finance. "
        f"Are you {state['customer_name']}?"
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