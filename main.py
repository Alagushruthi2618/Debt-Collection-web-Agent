# main.py
# CLI interface for testing the debt collection agent

from src.state import create_initial_state
from src.graph import app


def main():
    """Main entry point for CLI-based agent testing."""
    print("=== Debt Collection Agent Test ===")
    print("Available test customers:")
    print("  1. +919876543210 (Rajesh Kumar, DOB: 15-03-1985)")
    print("  2. +919876543211 (Priya Sharma, DOB: 22-07-1990)")
    print("  3. +919876543212 (Amit Patel, DOB: 05-11-1988)")
    print()

    phone = input("Enter phone number: ").strip()
    state = create_initial_state(phone)

    if not state:
        print("Customer not found!")
        return

    print("\n--- Starting Call ---\n")

    # Main conversation loop - continues until call is complete
    iteration = 0
    while not state.get("is_complete"):
        iteration += 1
        
        # Prevent infinite loops
        if iteration > 50:
            print("\nMax iterations reached - ending call")
            break
            
        try:
            # Log current state for debugging
            stage = state.get('stage')
            awaiting = state.get('awaiting_user')
            verified = state.get('is_verified')
            payment_status = state.get('payment_status')
            
            print(f"[DEBUG] Before invoke - Stage: {stage}, Awaiting: {awaiting}, Payment: {payment_status}")
            
            # Process current state through LangGraph
            state = app.invoke(state, config={"recursion_limit": 25})
            
            print(f"[DEBUG] After invoke - Stage: {state.get('stage')}, Awaiting: {state.get('awaiting_user')}, Payment: {state.get('payment_status')}")
            
            # Display agent's response
            messages = state.get("messages", [])
            if messages and messages[-1]["role"] == "assistant":
                print(f"Agent: {messages[-1]['content']}\n")
            
            # Exit if conversation completed
            if state.get("is_complete"):
                break
            
            # Get user input when agent is waiting
            if state.get("awaiting_user"):
                user_input = input("You: ").strip()
                
                # Handle empty input
                if user_input == "":
                    print("(Please provide a response)\n")
                    continue
                
                # Allow user to exit
                if user_input.lower() in ["quit", "exit"]:
                    print("\nCall ended by user.")
                    break
                
                # Update state with user input
                state["messages"].append({
                    "role": "user",
                    "content": user_input
                })
                state["last_user_input"] = user_input
                state["awaiting_user"] = False
            else:
                # Validate state consistency
                current_stage = state.get("stage")
                
                # Warn if stage should be awaiting input but isn't
                if current_stage in ["greeting", "verification", "disclosure", "negotiation"]:
                    print(f"\n[WARNING] Stage '{current_stage}' should be awaiting user input")
                
                # Safety check for unexpected states
                if not state.get("awaiting_user") and not state.get("is_complete"):
                    print(f"\n[DEBUG] Unexpected state - ending call")
                    break
                
        except Exception as e:
            print(f"\nError during call: {e}")
            import traceback
            traceback.print_exc()
            break

    print("\n=== Call Summary ===")
    print(f"Outcome: {state.get('call_outcome', 'unknown')}")
    print(f"Verified: {state.get('is_verified')}")
    print(f"Payment Status: {state.get('payment_status')}")
    if state.get("call_summary"):
        print(f"\n{state['call_summary']}")


if __name__ == "__main__":
    main()