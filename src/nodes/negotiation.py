# src/nodes/negotiation.py

from ..state import CallState
from ..utils.llm import generate_negotiation_response, generate_payment_plans
from ..data import save_ptp
from datetime import datetime, timedelta
import re


def extract_amount(text: str) -> float:
    """Extract monetary amount from text."""
    # Remove commas and normalize currency symbols
    text = text.replace(',', '').replace('₹', '').replace('Rs', '').replace('rs', '')
    
    # Try to find amounts with currency context (₹, Rs, rupees, etc.)
    amount_patterns = [
        r'₹\s*(\d+(?:\.\d+)?)',  # ₹45000
        r'rs\.?\s*(\d+(?:\.\d+)?)',  # Rs 45000 or Rs. 45000
        r'rupees?\s*(\d+(?:\.\d+)?)',  # rupees 45000
        r'(\d+(?:\.\d+)?)\s*(?:rupees?|rs|₹)',  # 45000 rupees
        r'(\d+(?:,\d+)*(?:\.\d+)?)',  # 45,000 or 45000
    ]
    
    for pattern in amount_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Handle comma-separated numbers
            amount_str = str(match).replace(',', '')
            try:
                amount = float(amount_str)
                # Filter out years (4-digit numbers between 1900-2020 are likely years, not amounts)
                if 1900 <= amount <= 2020:
                    continue  # This is likely a year, not an amount
                if amount > 100:  # Reasonable minimum for debt payment
                    return amount
            except ValueError:
                continue
    
    return None


def extract_date(text: str) -> str:
    """Extract date from text in various formats."""
    text_lower = text.lower()
    
    months_map = {
        'jan': '01', 'january': '01',
        'feb': '02', 'february': '02',
        'mar': '03', 'march': '03',
        'apr': '04', 'april': '04',
        'may': '05',
        'jun': '06', 'june': '06',
        'jul': '07', 'july': '07',
        'aug': '08', 'august': '08',
        'sep': '09', 'september': '09',
        'oct': '10', 'october': '10',
        'nov': '11', 'november': '11',
        'dec': '12', 'december': '12',
    }
    
    # Try to find month name first
    for month_name, month_num in months_map.items():
        if month_name in text_lower:
            # Pattern: "5th January", "5 January", "January 5th", "January 5", "Jan 5th"
            day_match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s*' + month_name, text_lower)
            if not day_match:
                day_match = re.search(month_name + r'\s*(\d{1,2})(?:st|nd|rd|th)?', text_lower)
            
            if day_match:
                day = day_match.group(1)
                if 1 <= int(day) <= 31:
                    year_match = re.search(r'20\d{2}', text)
                    year = year_match.group(0) if year_match else "2025"
                    return f"{day.zfill(2)}-{month_num}-{year}"
    
    # Try DD-MM-YYYY or DD/MM/YYYY format (with or without year)
    # Match dates with full year (4 digits) - this includes DOB dates
    date_pattern_full = r'(\d{1,2})[-/\s](\d{1,2})[-/\s](\d{4})'
    match_full = re.search(date_pattern_full, text)
    if match_full:
        day, month, year = match_full.groups()
        year_int = int(year)
        # Filter out DOB dates (years before 2020 are likely DOB, not commitment dates)
        if year_int < 2020:
            return None  # This is a DOB, not a commitment date
        if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
            return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
    
    # Try DD-MM-YYYY or DD/MM/YYYY format without year (defaults to 2025)
    date_pattern = r'(\d{1,2})[-/\s](\d{1,2})(?![-/\s]?\d{4})'
    match = re.search(date_pattern, text)
    if match:
        day, month = match.groups()
        if 1 <= int(day) <= 31 and 1 <= int(month) <= 12:
            year = "2025"  # Default to current/future year
            return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
    
    # Try relative dates: "tomorrow", "next week", "next month", "15th", etc.
    today = datetime.now()
    
    if "tomorrow" in text_lower:
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime("%d-%m-%Y")
    elif "day after tomorrow" in text_lower:
        day_after = today + timedelta(days=2)
        return day_after.strftime("%d-%m-%Y")
    elif "next week" in text_lower or "week from now" in text_lower:
        next_week = today + timedelta(days=7)
        return next_week.strftime("%d-%m-%Y")
    elif "next month" in text_lower or "month from now" in text_lower:
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1)
        else:
            next_month = today.replace(month=today.month + 1)
        return next_month.strftime("%d-%m-%Y")
    
    # Try standalone day numbers (e.g., "15th", "15")
    day_only_match = re.search(r'\b(\d{1,2})(?:st|nd|rd|th)?\b', text_lower)
    if day_only_match and not any(month in text_lower for month in months_map.keys()):
        day = int(day_only_match.group(1))
        if 1 <= day <= 31:
            # Assume current or next month
            if day >= today.day:
                target_date = today.replace(day=day)
            else:
                if today.month == 12:
                    target_date = today.replace(year=today.year + 1, month=1, day=day)
                else:
                    target_date = today.replace(month=today.month + 1, day=day)
            return target_date.strftime("%d-%m-%Y")
    
    return None


def has_commitment_details(state: CallState, last_user_input: str) -> tuple:
    """
    Check if customer has provided both amount and date commitment.
    Returns (has_both, amount, date, plan_selected)
    """
    messages = state.get("messages", [])
    offered_plans = state.get("offered_plans", [])
    
    committed_amount = None
    committed_date = None
    selected_plan = None
    
    # Find where verification ended
    verification_done_index = -1
    for i, msg in enumerate(messages):
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            if "thank you for confirming" in content or "outstanding payment" in content:
                verification_done_index = i
    
    # Find where plans were offered
    plan_offer_index = -1
    for i, msg in enumerate(messages):
        if msg.get("role") == "assistant" and i > verification_done_index:
            if "option" in msg.get("content", "").lower() or "installment" in msg.get("content", "").lower():
                plan_offer_index = i
                break
    
    start_index = max(plan_offer_index, verification_done_index + 1) if plan_offer_index >= 0 else verification_done_index + 1
    relevant_messages = messages[start_index:] if start_index >= 0 else messages[-3:]
    
    print(f"[COMMITMENT] Checking {len(relevant_messages)} messages after plans offered")
    if offered_plans:
        print(f"[COMMITMENT] Available plans: {[p['name'] for p in offered_plans]}")
    
    for msg in relevant_messages:
        if msg.get("role") == "user":
            content = msg.get("content", "").lower()
            
            print(f"[COMMITMENT] Analyzing user message: '{content}'")
            
            if offered_plans and not selected_plan:
                print(f"[COMMITMENT] Plans available: {len(offered_plans)}")
                # Try to match by month count (e.g., "3 month", "3-month", "three month")
                month_match = re.search(r'(\d+)\s*[-]?\s*month', content)
                if month_match:
                    months = int(month_match.group(1))
                    print(f"[PLAN DETECTION] Found {months}-month mention in: '{content}'")
                    for idx, plan in enumerate(offered_plans):
                        plan_name_lower = plan['name'].lower()
                        plan_desc_lower = plan['description'].lower()
                        
                        print(f"[PLAN DETECTION] Checking plan {idx+1}: '{plan_name_lower}' / '{plan_desc_lower}'")
                        
                        matches = (
                            f"{months}-month" in plan_name_lower or
                            f"{months} month" in plan_desc_lower or
                            f"{months}month" in plan_name_lower.replace("-", "").replace(" ", "") or
                            (str(months) in plan_name_lower and "month" in plan_name_lower)
                        )
                        
                        if matches:
                            selected_plan = plan
                            print(f"[PLAN DETECTION] OK: Matched to plan: {plan['name']}")
                            amount_match = re.search(r'₹(\d+(?:,\d+)*)', plan['description'])
                            if amount_match:
                                committed_amount = float(amount_match.group(1).replace(',', ''))
                                print(f"[PLAN DETECTION] Amount: ₹{committed_amount:,.0f}")
                            break
                        else:
                            print(f"[PLAN DETECTION] No match for {months} months")
                
                # Try to match by plan/option number (e.g., "plan 1", "option 2", "1st plan")
                if not selected_plan:
                    plan_num_match = re.search(r'(?:plan|option|choice)\s*(\d+)', content)
                    if plan_num_match:
                        plan_idx = int(plan_num_match.group(1)) - 1
                        print(f"[PLAN DETECTION] Plan number {plan_idx + 1} selected")
                        if 0 <= plan_idx < len(offered_plans):
                            selected_plan = offered_plans[plan_idx]
                            print(f"[PLAN DETECTION] Matched to: {selected_plan['name']}")
                            amount_match = re.search(r'₹(\d+(?:,\d+)*)', selected_plan['description'])
                            if amount_match:
                                committed_amount = float(amount_match.group(1).replace(',', ''))
                
                # Try to match by position words (first, second, third, etc.)
                if not selected_plan:
                    position_keywords = [
                        ('first', 0), ('1st', 0), ('one', 0),
                        ('second', 1), ('2nd', 1), ('two', 1),
                        ('third', 2), ('3rd', 2), ('three', 2),
                        ('fourth', 3), ('4th', 3), ('four', 3)
                    ]
                    for keyword, idx in position_keywords:
                        if keyword in content:
                            if idx < len(offered_plans):
                                selected_plan = offered_plans[idx]
                                print(f"[PLAN DETECTION] Position-based selection ({keyword}): {selected_plan['name']}")
                                amount_match = re.search(r'₹(\d+(?:,\d+)*)', selected_plan['description'])
                                if amount_match:
                                    committed_amount = float(amount_match.group(1).replace(',', ''))
                            break
                
                # Try to match by acceptance phrases (works for me, sounds good, etc.)
                if not selected_plan:
                    acceptance_phrases = [
                        'works for me', 'i\'ll take', 'sounds good', 'that works', 'i accept',
                        'i agree', 'that\'s fine', 'that\'s good', 'okay', 'ok', 'sure',
                        'yes', 'yeah', 'i\'ll go with', 'i choose', 'i select', 'i pick',
                        'let\'s go with', 'let us go with', 'i\'d like', 'i would like'
                    ]
                    if any(phrase in content for phrase in acceptance_phrases):
                        print("[PLAN DETECTION] Acceptance phrase detected")
                        msg_index = messages.index(msg)
                        if msg_index > 0:
                            prev_msg = messages[msg_index - 1]
                            if prev_msg.get("role") == "assistant" and ("option" in prev_msg.get("content", "").lower() or "plan" in prev_msg.get("content", "").lower()):
                                # Default to second plan if available, otherwise first
                                if len(offered_plans) > 1:
                                    selected_plan = offered_plans[1]
                                else:
                                    selected_plan = offered_plans[0]
                                
                                print(f"[PLAN DETECTION] Assumed plan: {selected_plan['name']}")
                                amount_match = re.search(r'₹(\d+(?:,\d+)*)', selected_plan['description'])
                                if amount_match:
                                    committed_amount = float(amount_match.group(1).replace(',', ''))
                
                # Try to match by plan name keywords
                if not selected_plan:
                    for plan in offered_plans:
                        plan_name_words = set(plan['name'].lower().split())
                        content_words = set(content.split())
                        # If significant overlap in keywords, consider it a match
                        if len(plan_name_words & content_words) >= 2:
                            selected_plan = plan
                            print(f"[PLAN DETECTION] Keyword-based match: {plan['name']}")
                            amount_match = re.search(r'₹(\d+(?:,\d+)*)', plan['description'])
                            if amount_match:
                                committed_amount = float(amount_match.group(1).replace(',', ''))
                            break
            
            if not committed_date:
                date = extract_date(content)
                if date:
                    # Filter out DOB dates (dates before 2020 are likely DOB, not commitment dates)
                    date_parts = date.split('-')
                    if len(date_parts) == 3:
                        year = int(date_parts[2])
                        # Only accept dates from 2020 onwards (commitment dates should be future dates)
                        if year >= 2020:
                            committed_date = date
                            print(f"[DATE DETECTION] Found date: {date}")
                        else:
                            print(f"[DATE DETECTION] Ignoring past date (likely DOB): {date}")
            
            if not committed_amount and not selected_plan:
                amount = extract_amount(content)
                if amount:
                    committed_amount = amount
                    print(f"[AMOUNT DETECTION] Found explicit amount: {amount}")
    
    # If we have a date but no amount/plan, and user expressed willingness to pay, use full outstanding amount
    if committed_date and not committed_amount and not selected_plan:
        # Check if user expressed willingness to pay (various phrasings)
        all_user_messages = [msg.get("content", "").lower() for msg in messages if msg.get("role") == "user"]
        willingness_phrases = [
            "i want to pay", "ready to pay", "will pay", "can pay", "i'll pay",
            "want to pay", "willing to pay", "prepared to pay", "ready to make payment",
            "can make payment", "will make payment", "i can pay", "i will pay",
            "let's pay", "let us pay", "i'd like to pay", "i would like to pay"
        ]
        if any(phrase in msg for msg in all_user_messages for phrase in willingness_phrases):
            committed_amount = state.get("outstanding_amount")
            print(f"[COMMITMENT] Direct payment commitment detected, using full amount: ₹{committed_amount:,.0f}")
    
    has_both = committed_amount is not None and committed_date is not None
    
    print(f"[COMMITMENT] Final - Amount: {committed_amount}, Date: {committed_date}, Plan: {selected_plan['name'] if selected_plan else None}")
    
    return has_both, committed_amount, committed_date, selected_plan


def negotiation_node(state: CallState) -> dict:
    """
    Have an intelligent conversation with the customer about payment.
    Detects when customer commits to amount AND date, then moves to closing.
    """

    # Guardrail: Validate state structure
    if not isinstance(state, dict):
        raise ValueError("Invalid state: state must be a dictionary")
    
    # Guardrail: Validate verification status
    if not state.get("is_verified"):
        raise ValueError("Invalid state: User must be verified before negotiation")
    
    # Guardrail: Validate required fields
    if "outstanding_amount" not in state:
        raise ValueError("Invalid state: outstanding_amount is required")
    
    if "customer_name" not in state or not state.get("customer_name"):
        raise ValueError("Invalid state: customer_name is required")
    
    if "customer_id" not in state:
        raise ValueError("Invalid state: customer_id is required")
    
    # Guardrail: Validate outstanding amount
    amount = state["outstanding_amount"]
    if not isinstance(amount, (int, float)) or amount < 0:
        raise ValueError("Invalid state: outstanding_amount must be a non-negative number")
    
    # Guardrail: Sanitize customer name
    customer_name = str(state["customer_name"]).strip()
    if not customer_name:
        raise ValueError("Invalid state: customer_name cannot be empty")
    
    customer_name = customer_name.split()[0]
    
    last_user_input = state.get("last_user_input") or ""
    messages = state.get("messages", [])
    
    negotiation_turns = 0
    in_negotiation = False
    for msg in messages:
        if msg.get("role") == "assistant":
            content = msg.get("content", "").lower()
            if "outstanding payment" in content or "able to make this payment" in content:
                in_negotiation = False
            elif in_negotiation or any(keyword in content for keyword in ["option", "installment", "plan", "appreciate your willingness"]):
                in_negotiation = True
                negotiation_turns += 1
    
    print(f"[NEGOTIATION] Turn {negotiation_turns + 1}, User input: '{last_user_input}'")
    
    commitment_result = has_commitment_details(state, last_user_input)
    has_both, committed_amount, committed_date, selected_plan = commitment_result
    
    # If we have both - CLOSE IMMEDIATELY
    if has_both:
        print(f"[NEGOTIATION] OK: Full commitment received - CLOSING NOW")
        
        # Guardrail: Validate commitment data before saving
        if not committed_amount or committed_amount <= 0:
            raise ValueError("Invalid commitment: amount must be positive")
        
        if not committed_date:
            raise ValueError("Invalid commitment: date is required")
        
        # Save PTP record
        plan_name = selected_plan['name'] if selected_plan else "Custom Payment Plan"
        plan_type = plan_name  # Use plan name as plan_type
        ptp_id = save_ptp(
            customer_id=state["customer_id"],
            amount=committed_amount,
            date=committed_date,
            plan_type=plan_type
        )
        print(f"[NEGOTIATION] PTP saved with ID: {ptp_id}")
        
        response = (
            f"Perfect, {customer_name}. Maine aapka commitment document kar diya hai - {plan_name} "
            f"ke saath ₹{committed_amount:,.0f} ki payment {committed_date} se shuru hogi. "
            f"Aapka PTP reference number hai {ptp_id}. "
            f"Aapko jaldi hi confirmation mil jayega. Is matter ko resolve karne ke liye dhanyawad. Aapka din achha rahe!"
        )
        
        # Return with is_complete=True to END the call
        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": response
            }],
            "ptp_amount": committed_amount,
            "ptp_date": committed_date,
            "ptp_id": ptp_id,
            "selected_plan": selected_plan,
            "stage": "closing",
            "awaiting_user": False,
            "last_user_input": None,
            "payment_status": "willing",
            "call_outcome": "ptp_recorded",
            "is_complete": True,  # THIS ENDS THE CALL
        }
    
    if selected_plan and not committed_date:
        print(f"[NEGOTIATION] Plan selected, asking for date")
        response = (
            f"Bahut achha choice, {customer_name}! Maine {selected_plan['name']} note kar liya hai. "
            f"Aap pehli payment kab karna chahenge?"
        )
        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": response
            }],
            "stage": "negotiation",
            "awaiting_user": True,
            "last_user_input": None,
            "payment_status": "willing",
        }
    
    end_signals = ["no that's all", "no thanks bye", "goodbye", "bye bye", "nothing else", "that's all"]
    user_wants_to_end = any(signal in last_user_input.lower() for signal in end_signals)
    
    should_close = user_wants_to_end or negotiation_turns >= 8
    
    if should_close:
        print(f"[NEGOTIATION] Closing conversation (user_wants_to_end={user_wants_to_end}, turns={negotiation_turns})")
        response = (
            f"Dhanyawad, {customer_name}. Maine hamari discussion document kar di hai. "
            f"Hum jaldi hi aapke saath follow-up karke arrangement finalize kar denge. "
            f"Aapka din achha rahe."
        )
        return {
            "messages": state["messages"] + [{
                "role": "assistant",
                "content": response
            }],
            "stage": "negotiation",
            "awaiting_user": False,
            "last_user_input": None,
        }
    
    plan_request_keywords = [
        "payment plan", "installment", "emi", "monthly payment",
        "break it up", "pay in parts", "split", "work out a plan",
        "options", "what are my options", "can you offer"
    ]
    
    is_plan_request = any(keyword in last_user_input.lower() for keyword in plan_request_keywords)
    
    if negotiation_turns == 0 or (is_plan_request and not state.get("offered_plans")):
        try:
            plans = generate_payment_plans(amount, customer_name)
        except Exception as e:
            print(f"[NEGOTIATION] Error generating plans: {e}, using fallback")
            from ..utils.llm import generate_fallback_plans
            plans = generate_fallback_plans(amount)
        
        if plans and len(plans) > 0:
            if negotiation_turns == 0:
                response = f"Main aapki willingness ki kadar karta hoon, {customer_name}. Chaliye main aapko kuch options dikhata hoon:\n\n"
            else:
                response = f"Bilkul, {customer_name}. Yahan kuch payment options hain:\n\n"
            
            for i, plan in enumerate(plans, 1):
                # Remove any markdown asterisks from plan name
                clean_name = plan['name'].replace('**', '').strip()
                response += f"{i}. {clean_name}: {plan['description']}\n"
            
            response += f"\nAapke liye kaunsa option best rahega?"
            
            return {
                "offered_plans": plans,
                "messages": state["messages"] + [{
                    "role": "assistant",
                    "content": response
                }],
                "stage": "negotiation",
                "awaiting_user": True,
                "last_user_input": None,
                "payment_status": "willing",
            }
        else:
            return {
                "messages": state["messages"] + [{
                    "role": "assistant",
                    "content": (
                        f"Main aapki willingness ki kadar karta hoon, {customer_name}. "
                        f"Kya aap mujhe bata sakte hain ki monthly kitna amount aur kab ka date aapke liye theek rahega?"
                    )
                }],
                "stage": "negotiation",
                "awaiting_user": True,
                "last_user_input": None,
                "payment_status": "willing",
            }
    
    recent_conversation = ""
    for msg in messages[-6:]:
        role = "Agent" if msg["role"] == "assistant" else "Customer"
        recent_conversation += f"{role}: {msg['content']}\n"
    
    plans_context = ""
    if state.get("offered_plans"):
        plans_context = "\n\nOffered plans:\n"
        for plan in state["offered_plans"]:
            plans_context += f"- {plan['name']}: {plan['description']}\n"
    
    context = f"""Aap ek professional debt collection agent hain. Hinglish mein respond karein (Hindi aur English mix).

Customer: {customer_name}
Outstanding: ₹{amount:,.0f}

Recent conversation:
{recent_conversation}
{plans_context}

Customer ne kaha: "{last_user_input}"

Task: Naturally respond karein Hinglish mein. Agar unhone plan select kiya hai, confirm karein aur payment date puchhein. Agar unhone date mention kiya hai, confirm karein. Brief rahein (2-3 sentences).

Response:"""

    response = generate_negotiation_response(context)
    
    if not response:
        print("[NEGOTIATION] Using smart template fallback")
        
        if committed_date and not committed_amount and not selected_plan:
            response = (
                f"Us date ke liye dhanyawad, {customer_name}. "
                f"Kya aap confirm kar sakte hain ki kaunsa payment plan aapke liye best rahega?"
            )
        else:
            response = (
                f"Main aapke input ki kadar karta hoon, {customer_name}. "
                f"Ise finalize karne ke liye, kya aap payment plan aur date confirm kar sakte hain jo aapke liye theek ho?"
            )
    
    return {
        "messages": state["messages"] + [{
            "role": "assistant",
            "content": response
        }],
        "stage": "negotiation",
        "awaiting_user": True,
        "last_user_input": None,
        "payment_status": "willing",
    }