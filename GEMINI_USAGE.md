# Gemini LLM Usage in Debt Collection Agent

This document details exactly where and how Google Gemini is used in this project.

---

## 📍 **Location: `src/utils/llm.py`**

All Gemini integration is centralized in this file. The project uses **Google Gemini Flash models** (2.5, 2.0, or 1.5) as the primary LLM.

---

## 🎯 **Purpose 1: Intent Classification** (Primary Use)

### **Function:** `classify_intent_with_gemini(prompt: str)`

**What it does:**
- Classifies customer responses into one of 5 payment intents:
  - `paid` - Customer claims they already paid
  - `disputed` - Customer disputes the debt
  - `callback` - Customer wants to be called back later
  - `unable` - Customer cannot afford to pay
  - `willing` - Customer is willing to pay/negotiate

**When it's called:**
- **Called from:** `payment_check_node()` in `src/nodes/payment_check.py`
- **Trigger:** After the agent discloses the debt and asks "Are you able to make this payment today?"
- **User input example:** "I already paid last week" → Classified as `paid`

**How it works:**
1. First tries **rule-based classification** (fast, no API call)
2. If uncertain (`unknown`), calls **Gemini** for intelligent classification
3. Gemini analyzes the customer's response and returns one of the 5 intents
4. Falls back to rule-based if Gemini fails or is blocked

**Prompt sent to Gemini:**
```
Classify this customer response in a debt collection call.

Response: "{user_input}"

Return ONE word only from: paid, disputed, callback, unable, willing

Classification:
```

**Configuration:**
- Temperature: `0.1` (low for consistent classification)
- Max tokens: `10` (just need one word)
- Safety settings: All disabled (to avoid false blocks)

---

## 🎯 **Purpose 2: Payment Plan Generation**

### **Function:** `generate_payment_plans(outstanding_amount: float, customer_name: str)`

**What it does:**
- Generates 2-3 personalized payment plan options based on the outstanding amount
- Returns JSON array with plan names and descriptions

**When it's called:**
- **Called from:** `negotiation_node()` in `src/nodes/negotiation.py`
- **Trigger:** When customer expresses willingness to pay (`payment_status: "willing"`)
- **Example:** Outstanding ₹45,000 → Generates plans like:
  - "3-Month Installment: Pay ₹15,000 per month"
  - "6-Month Installment: Pay ₹7,500 per month"

**How it works:**
1. Sends amount to Gemini with instructions to create payment plans
2. Gemini generates JSON with plan options
3. Parses JSON and validates structure
4. Falls back to rule-based plans if Gemini fails

**Prompt sent to Gemini:**
```
Create 2-3 payment plans for a debt of ₹{amount}.

Return JSON array only:
[
  {"name": "Plan name", "description": "Details with amount and timeline"}
]

Generate plans:
```

**Configuration:**
- Temperature: `0.3` (moderate for creative but structured output)
- Max tokens: `500` (enough for JSON)
- Safety settings: All disabled

---

## 🎯 **Purpose 3: Negotiation Response Generation**

### **Function:** `generate_negotiation_response(context: str)`

**What it does:**
- Generates natural, conversational responses during payment negotiation
- Creates contextually appropriate replies based on conversation history

**When it's called:**
- **Called from:** `negotiation_node()` in `src/nodes/negotiation.py`
- **Trigger:** During negotiation when customer discusses payment options
- **Example:** Customer says "Can I pay in 6 months?" → Gemini generates a professional response confirming or negotiating

**How it works:**
1. Builds context from recent conversation (last 6 messages)
2. Includes customer name, outstanding amount, and offered plans
3. Sends to Gemini with instructions to respond professionally
4. Falls back to template responses if Gemini fails

**Prompt sent to Gemini:**
```
You are a professional debt collection agent.

Customer: {name}
Outstanding: ₹{amount}

Recent conversation:
{last_6_messages}

Customer said: "{user_input}"

Task: Respond naturally. If they selected a plan, confirm it and ask for payment date. 
If they mentioned a date, confirm it. Be brief (2-3 sentences).

Response:
```

**Configuration:**
- Temperature: `0.7` (higher for natural conversation)
- Max tokens: `150` (2-3 sentences)
- Safety settings: All disabled

---

## 🔄 **Call Flow: When Gemini is Used**

```
1. User enters phone number → Session starts
2. Agent greets → "Am I speaking with Rajesh Kumar?"
3. User confirms → Verification (DOB check - NO GEMINI)
4. Agent discloses debt → "You owe ₹45,000. Can you pay today?"
5. User responds → "I can't pay right now"
   
   ⚡ GEMINI CALL #1: classify_intent()
   → Classifies as "unable"
   
6. Agent offers payment plans
   
   ⚡ GEMINI CALL #2: generate_payment_plans()
   → Generates 3 installment options
   
7. User negotiates → "Can I pay in 6 months?"
   
   ⚡ GEMINI CALL #3: generate_negotiation_response()
   → Generates natural response confirming/negotiating
```

---

## 🛡️ **Fallback Strategy**

The system has **multiple fallback layers**:

1. **Rule-based first:** Fast pattern matching for obvious cases (no API call)
2. **Gemini second:** Only called when rule-based returns `unknown`
3. **Template fallback:** If Gemini fails/blocked, uses predefined templates
4. **Model fallback:** Tries multiple Gemini models (2.5 → 2.0 → 1.5) until one works

---

## 📊 **Gemini Models Used**

The system tries these models in order:
1. `gemini-2.5-flash` (latest)
2. `models/gemini-2.5-flash` (alternative format)
3. `gemini-2.0-flash`
4. `models/gemini-2.0-flash`
5. `gemini-1.5-flash` (fallback)
6. `models/gemini-1.5-flash`

**Why multiple models?** Different API endpoints may use different naming conventions.

---

## 🔐 **API Key Configuration**

- **Environment variable:** `GEMINI_API_KEY`
- **Location:** `.env` file in project root
- **Required:** Yes (system won't work without it)
- **Get key:** https://aistudio.google.com/app/apikey

---

## 📈 **Usage Statistics**

**Typical conversation uses Gemini:**
- **1-2 times** for intent classification (when user response is ambiguous)
- **1 time** for payment plan generation (when customer is willing to pay)
- **2-5 times** for negotiation responses (during back-and-forth discussion)

**Total Gemini calls per conversation:** 4-8 calls (depending on conversation complexity)

---

## 🚫 **Where Gemini is NOT Used**

- ❌ **Greeting** - Simple template message
- ❌ **Verification** - Rule-based DOB matching (no LLM)
- ❌ **Disclosure** - Template legal disclosure
- ❌ **Closing** - Template closing message

---

## 💡 **Why Gemini?**

1. **Intent Classification:** Handles ambiguous responses better than rules
   - Example: "I'm having financial difficulties" → Correctly classified as `unable`
   
2. **Payment Plans:** Generates personalized options based on amount
   - Example: ₹45,000 → Creates appropriate installment plans
   
3. **Natural Conversation:** Makes negotiation feel more human
   - Example: Responds contextually instead of using rigid templates

---

## 🔍 **Code References**

| Function | File | Line |
|----------|------|------|
| `classify_intent_with_gemini()` | `src/utils/llm.py` | 156 |
| `generate_payment_plans()` | `src/utils/llm.py` | 380 |
| `generate_negotiation_response()` | `src/utils/llm.py` | 338 |
| `classify_intent()` (unified) | `src/utils/llm.py` | 311 |
| Called from `payment_check_node()` | `src/nodes/payment_check.py` | 26 |
| Called from `negotiation_node()` | `src/nodes/negotiation.py` | 299, 368 |

---

## 📝 **Summary**

**Gemini is used for 3 specific purposes:**
1. ✅ **Classifying customer payment intent** (when rules are uncertain)
2. ✅ **Generating payment plan options** (personalized to amount)
3. ✅ **Creating natural negotiation responses** (contextual conversation)

**All other functionality** (greeting, verification, disclosure, closing) uses **rule-based logic** or **templates** - no LLM needed.

