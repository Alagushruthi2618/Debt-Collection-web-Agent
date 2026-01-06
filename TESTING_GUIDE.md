# Testing Guide - Debt Collection Agent

This guide covers all ways to test the application.

## Prerequisites

1. ✅ Backend server running on `http://localhost:8000`
2. ✅ Frontend server running on `http://localhost:5173` (for web testing)
3. ✅ `.env` file with `GEMINI_API_KEY` set

---

## 🧪 Test Customers

Use these phone numbers for testing:

| Phone Number | Name | Date of Birth | Loan Type | Outstanding Amount |
|-------------|------|---------------|-----------|-------------------|
| `+919876543210` | Rajesh Kumar | 15-03-1985 | Personal Loan | ₹45,000 |
| `+919876543211` | Priya Sharma | 22-07-1990 | Credit Card | ₹52,500 |
| `+919876543212` | Amit Patel | 05-11-1988 | Vehicle Loan | ₹1,25,000 |

---

## Method 1: Web Application Testing (Recommended)

### Step 1: Start Both Servers

**Terminal 1 - Backend:**
```powershell
python backend/app.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Step 2: Open Browser

1. Open `http://localhost:5173` in your browser
2. You should see a phone number input field

### Step 3: Test Conversation Flow

**Enter phone number:** `+919876543210`

**Expected Flow:**

1. **Greeting Stage:**
   - Agent greets: "Hello Rajesh, good day..."
   - You respond: `Yes, this is Rajesh`

2. **Verification Stage:**
   - Agent asks for Date of Birth
   - You respond: `15-03-1985` (or `15/03/1985`)

3. **Disclosure Stage:**
   - Agent provides legal disclosure
   - You respond: `I understand` or `Yes`

4. **Payment Discussion:**
   - Agent explains outstanding amount (₹45,000)
   - You can test different scenarios:
     - **Willing to pay:** `I want to pay` → Agent offers payment plans
     - **Already paid:** `I already paid` → Agent acknowledges
     - **Dispute:** `I dispute this debt` → Agent records dispute
     - **Unable to pay:** `I can't pay right now` → Agent offers negotiation
     - **Callback:** `Can you call me back later?` → Agent schedules callback

5. **Negotiation (if applicable):**
   - Agent offers payment plans (EMI, partial, deferred)
   - You select a plan or negotiate

6. **Closing:**
   - Agent closes the call professionally
   - Call outcome is recorded

---

## Method 2: CLI Mode Testing (Terminal)

### Start CLI Mode

```powershell
python main.py
```

### Example Test Conversation

```
=== Debt Collection Agent Test ===
Available test customers:
1. +919876543210 (Rajesh Kumar)
2. +919876543211 (Priya Sharma)
3. +919876543212 (Amit Patel)

Enter phone number: +919876543210

[Agent]: Hello Rajesh, good day. This is a call from ABC Finance...

[You]: Yes, this is Rajesh

[Agent]: Thank you for confirming. To proceed, I need to verify your identity...

[You]: 15-03-1985

[Agent]: Thank you, verification successful. Before we proceed...

[You]: I understand

[Agent]: You have an outstanding amount of ₹45,000...

[You]: I want to make a payment plan

[Agent]: I can offer you the following options...
```

---

## Method 3: API Testing

### Option A: Using Test Script

```powershell
python backend/test_api.py
```

This will automatically test:
- Health endpoint
- Session initialization
- Chat messages

### Option B: Using curl (PowerShell)

**1. Health Check:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

**2. Initialize Session:**
```powershell
$body = @{phone = "+919876543210"} | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://localhost:8000/api/init" -Method POST -Body $body -ContentType "application/json"
$sessionId = ($response.Content | ConvertFrom-Json).session_id
Write-Host "Session ID: $sessionId"
```

**3. Send Chat Message:**
```powershell
$body = @{
    session_id = $sessionId
    user_input = "Yes, this is Rajesh"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/chat" -Method POST -Body $body -ContentType "application/json"
```

### Option C: Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Initialize session
response = requests.post(
    f"{BASE_URL}/api/init",
    json={"phone": "+919876543210"}
)
data = response.json()
session_id = data["session_id"]
print(f"Session ID: {session_id}")

# Send messages
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "session_id": session_id,
        "user_input": "Yes, this is Rajesh"
    }
)
print(response.json())
```

### Option D: Using API Documentation (Swagger UI)

1. Start backend server
2. Open `http://localhost:8000/docs` in browser
3. Use the interactive API documentation to test endpoints

---

## 📋 Test Scenarios

### Scenario 1: Happy Path - Customer Commits to Payment

**Phone:** `+919876543210`  
**DOB:** `15-03-1985`

**Conversation:**
1. Confirm identity: `Yes, this is Rajesh`
2. Provide DOB: `15-03-1985`
3. Accept disclosure: `I understand`
4. Commit to payment: `I want to pay`
5. Select plan: `I'll take the 3-month plan`

**Expected Result:**
- ✅ Verification successful
- ✅ Payment plan recorded
- ✅ Call outcome: `willing`

---

### Scenario 2: Customer Already Paid

**Phone:** `+919876543210`  
**DOB:** `15-03-1985`

**Conversation:**
1. Confirm identity: `Yes`
2. Provide DOB: `15-03-1985`
3. Accept disclosure: `Yes`
4. Claim payment: `I already paid this amount`

**Expected Result:**
- ✅ Verification successful
- ✅ Payment status: `paid`
- ✅ Call outcome: `paid`

---

### Scenario 3: Customer Disputes Debt

**Phone:** `+919876543211`  
**DOB:** `22-07-1990`

**Conversation:**
1. Confirm identity: `Yes, Priya here`
2. Provide DOB: `22-07-1990`
3. Accept disclosure: `Okay`
4. Dispute: `I don't owe this money` or `This is wrong`

**Expected Result:**
- ✅ Verification successful
- ✅ Dispute recorded
- ✅ Call outcome: `disputed`

---

### Scenario 4: Verification Failed (3 Attempts)

**Phone:** `+919876543210`

**Conversation:**
1. Confirm identity: `Yes`
2. Wrong DOB: `01-01-2000` ❌
3. Wrong DOB: `01-01-2001` ❌
4. Wrong DOB: `01-01-2002` ❌

**Expected Result:**
- ❌ Verification failed after 3 attempts
- ✅ Call outcome: `verification_failed`
- ✅ Call ends without disclosure

---

### Scenario 5: Customer Requests Callback

**Phone:** `+919876543212`  
**DOB:** `05-11-1988`

**Conversation:**
1. Confirm identity: `Yes`
2. Provide DOB: `05-11-1988`
3. Accept disclosure: `Yes`
4. Request callback: `Can you call me back tomorrow?`

**Expected Result:**
- ✅ Verification successful
- ✅ Callback scheduled
- ✅ Call outcome: `callback`

---

### Scenario 6: Negotiation Flow

**Phone:** `+919876543210`  
**DOB:** `15-03-1985`

**Conversation:**
1. Complete verification
2. Express inability: `I can't pay the full amount right now`
3. Agent offers plans
4. Negotiate: `Can I pay in 6 months instead?`

**Expected Result:**
- ✅ Negotiation options shown
- ✅ Plan selected/negotiated
- ✅ PTP (Promise-to-Pay) recorded

---

## 🔍 What to Check

### Backend Logs

Watch the backend terminal for:
- ✅ Session creation
- ✅ LangGraph node execution
- ✅ State transitions
- ❌ Any error messages

### Frontend Behavior

Check:
- ✅ Messages appear correctly
- ✅ Input field enables/disables based on `awaiting_user`
- ✅ Loading states work
- ✅ Error handling (network errors, etc.)

### API Responses

Verify response structure:
```json
{
  "session_id": "abc123...",
  "messages": [
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "stage": "greeting|verification|disclosure|payment_check|negotiation|closing",
  "awaiting_user": true|false,
  "is_complete": true|false,
  "offered_plans": [...]
}
```

---

## 🐛 Troubleshooting

### Backend Issues

**"GEMINI_API_KEY not set"**
- Check `.env` file exists
- Verify API key is correct
- Restart backend server

**"Session not found"**
- Make sure you call `/api/init` first
- Check session_id is correct

**Import errors**
- Make sure you're in project root
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend Issues

**"Failed to start chat"**
- Check backend is running on port 8000
- Check browser console for errors
- Verify CORS is enabled

**"Invalid realid provided"**
- This is for production build
- Use source code version (should ask for phone number)
- Or add `?realid=123` to URL

**Can't connect to backend**
- Verify backend URL in `frontend/src/api/chatapi.js`
- Check backend is running
- Check firewall/antivirus blocking

---

## 📊 Expected Outcomes

After testing, you should see:

1. **Call Records** stored in memory (`src/data.py`)
2. **PTP Records** if payment plans were made
3. **Dispute Records** if disputes were raised
4. **Session State** properly managed throughout conversation

---

## 🎯 Quick Test Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads in browser
- [ ] Can initialize session with test phone number
- [ ] Verification works with correct DOB
- [ ] Verification fails after 3 wrong attempts
- [ ] Payment discussion flows correctly
- [ ] Negotiation offers plans
- [ ] Different customer responses handled correctly
- [ ] Call closes properly
- [ ] API returns correct response structure

---

## 📚 Additional Resources

- **API Documentation:** `http://localhost:8000/docs`
- **Backend README:** `backend/README.md`
- **Quick Start:** `QUICKSTART.md`
- **Main README:** `README.md`

