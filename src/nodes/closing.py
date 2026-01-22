# src/nodes/closing.py

from ..state import CallState
from ..data import save_call_record, save_dispute, save_ptp


def closing_node(state: CallState) -> dict:
    """
    End the call professionally and record outcome.
    Handles different payment statuses with appropriate closing messages.
    """
    # Get payment status from state
    payment_status = state.get("payment_status", "completed")
    
    print(f"[CLOSING] Closing node called. payment_status={payment_status}, is_complete={state.get('is_complete')}, stage={state.get('stage')}")
    
    # Generate closing message based on payment status
    if payment_status == "paid":
        # Check if payment proof screenshot has been uploaded
        messages = state.get("messages", [])
        has_screenshot = any(
            msg.get("content", "").startswith("[Screenshot uploaded:") 
            for msg in messages
        )
        
        print(f"[CLOSING] Payment status is 'paid'. Has screenshot: {has_screenshot}")
        print(f"[CLOSING] Messages count: {len(messages)}")
        
        if not has_screenshot:
            # Request payment proof before closing
            closing_message = (
                "Aapke payment confirm karne ke liye dhanyawad. "
                "Jaldi verify aur process karne ke liye, kripya payment ka proof attachment ke roop mein upload karein "
                "(payment receipt/transaction ka screenshot ya image). "
                "Aap neeche attachment button (📎) use karke apna proof upload kar sakte hain."
            )
            outcome = "paid"
            print(f"[CLOSING] Returning early - asking for proof. is_complete=False, awaiting_user=True")
            # Don't complete yet - wait for screenshot upload
            return {
                "messages": state["messages"] + [{
                    "role": "assistant",
                    "content": closing_message
                }],
                "call_outcome": outcome,
                "stage": "closing",
                "awaiting_user": True,  # Wait for screenshot upload
                "is_complete": False,  # Don't complete until screenshot is uploaded
            }
        else:
            # Screenshot uploaded, show final closing message
            print(f"[CLOSING] Screenshot found - showing final closing message")
            closing_message = (
                "Payment proof dene ke liye dhanyawad. "
                "Humne aapka attachment receive kar liya hai aur hum ise verify karenge. "
                "Verification complete hone ke baad aapka account accordingly update ho jayega. "
                "Agar aapke paas koi sawaal hain, toh kripya humse contact karein. "
                "Aapka din achha rahe."
            )
            outcome = "paid"
        
    elif payment_status == "disputed":
        # Extract dispute reason from user messages
        dispute_reason = state.get("last_user_input")
        if not dispute_reason:
            # Find the user message that triggered the dispute
            messages = state.get("messages", [])
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    dispute_reason = msg.get("content", "Customer disputes the debt")
                    break
        if not dispute_reason:
            dispute_reason = "Customer disputes the debt"
        
        # Save dispute ticket
        dispute_id = save_dispute(state["customer_id"], dispute_reason)
        
        closing_message = (
            "Main samajh gaya hoon ki aap is debt ko dispute kar rahe hain. "
            f"Maine ek dispute ticket create kar diya hai (Reference: {dispute_id}). "
            "Hamara disputes team ise review karega aur 3-5 business days mein aapse contact karega. "
            "Is matter ko hamare attention mein lane ke liye dhanyawad."
        )
        outcome = "disputed"
        state["dispute_id"] = dispute_id
        state["dispute_reason"] = dispute_reason
        
    elif payment_status == "callback":
        closing_message = (
            "Koi baat nahi, main samajh gaya hoon ki aapko aur time chahiye. "
            "Hum aapko requested time par call back karenge. "
            "Aaj aapka time dene ke liye dhanyawad."
        )
        outcome = "callback"
        
    elif payment_status == "unable":
        closing_message = (
            "Main aapki current financial situation samajh raha hoon. "
            "Hamara team aapke case ko review karega aur possible options discuss karne ke liye aapse contact karega. "
            "Aaj hamare saath honest rehne ke liye dhanyawad."
        )
        outcome = "unable"
        
    elif payment_status == "willing":
        # Check if PTP was already recorded in negotiation node
        if state.get("ptp_id"):
            # PTP already saved - show confirmation with reference number
            ptp_id = state.get("ptp_id")
            ptp_amount = state.get("ptp_amount")
            ptp_date = state.get("ptp_date")
            plan_name = state.get("selected_plan", {}).get("name", "Payment Plan") if state.get("selected_plan") else "Payment Plan"
            
            closing_message = (
                f"Perfect! Maine aapka commitment document kar diya hai - {plan_name} "
                f"ke saath ₹{ptp_amount:,.0f} ki payment {ptp_date} se shuru hogi. "
                f"Aapka PTP reference number hai {ptp_id}. "
                f"Aapko jaldi hi confirmation mil jayega. Is matter ko resolve karne ke liye dhanyawad. Aapka din achha rahe!"
            )
            outcome = "ptp_recorded"
        else:
            # Customer willing but no specific commitment yet
            closing_message = (
                "Aaj hamare saath is matter par discuss karne ke liye dhanyawad. "
                "Hamari conversation ke basis par, hum jaldi hi aapke saath follow-up karke payment arrangement finalize karenge. "
                "Agar aap usse pehle payment proceed karna chahte hain, toh kripya humse contact karein. "
                "Aapka din achha rahe."
            )
            outcome = "willing"
        
    else:
        # Fallback for any unexpected status
        closing_message = (
            "Aaj aapka time dene ke liye dhanyawad. "
            "Agar aapke paas koi sawaal hain, toh kripya humse contact karein. "
            "Aapka din achha rahe."
        )
        outcome = payment_status or "completed"

    # Create call summary for records
    summary = f"""
Call completed.
Verified: {state['is_verified']}
Outcome: {outcome}
Payment Status: {payment_status}
Customer: {state['customer_name']}
Outstanding Amount: ₹{state['outstanding_amount']}
"""

    # Persist call record
    save_call_record({
        "customer_id": state["customer_id"],
        "outcome": outcome,
        "payment_status": payment_status,
        "summary": summary.strip()
    })

    return {
        "messages": state["messages"] + [{
            "role": "assistant",
            "content": closing_message
        }],
        "call_outcome": outcome,
        "call_summary": summary.strip(),
        "is_complete": True,
        "stage": "closing",
    }