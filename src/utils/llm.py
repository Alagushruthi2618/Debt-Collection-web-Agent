"""
LLM utilities for intent classification and response generation.

Uses Azure OpenAI as primary classifier with rule-based fallback.
Supports Hinglish (Hindi-English mix) for Indian customers.
"""

from dotenv import load_dotenv
import os

# Disable LangSmith tracing to avoid rate limits
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

load_dotenv()

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://llm-3rdparty.cognitiveservices.azure.com/")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# Valid payment intent classifications
ALLOWED_INTENTS = [
    "paid",
    "disputed",
    "callback",
    "unable",
    "willing",
    "unknown",
]

# ------------------------------------------------------------------
# Azure OpenAI integration (PRIMARY CLASSIFIER)
# ------------------------------------------------------------------

_client_cache = None

def get_azure_openai_client():
    """
    Initialize and cache Azure OpenAI client (singleton pattern).
    Tests connection on first call.
    """
    global _client_cache
    
    if _client_cache is not None:
        return _client_cache
    
    try:
        from openai import AzureOpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    if not AZURE_OPENAI_API_KEY:
        raise RuntimeError("AZURE_OPENAI_API_KEY not set")

    try:
        print(f"[AZURE_OPENAI] Initializing client with endpoint: {AZURE_OPENAI_ENDPOINT}")
        print(f"[AZURE_OPENAI] Using deployment: {AZURE_OPENAI_DEPLOYMENT}")
        
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        
        # Test connection with simple request
        test_response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": "Say 'ok'"}],
            max_tokens=5
        )
        
        if test_response and test_response.choices and len(test_response.choices) > 0:
            print(f"[AZURE_OPENAI] OK: Successfully initialized client")
            _client_cache = client
            return _client_cache
        else:
            raise RuntimeError("Test response was empty")
            
    except Exception as e:
        print(f"[AZURE_OPENAI] ERROR: Failed to initialize: {str(e)[:200]}")
        raise RuntimeError(f"Azure OpenAI initialization failed: {e}")


def safe_get_response_text(response):
    """
    Safely extract text from Azure OpenAI response.
    Returns (text, was_blocked) tuple.
    """
    try:
        # Azure OpenAI response structure
        if not response or not hasattr(response, 'choices'):
            print("[AZURE_OPENAI] No choices in response")
            return None, True
        
        if len(response.choices) == 0:
            print("[AZURE_OPENAI] Empty choices list")
            return None, True
        
        choice = response.choices[0]
        
        # Check finish reason
        if hasattr(choice, 'finish_reason'):
            finish_reason = choice.finish_reason
            if finish_reason and finish_reason not in ['stop', 'length']:
                print(f"[AZURE_OPENAI] Unexpected finish reason: {finish_reason}")
                # Don't treat as blocked, but log it
        
        # Extract text from message content
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            text = choice.message.content
            if text and len(text.strip()) > 0:
                return text.strip(), False
        
        print("[AZURE_OPENAI] No text found in response")
        return None, True
        
    except Exception as e:
        print(f"[AZURE_OPENAI] Unexpected error extracting text: {type(e).__name__} - {e}")
        return None, True


def classify_intent_with_azure_openai(prompt: str) -> str:
    """
    Use Azure OpenAI to intelligently classify customer intent.
    Returns one of the ALLOWED_INTENTS.
    """
    
    try:
        client = get_azure_openai_client()
    except Exception as e:
        print(f"Error initializing Azure OpenAI: {e}")
        # Apply smart fallback when Azure OpenAI is unavailable
        rule_intent = classify_intent_rule_based(prompt)
        if rule_intent != "unknown":
            return rule_intent
        
        # Smart fallback: check for common patterns
        text_lower = prompt.lower()
        # Check for dispute patterns
        dispute_keywords = ["nahi hai", "nahi liya", "galat", "fraud", "wrong", "mistake", "not mine", "never took"]
        if any(kw in text_lower for kw in dispute_keywords):
            return "disputed"
        
        # Check for payment-related patterns
        if any(phrase in text_lower for phrase in ["pay", "payment", "emi", "installment", "plan"]):
            if any(phrase in text_lower for phrase in ["full", "nahi de sakta", "can't"]):
                return "willing"
            return "willing"
        
        # Check for callback patterns (but only if explicit)
        if any(phrase in text_lower for phrase in ["call karo", "call kar", "call me", "call back", "baad mein call", "kal call"]):
            return "callback"
        
        # Default fallback - ambiguous inputs should be "unknown"
        return "unknown"

    # Simplified prompt to avoid safety filters - Updated for Hinglish
    llm_prompt = f"""Classify this customer response in a debt collection call (customer may respond in Hinglish/Hindi/English).

Response: "{prompt}"

Categories (choose the best match):
- paid: Customer claims they already made payment (e.g., "I paid", "already cleared", "payment done", "transferred", "main ne pay kar diya", "payment ho gaya")
- disputed: Customer denies the debt or says it's wrong/not theirs (e.g., "never took", "not mine", "fraud", "wrong", "maine liya hi nahi", "yeh mera nahi hai")
- callback: Customer explicitly wants to be called back later (e.g., "call me later", "busy now", "not available", "out of town", "baad mein call karo", "abhi busy hoon")
- unable: Customer has no money/can't afford anything (e.g., "lost job", "no money", "can't afford", "struggling", "paise nahi hain", "afford nahi kar sakta")
- willing: Customer wants to pay but needs options (e.g., "can't pay full", "installment", "payment plan", "will pay", "ready to pay", "EMI chahiye", "payment plan de do", "pay kar sakta hoon")
- unknown: For ambiguous responses like greetings ("Hi", "Hello"), simple questions ("Kya?", "Kya hua?"), confirmations without context ("Haan", "Nahi", "Ok"), or requests for clarification ("Samajh nahi aaya", "Explain kar sakte hain?")

Important: 
- If customer says they want to pay but can't pay full amount, classify as "willing" (not "unable").
- If customer says they already paid, classify as "paid" (not "willing").
- For ambiguous responses (greetings, simple questions, confirmations without payment context), classify as "unknown" (not "callback", "disputed", or "unable").

Return ONE word only: paid, disputed, callback, unable, willing, or unknown

Classification:"""

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": llm_prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        if was_blocked or not text:
            print("Azure OpenAI classification blocked, using rule-based fallback")
            rule_intent = classify_intent_rule_based(prompt)
            
            # If rule-based found something, use it
            if rule_intent != "unknown":
                return rule_intent
            
            # Smart fallback for blocked cases
            text_lower = prompt.lower()
            dispute_keywords = ["not right", "doesnt seem", "doesn't seem", "wrong", "mistake", "not mine", "never took", "didn't take"]
            if any(kw in text_lower for kw in dispute_keywords):
                return "disputed"
            
            # If they mention payment but can't pay full, they're willing to negotiate
            if any(phrase in text_lower for phrase in ["can't pay", "cant pay", "cannot pay", "pay", "payment"]):
                if any(phrase in text_lower for phrase in ["full", "all", "complete", "entire"]):
                    return "willing"  # Willing to pay partial/negotiate
            
            # Default to unknown for ambiguous inputs
            return "unknown"
        
        intent = text.strip().lower()
        
        # Validate response
        if intent in ALLOWED_INTENTS:
            return intent
        
        # Try to extract valid intent from response
        for valid_intent in ALLOWED_INTENTS:
            if valid_intent in intent:
                return valid_intent
        
        # Fallback
        print(f"Warning: Azure OpenAI returned unexpected intent '{intent}'")
        rule_intent = classify_intent_rule_based(prompt)
        return rule_intent if rule_intent != "unknown" else "disputed"
        
    except Exception as e:
        print(f"Error in Azure OpenAI classification: {e}")
        rule_intent = classify_intent_rule_based(prompt)
        
        # If rule-based found something, use it
        if rule_intent != "unknown":
            return rule_intent
        
        # Smart fallback: check for common patterns
        text_lower = prompt.lower()
        dispute_keywords = ["not right", "doesnt seem", "doesn't seem", "wrong", "mistake", "not mine", "never took", "didn't take"]
        if any(kw in text_lower for kw in dispute_keywords):
            return "disputed"
        
        # If they mention payment but can't pay full, they're willing to negotiate
        if any(phrase in text_lower for phrase in ["can't pay", "cant pay", "cannot pay", "pay", "payment"]):
            if any(phrase in text_lower for phrase in ["full", "all", "complete", "entire"]):
                return "willing"  # Willing to pay partial/negotiate
        
        # Default to unknown for ambiguous inputs
        return "unknown"


# ------------------------------------------------------------------
# Rule-based intent classification (FALLBACK/SHORTCUT)
# ------------------------------------------------------------------

def classify_intent_rule_based(prompt: str) -> str:
    """
    Fast rule-based classification for obvious cases.
    Returns 'unknown' if uncertain - Gemini will handle these.
    """

    text = prompt.lower().strip()
    
    # First, check for ambiguous/unknown inputs (greetings, questions, confirmations)
    # These should be classified as "unable" (which maps to unknown) before checking other patterns
    ambiguous_patterns = [
        # Simple greetings
        "hi", "hello", "hey",
        # Simple questions (single word or very short)
        "kya?", "kaise?", "kyun?", "kahan?", "kab?", "kaun?", "kya hua?", "kya baat hai?",
        # Confirmation words (without context)
        "haan", "nahi", "theek hai", "achha", "ok", "okay",
        # Requests for clarification
        "samajh nahi aaya", "aap kya keh rahe hain?", "aap kya bol rahe hain?",
        "explain kar sakte hain?", "kya matlab hai?", "mujhe samajh nahi aaya",
        # Wait phrases
        "wait", "ruko", "thoda ruko", "ek minute", "just a moment",
        # Generic responses
        "batao", "suno", "dekho",
        # Identity questions
        "yeh kaun hai?"
    ]
    
    # Check if input is exactly one of these ambiguous patterns
    if text in ambiguous_patterns:
        return "unknown"
    
    # Check if input is very short (1-3 words) and matches ambiguous patterns
    words = text.split()
    if len(words) <= 3:
        # Check if it's a simple greeting
        if text in ["hi", "hello", "hey"]:
            return "unknown"
        # Check if it's a simple confirmation without payment context
        if text in ["haan", "nahi", "ok", "okay", "theek hai", "achha"]:
            return "unknown"
        # Check for single-word questions
        if text.endswith("?") and len(words) <= 2:
            question_words = ["kya", "kaise", "kyun", "kahan", "kab", "kaun", "kya hua", "kya baat hai"]
            if any(qw in text for qw in question_words):
                return "unknown"
        # Check for wait phrases
        if any(phrase in text for phrase in ["wait", "ruko", "thoda ruko", "ek minute", "just a moment"]):
            return "unknown"
        # Check for clarification requests
        if any(phrase in text for phrase in ["samajh nahi", "kya matlab", "explain", "yeh kaun hai"]):
            return "unknown"

    # Very clear "already paid" signals (including Hinglish)
    if any(phrase in text for phrase in [
        "already paid", "already made payment", "already cleared",
        "payment done", "payment made", "payment cleared", "payment completed",
        "i paid", "i've paid", "i have paid", "i made payment", "i cleared",
        "paid last week", "paid yesterday", "paid today", "paid it",
        "made the payment", "cleared the payment", "settled the payment",
        "transferred", "transferred the amount", "sent the money",
        "payment was made", "payment is done", "already settled",
        "cleared my dues", "paid my dues", "settled my account",
        # Hinglish phrases - expanded patterns
        "main ne pay kar diya", "payment ho gaya", "payment kar diya",
        "main ne payment kar di", "payment clear ho gaya", "dues clear kar di",
        "main ne transfer kar diya", "amount transfer ho gaya", "paise bhej diye",
        "main ne pehle hi payment kar diya", "pehle hi payment", "pehle hi pay",
        "payment ho gaya hai", "payment kar diya hai", "payment kar di thi",
        "transfer kar diya", "amount transfer", "transfer ho chuka",
        "dues clear ho gaye", "clear ho gaye hain", "dues clear",
        "sab paise de diye", "full amount pay kar diya", "loan clear kar diya",
        "pehle hi settle kar diya", "settle kar diya", "settle ho gaya",
        "payment receipt bhej di", "receipt bhej di", "proof bhej diya",
        "payement successfull ho gya", "payment successful ho gaya", "payment success ho gaya",
        "upi se transfer", "bank se payment", "cheque bhej diya",
        "online payment kar diya", "payment done hai", "emi pay kar di",
        "account clear ho gaya", "payment process ho gaya", "payment confirm",
        "amount deduct ho gaya", "payment kar di thi kal", "receipt mil gaya",
        # Additional patterns for successful payments
        "transaction complete ho gaya", "payment successful ho gaya",
        "transaction complete", "payment successful", "payment successful hai",
        "transaction successful", "transaction successful hai", "complete ho gaya",
        "successful ho gaya", "successfully done", "successfully completed"
    ]):
        return "paid"

    # Very clear financial hardship signals (including Hinglish)
    # Check this BEFORE dispute to avoid false positives
    if any(phrase in text for phrase in [
        "lost my job", "lost job", "no job", "unemployed", "jobless",
        "no money", "no funds", "no cash", "broke", "out of money",
        "can't afford", "cant afford", "cannot afford", "unable to afford",
        "financial crisis", "financial difficulty", "financial trouble",
        "struggling", "struggling financially", "going through tough times",
        "difficult situation", "hard time", "tough time",
        "no income", "no salary", "no earnings", "no source of income",
        "medical emergency", "family emergency", "emergency expenses",
        # Hinglish phrases - expanded patterns
        "naukri chali gayi", "job nahi hai", "paise nahi hain",
        "afford nahi kar sakta", "paisa nahi hai", "financial problem hai",
        "mushkil mein hoon", "paise ki problem hai", "income nahi hai",
        # Additional patterns for inability to pay
        "kuch bhi pay nahi kar sakta", "kuch nahi de sakta", "kuch bhi nahi de sakta",
        "paise nahi de sakta", "pay nahi kar sakta", "payment nahi kar sakta",
        "salary bandh ho gayi", "salary bandh", "income source bandh",
        "savings khatam ho gayi", "savings khatam", "funds khatam",
        "financial condition theek nahi", "financial situation kharab",
        "financial condition kharab", "financial situation theek nahi",
        "financially weak", "financially unstable", "financially unable",
        "funds available nahi", "resources nahi hain", "money available nahi",
        "paise de sakta right now", "abhi paise nahi", "right now paise nahi",
        "job chali gayi", "naukri chali gayi hai", "income source bandh ho gayi",
        "mere paas funds nahi", "mere paas money nahi", "mere paas paise nahi",
        "main financially struggling", "main financially weak", "main financially unstable"
    ]):
        return "unable"

    # Very clear dispute signals (including Hinglish)
    # IMPORTANT: Exclude financial hardship phrases to avoid false positives
    dispute_phrases = [
        "never took", "never borrowed", "never applied", "never had",
        "haven't taken", "havent taken", "didn't take", "didnt take",
        "not my loan", "not my account", "not my debt", "not mine",
        "don't owe", "dont owe", "do not owe", "i don't owe",
        "this is wrong", "this is incorrect", "this is not mine",
        "this is not my", "this doesn't belong", "this is fraud",
        "i didn't take", "i never took", "i never borrowed",
        "doesn't seem right", "doesnt seem right", "does not seem right",
        "not right", "seems wrong", "looks wrong", "appears wrong",
        "mistake", "error", "fraud", "fraudulent", "identity theft",
        "someone else", "wrong person", "not me", "i don't know about this",
        "i never applied", "i never signed", "unauthorized", "not authorized",
        # Hinglish phrases - expanded patterns
        "maine liya hi nahi", "yeh mera nahi hai", "yeh galat hai",
        "maine kabhi nahi liya", "yeh meri loan nahi hai", "yeh fraud hai",
        "mujhe nahi pata", "galat person", "yeh mera account nahi hai",
        "yeh loan mera nahi", "loan mera nahi hai", "yeh loan kabhi nahi liya",
        "yeh galat hai mujhe", "kuch nahi dena", "fraud lagta hai",
        "yeh mera account nahi", "loan apply nahi kiya", "kabhi yeh loan nahi",
        "yeh mistake hai", "wrong person hai", "yeh debt nahi liya",
        "unauthorized transaction", "loan sign nahi kiya", "identity theft lagta",
        "loan approve nahi kiya", "meri responsibility nahi", "loan accept nahi",
        "error hai system", "loan acknowledge nahi", "meri liability nahi",
        "loan authorize nahi", "fake loan hai", "loan verify nahi",
        "meri mistake nahi", "loan process nahi", "wrong account hai",
        "loan document nahi sign", "meri fault nahi", "loan agree nahi",
        "incorrect information hai"
    ]
    
    if any(phrase in text for phrase in dispute_phrases):
        # Exclude if it's clearly about financial hardship/condition (not loan denial)
        financial_hardship_context = [
            "financial condition", "financial situation", "financial problem",
            "financially", "income", "salary", "funds", "savings", "paise",
            "naukri", "job", "struggling", "weak", "unstable", "crisis"
        ]
        # Only exclude if the phrase is clearly about financial condition AND doesn't contain loan denial words
        if any(context in text for context in financial_hardship_context):
            # Check if it's actually about loan denial (contains loan/debt/account denial words)
            loan_denial_words = ["loan", "debt", "account", "mera nahi", "meri nahi", 
                                "liya", "kiya", "sign", "approve", "apply"]
            if not any(word in text for word in loan_denial_words):
                # This is about financial condition, not loan denial - skip dispute check
                pass
            else:
                return "disputed"
        else:
            return "disputed"

    # Very clear callback signals (including Hinglish)
    if any(phrase in text for phrase in [
        "call later", "call me later", "call back", "callback",
        "call me next week", "call me next month", "call me tomorrow",
        "call me next time", "call me some other time",
        "call you back", "call back later", "call back tomorrow",
        "next week", "next month", "tomorrow", "some other time",
        "busy now", "busy right now", "busy at the moment", "busy currently",
        "not available", "not available now", "not available right now",
        "out of town", "currently out", "away", "travelling", "traveling",
        "can't talk now", "cant talk now", "cannot talk now",
        "not a good time", "bad time", "inconvenient time",
        "later please", "please call later", "call me when convenient",
        # Hinglish phrases - expanded patterns
        "baad mein call karo", "abhi busy hoon", "abhi available nahi hoon",
        "kal call karo", "baad mein baat karte hain", "abhi time nahi hai",
        "ghar se bahar hoon", "travel kar raha hoon", "abhi baat nahi kar sakta",
        "aap baad mein call kar sakte", "baad mein call kar sakte hain",
        "abhi busy hoon kal", "available nahi hoon next week", "next week call karo",
        "out of town hoon", "next month call karo", "baat nahi kar sakta baad mein",
        "kal call karo please", "office mein hoon", "next week call kar lena",
        "time nahi hai evening", "travel kar raha hoon baad mein", "meeting mein hoon",
        "tomorrow call karo", "abhi driving kar raha", "weekend mein call karo",
        "convenient nahi hai", "baad mein call kar lena", "ghar par nahi hoon",
        "discuss nahi kar sakta", "kal subah call karo", "hospital mein hoon",
        "evening mein call karo", "baat karne ka time nahi", "available rahunga",
        "family ke saath hoon", "baad mein call kar lena please", "busy hoon later",
        "tomorrow evening call karo", "important work mein hoon", "next week call"
    ]):
        return "callback"

    # Very clear willingness to pay (including partial payment willingness and Hinglish)
    if any(phrase in text for phrase in [
        "i want to pay", "i will pay", "i can pay", "i'd like to pay",
        "ready to pay", "willing to pay", "prepared to pay",
        "installment", "installments", "monthly payment", "monthly installments",
        "payment plan", "payemnt plan", "pay plan", "repayment plan",
        "can i pay in", "can pay in", "pay in installments", "pay in parts",
        "emi", "equated monthly installment", "monthly emi",
        "work out a plan", "work out payment", "work something out",
        "can't pay full", "cant pay full", "cannot pay full",
        "can't pay in full", "cant pay in full", "cannot pay in full",
        "can't pay the full", "cant pay the full", "cannot pay the full",
        "can't pay full amount", "cant pay full amount", "cannot pay full amount",
        "can pay partial", "can pay some", "can pay part", "can pay portion",
        "partial payment", "pay partial", "pay some", "pay part",
        "pay later", "pay next month", "pay after", "pay when",
        "let's work", "let us work", "we can work", "we can arrange",
        "interested in paying", "want to settle", "want to clear",
        "can manage", "can arrange", "can figure out", "can work something out",
        # Payment options requests
        "payment options", "payment option", "show payment options", "show me payment options",
        "i'd like to see payment options", "i would like to see payment options",
        "i want to see payment options", "want to see payment options",
        "can i see payment options", "can you show payment options",
        "what are my options", "what options do i have", "what are the options",
        "options please", "show options", "show me options",
        "what can you offer", "can you offer", "do you have options",
        "i'd like options", "i would like options", "want options",
        # Hinglish phrases - expanded patterns
        "main pay kar sakta hoon", "emi chahiye", "payment plan de do",
        "installment mein pay kar sakta hoon", "monthly pay kar sakta hoon",
        "full amount nahi de sakta", "thoda thoda pay kar sakta hoon",
        "payment options dikhao", "kya options hain", "payment kar sakta hoon",
        "settle kar sakta hoon", "clear kar sakta hoon", "manage kar sakta hoon",
        "pay karna chahta hoon", "pay karne ko ready", "pay karne ko willing",
        "installments mein pay", "kya main installments mein", "monthly installments de sakta",
        "payment options dikhao", "kya options hain", "monthly basis par pay",
        "thoda thoda pay", "payment karne ko ready", "emi plan chahiye",
        "pay kar sakta hoon but installments", "payment options kya hain",
        "settle kar sakta hoon but plan", "monthly pay kar sakta",
        "kya main payment plan le sakta", "pay karne ko interested",
        "payment options batao", "monthly emi de sakta", "payment plan choose",
        "monthly basis par", "settle kar sakta installment mein",
        "payment plan select", "options chahiye", "payment plan ke liye ready"
    ]):
        return "willing"

    # Additional flexible keyword-based checks for better coverage
    # Check for paid keywords (past tense indicators)
    paid_keywords = ["pay kar diya", "payment kar diya", "transfer kar diya", "clear kar diya", 
                     "settle kar diya", "ho gaya hai", "kar di thi", "bhej diya", "receipt"]
    if any(keyword in text for keyword in paid_keywords):
        # Exclude if it's about future payment or asking about payment
        if not any(phrase in text for phrase in ["nahi kar sakta", "nahi de sakta", "karna chahta", 
                                                  "kar sakta hoon", "kar sakta", "chahta hoon"]):
            return "paid"
    
    # Check for dispute keywords (denial patterns)
    # IMPORTANT: Exclude financial hardship phrases to avoid false positives
    dispute_keywords = ["mera nahi hai", "nahi hai", "galat hai", "fraud", "wrong", "mistake hai", 
                        "nahi liya", "nahi kiya", "nahi sign", "nahi approve", "meri nahi"]
    if any(keyword in text for keyword in dispute_keywords):
        # Exclude if it's about payment ability, financial hardship, or financial condition
        financial_hardship_indicators = [
            "pay kar sakta", "payment kar sakta", "de sakta", "afford", "paise",
            "financial", "financially", "income", "salary", "funds", "savings",
            "naukri", "job", "struggling", "weak", "unstable", "crisis", "problem",
            "khatam", "bandh", "nahi hain", "available nahi", "resources"
        ]
        if not any(phrase in text for phrase in financial_hardship_indicators):
            return "disputed"
    
    # Additional check for "unable" patterns that might have been missed
    # This catches phrases that indicate inability to pay but weren't caught earlier
    unable_indicators = [
        "nahi de sakta", "nahi kar sakta", "pay nahi", "payment nahi",
        "salary bandh", "income source", "savings khatam", "funds nahi",
        "financial condition", "financial situation", "financially weak",
        "financially unstable", "paise available nahi", "resources nahi"
    ]
    if any(indicator in text for indicator in unable_indicators):
        # Make sure it's not about willingness to pay (which would be "willing")
        if not any(phrase in text for phrase in ["pay kar sakta", "payment kar sakta", 
                                                   "installment", "emi", "plan chahiye", 
                                                   "options chahiye", "willing", "ready"]):
            return "unable"
    
    # Check for callback keywords (time/deferral patterns)
    callback_keywords = ["call karo", "call kar", "baad mein", "kal", "tomorrow", "next week", 
                         "next month", "busy hoon", "available nahi", "time nahi", "call sakte"]
    if any(keyword in text for keyword in callback_keywords):
        return "callback"
    
    # Check for willing keywords (payment-related but not already paid)
    willing_keywords = ["pay kar sakta", "payment kar sakta", "emi", "installment", "plan chahiye", 
                         "options chahiye", "karna chahta", "ready hoon", "willing", "chahta hoon"]
    if any(keyword in text for keyword in willing_keywords):
        return "willing"

    return "unknown"


# ------------------------------------------------------------------
# Unified classifier (RULES → AZURE OPENAI)
# ------------------------------------------------------------------

def classify_intent(prompt: str) -> str:
    """
    Unified intent classifier with hybrid approach.
    
    Strategy:
    1. Try fast rule-based classification for obvious cases
    2. If uncertain, use Azure OpenAI for intelligent classification
    3. Always return a valid intent
    """
    # Try rule-based first (fast)
    rule_intent = classify_intent_rule_based(prompt)
    
    if rule_intent in ALLOWED_INTENTS:
        print(f"[INTENT] Rule-based: {rule_intent}")
        return rule_intent
    
    # Fall back to LLM for complex cases
    print(f"[INTENT] Using Azure OpenAI for: '{prompt[:50]}...'")
    azure_intent = classify_intent_with_azure_openai(prompt)
    print(f"[INTENT] Azure OpenAI classified as: {azure_intent}")
    
    return azure_intent


# ------------------------------------------------------------------
# Response generation (for negotiation node)
# ------------------------------------------------------------------

def generate_negotiation_response(context: str) -> str:
    """
    Generate conversational negotiation responses using Azure OpenAI.
    Returns None if generation fails (triggers template fallback).
    """
    try:
        client = get_azure_openai_client()
        
        # Simplified prompt to avoid safety filters
        safe_prompt = f"""{context}

Respond professionally in 2-3 sentences."""
        
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": safe_prompt}],
            temperature=0.7,
            max_tokens=150
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        # Validate response quality
        if was_blocked or not text or len(text.strip()) < 20:
            print("Warning: Azure OpenAI response blocked or incomplete, using template")
            raise Exception("Blocked or incomplete response")
        
        return text
        
    except Exception as e:
        print(f"Error generating negotiation response: {e}")
        return None


def generate_payment_plans(outstanding_amount: float, customer_name: str) -> list:
    """
    Generate 2-3 payment plan options using Azure OpenAI.
    Falls back to rule-based plans if generation fails.
    """
    
    try:
        client = get_azure_openai_client()
        
        # Safer prompt structure - Updated for Hinglish
        prompt = f"""Create 2-3 payment plans for a debt of ₹{outstanding_amount:,.0f}. Plans should be in Hinglish (Hindi + English mix).

Return JSON array only:
[
  {{"name": "Plan name", "description": "Details with amount and timeline in Hinglish"}}
]

Example: {{"name": "3-Month EMI Plan", "description": "3 mahine tak ₹X per month"}}

Generate plans:"""

        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        text, was_blocked = safe_get_response_text(response)
        
        if was_blocked or not text:
            print("Warning: Plan generation blocked, using fallback")
            raise Exception("Response blocked")
        
        # Extract JSON
        import json
        import re
        
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            plans = json.loads(json_str)
            
            if isinstance(plans, list) and len(plans) > 0:
                for plan in plans:
                    if 'name' not in plan or 'description' not in plan:
                        raise Exception("Invalid plan structure")
                
                print(f"[PLANS] Generated {len(plans)} payment plans")
                return plans
        
        raise Exception("Could not extract valid JSON")
        
    except Exception as e:
        print(f"Error generating payment plans: {e}")
        return generate_fallback_plans(outstanding_amount)


def generate_fallback_plans(amount: float) -> list:
    """
    Generate fallback payment plans using rule-based logic.
    Creates 2-3 standard plans based on amount.
    """
    plans = []
    
    # Plan 1: Full payment with 5% discount
    discount = int(amount * 0.05)
    plans.append({
        "name": "Immediate Settlement",
        "description": f"7 din ke andar ₹{amount - discount:,.0f} (5% discount) full payment"
    })
    
    # Plan 2: 3-month installment
    monthly_3 = int(amount / 3)
    plans.append({
        "name": "3-Month EMI Plan",
        "description": f"3 mahine tak ₹{monthly_3:,.0f} per month"
    })
    
    # Plan 3: 6-month (large amounts) or 2-month (smaller amounts)
    if amount > 30000:
        monthly_6 = int(amount / 6)
        plans.append({
            "name": "6-Month EMI Plan",
            "description": f"6 mahine tak ₹{monthly_6:,.0f} per month"
        })
    else:
        monthly_2 = int(amount / 2)
        plans.append({
            "name": "2-Month EMI Plan",
            "description": f"2 mahine tak ₹{monthly_2:,.0f} per month"
        })
    
    print(f"[PLANS] Using fallback plans ({len(plans)} options)")
    return plans
