# src/state.py

from typing import TypedDict, List, Optional, Literal
from src.data import get_customer_with_loan


Stage = Literal[
    "init",
    "greeting",
    "verification",
    "verified",
    "disclosure",
    "payment_check",
    "already_paid",
    "dispute",
    "negotiation",
    "ptp_recording",
    "escalation",
    "closing",
]

PaymentStatus = Literal[
    "paid",
    "disputed",
    "unable",
    "willing",
    "callback",
    "unknown",
]


# =========================
# Call State
# =========================
class CallState(TypedDict):
    """Complete state for a debt collection call conversation."""
    # === Conversation ===
    messages: List[dict]  # Conversation history
    stage: Stage  # Current conversation stage
    turn_count: int  # Number of conversation turns
    last_user_input: Optional[str]  # Most recent user message
    awaiting_user: bool  # Whether agent is waiting for user input
    has_greeted: bool  # Whether greeting has been sent
    has_disclosed: bool  # Whether legal disclosure has been provided
    
    # === Customer Info ===
    customer_id: str  # Unique customer identifier
    customer_name: str  # Customer's name
    customer_phone: str  # Customer's phone number
    customer_dob: str  # Customer's date of birth (for verification)
    
    # === Loan Info ===
    loan_id: str  # Loan identifier
    loan_type: str  # Type of loan (e.g., "Personal Loan")
    outstanding_amount: float  # Amount owed
    days_past_due: int  # Days overdue
    
    # === Verification ===
    verification_attempts: int  # Number of verification attempts
    is_verified: bool  # Whether customer identity is verified
    
    # === Payment Handling ===
    payment_status: Optional[PaymentStatus]  # Customer's payment intent
    
    # === Promise To Pay ===
    ptp_amount: Optional[float]  # Committed payment amount
    ptp_date: Optional[str]  # Committed payment date
    ptp_id: Optional[str]  # PTP reference number
    
    # === Dispute ===
    dispute_reason: Optional[str]  # Reason for dispute
    dispute_id: Optional[str]  # Dispute ticket ID
    
    # === Negotiation ===
    offered_plans: List[dict]  # Payment plans offered to customer
    selected_plan: Optional[dict]  # Plan selected by customer
    
    # === Call Outcome ===
    call_outcome: Optional[str]  # Final call result
    call_summary: Optional[str]  # Summary of the call
    
    # === Flags ===
    is_complete: bool  # Whether conversation is finished


# =========================
# Initial State Factory
# =========================
def create_initial_state(phone: str) -> Optional[CallState]:
    """
    Create initial CallState using mock customer + loan data.
    Returns None if customer not found.
    """
    data = get_customer_with_loan(phone)
    if not data:
        return None
    
    customer = data["customer"]
    loan = data["loan"]
    
    return CallState(
        # Conversation
        messages=[],
        stage="init",
        turn_count=0,
        last_user_input=None,
        awaiting_user=False,
        has_greeted=False,
        has_disclosed=False,
        
        # Customer
        customer_id=customer["id"],
        customer_name=customer["name"],
        customer_phone=customer["phone"],
        customer_dob=customer["dob"],
        
        # Loan
        loan_id=loan["id"],
        loan_type=loan["type"],
        outstanding_amount=loan["outstanding"],
        days_past_due=loan["days_past_due"],
        
        # Verification
        verification_attempts=0,
        is_verified=False,
        
        # Payment
        payment_status=None,
        
        # PTP
        ptp_amount=None,
        ptp_date=None,
        ptp_id=None,
        
        # Dispute
        dispute_reason=None,
        dispute_id=None,
        
        # Negotiation
        offered_plans=[],
        selected_plan=None,
        
        # Outcome
        call_outcome=None,
        call_summary=None,
        
        # Flags
        is_complete=False,
    )