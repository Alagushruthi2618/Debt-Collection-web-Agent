# Testing Guide - Debt Collection Web Agent

This guide covers how to test both the backend API and the frontend web application.

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js and npm** installed
3. **Azure OpenAI API Key** - Configure your Azure OpenAI credentials

## Quick Start Testing

### Step 1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://llm-3rdparty.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_MODEL=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Step 2: Start the Backend Server

Open a terminal in the project root:

```bash
# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Start the backend server
python backend/app.py
```

Or using uvicorn:
```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The backend will run on `http://localhost:8000`

### Step 3: Start the Frontend

Open a **new terminal** in the project root:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

### Step 4: Test in Browser

1. Open your browser and go to `http://localhost:5173`
2. Enter a test phone number: `+919876543210`
3. Click "Start Chat"
4. Start chatting!

## Testing Scenarios

### Test Customer Phone Numbers

Use these phone numbers for testing (they have pre-configured data):

- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

### Scenario 1: Happy Path (Payment Plan)

1. Start chat with `+919876543210`
2. Reply to greeting: "Yes, this is Rajesh"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I want a payment plan" or "I'm willing to pay"
5. Select a payment plan option
6. Complete the conversation

**Expected**: Agent should offer payment plans and allow selection.

### Scenario 2: Already Paid

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I have already made the payment" or "I already paid"

**Expected**: Agent should acknowledge the payment and mention verification, NOT create a dispute ticket.

### Scenario 3: Future Payment Commitment

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "My salary is due tomorrow, so I can only make the payment after tomorrow"

**Expected**: Agent should classify as "willing" and acknowledge the future payment timeline, NOT say "already paid".

### Scenario 4: Dispute

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "This is not my debt" or "I never took this loan"

**Expected**: Agent should create a dispute ticket and provide a reference number.

### Scenario 5: Callback Request

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I'm busy right now, can you call me later?" or "No, I am currently out of town"

**Expected**: Agent should acknowledge and confirm callback.

### Scenario 6: Unable to Pay

1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: "I lost my job" or "I can't afford to pay"

**Expected**: Agent should show empathy and mention reviewing options.

### Scenario 7: Negative Response to Greeting

1. Start chat with `+919876543210`
2. When asked "Am I speaking with Rajesh Kumar?": Reply "No" or "Wrong person"

**Expected**: Agent should politely end the call, NOT proceed to verification.

## Backend API Testing

### Option 1: Using the Test Script

```bash
# Make sure backend is running first
python backend/test_api.py
```

### Option 2: Using curl

```bash
# Health check
curl http://localhost:8000/health

# Initialize session
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'

# Send chat message (replace SESSION_ID)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "user_input": "Yes, this is Rajesh"}'
```

### Option 3: Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Initialize
response = requests.post(
    f"{BASE_URL}/api/init",
    json={"phone": "+919876543210"}
)
data = response.json()
session_id = data["session_id"]
print(f"Session ID: {session_id}")

# Chat
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "session_id": session_id,
        "user_input": "Yes, this is Rajesh"
    }
)
print(response.json())
```

### Option 4: Using Swagger UI

1. Start the backend server
2. Open browser to `http://localhost:8000/docs`
3. Use the interactive API documentation to test endpoints

## Testing Specific Fixes

### Test 1: Input Focus Retention

1. Start a chat
2. Type a message and press Enter
3. **Expected**: Cursor should stay in the input box, ready for next message
4. Type another message without clicking
5. **Expected**: Should work without clicking the input box

### Test 2: No Duplicate Messages

1. Start a chat and complete the flow
2. **Expected**: Each assistant response should appear only once
3. Check that "already paid" responses don't appear twice

### Test 3: Correct Intent Classification

Test these specific phrases:

- "I have already made the payment" → Should be "paid"
- "My salary is due tomorrow, so I can only make the payment after tomorrow" → Should be "willing" (NOT "paid")
- "I can pay after next week" → Should be "willing"
- "I already paid yesterday" → Should be "paid"
- "No, I am currently out of town" → Should be "callback"

### Test 4: Greeting "No" Response

1. Start chat
2. When asked "Am I speaking with [Name]?", reply "No"
3. **Expected**: Call should end politely, NOT proceed to verification

## Testing Screenshot Upload Feature

The screenshot upload feature allows customers to upload proof of payment when they claim to have already paid or when there's a payment dispute.

### When the Screenshot Button Appears

The screenshot upload button (📎 icon) appears in the input area when:

1. **Payment Status is "disputed"** - When the agent classifies the payment as disputed
2. **Customer mentions they paid** - When the customer says any of these phrases in recent messages:
   - "paid"
   - "already paid"
   - "i paid"
   - "made payment"
   - "payment done"

### Test Scenario 1: Screenshot Upload After "Already Paid" Claim

**Steps:**
1. Start chat with `+919876543210`
2. Reply to greeting: "Yes, this is Rajesh"
3. Enter DOB: "15-03-1985"
4. When asked about payment, say: **"I already paid"** or **"I have made the payment"**
5. **Expected**: The screenshot upload button (📎) should appear next to the text input
6. Click the screenshot button
7. Select an image file (PNG, JPG, etc.)
8. **Expected**: 
   - Image uploads successfully
   - A message appears: "I've uploaded a screenshot as proof of payment. Our team will review it."
   - The screenshot is saved to `uploads/screenshots/` directory on the backend
   - The conversation continues

**Verification:**
- Check browser console (F12) for upload success
- Check backend terminal for upload confirmation
- Verify file exists in `uploads/screenshots/` directory with format: `{session_id}_{timestamp}.{extension}`

### Test Scenario 2: Screenshot Upload During Dispute

**Steps:**
1. Start chat with `+919876543210`
2. Reply: "Yes"
3. Enter DOB: "15-03-1985"
4. When asked about payment: **"This is not my debt"** or **"I never took this loan"**
5. **Expected**: Agent creates a dispute ticket
6. **Expected**: Screenshot button should appear (because payment_status = "disputed")
7. Upload a screenshot as proof
8. **Expected**: Same behavior as Scenario 1

### Test Scenario 3: Screenshot Upload via API (Backend Testing)

You can test the upload endpoint directly using curl:

```bash
# First, initialize a session and get session_id
SESSION_ID="your_session_id_here"

# Upload a screenshot
curl -X POST http://localhost:8000/api/upload-screenshot \
  -F "session_id=$SESSION_ID" \
  -F "screenshot=@/path/to/your/image.png"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Screenshot uploaded successfully. Our team will review it.",
  "filename": "{session_id}_{timestamp}.png",
  "file_path": "uploads/screenshots/{session_id}_{timestamp}.png"
}
```

### Test Scenario 4: Screenshot Upload via Python

```python
import requests

BASE_URL = "http://localhost:8000"
SESSION_ID = "your_session_id_here"

# Upload screenshot
with open("test_screenshot.png", "rb") as f:
    files = {"screenshot": f}
    data = {"session_id": SESSION_ID}
    response = requests.post(
        f"{BASE_URL}/api/upload-screenshot",
        files=files,
        data=data
    )
    print(response.json())
```

### Test Scenario 5: Error Cases

**Test Invalid File Type:**
1. Try uploading a non-image file (e.g., .txt, .pdf)
2. **Expected**: Backend should reject with error: "File must be an image"

**Test Without Session:**
1. Try uploading without a valid session_id
2. **Expected**: Backend should return 404: "Session not found"

**Test Button Visibility:**
1. Start a normal conversation without mentioning payment
2. **Expected**: Screenshot button should NOT appear
3. Complete the conversation
4. **Expected**: Screenshot button should NOT appear (chat is complete)

### Verification Checklist

After uploading a screenshot, verify:

- [ ] Screenshot button appears when customer says they paid
- [ ] Screenshot button appears when payment is disputed
- [ ] File picker opens when button is clicked
- [ ] Image uploads successfully (check Network tab in DevTools)
- [ ] Success message appears in chat
- [ ] File is saved in `uploads/screenshots/` directory
- [ ] File has correct naming format: `{session_id}_{timestamp}.{ext}`
- [ ] Session state is updated with screenshot message
- [ ] Conversation continues after upload
- [ ] Error handling works for invalid files
- [ ] Error handling works for missing session

### Debugging Screenshot Upload

**Check Browser Console (F12):**
- Network tab: Look for POST request to `/api/upload-screenshot`
- Check request payload (FormData)
- Check response status (should be 200)
- Check for any console errors

**Check Backend Logs:**
- Look for `[ERROR] Screenshot upload error:` if upload fails
- Verify file is being saved to correct directory
- Check that `uploads/screenshots/` directory exists

**Check File System:**
```bash
# From project root
ls -la uploads/screenshots/
# Should show uploaded files with session_id and timestamp
```

**Common Issues:**

1. **Button not appearing:**
   - Make sure you mentioned "paid" or payment is disputed
   - Check browser console for errors
   - Verify `shouldShowScreenshotButton()` logic

2. **Upload fails:**
   - Check backend is running on port 8000
   - Verify `uploads/screenshots/` directory exists (backend creates it automatically)
   - Check file size (very large files might timeout)
   - Verify file is actually an image (PNG, JPG, etc.)

3. **File not saved:**
   - Check backend logs for errors
   - Verify write permissions on `uploads/` directory
   - Check disk space

## Debugging Tips

### Check Backend Logs

The backend prints detailed logs:
- `[PAYMENT_CHECK]` - Intent classification
- `[INTENT]` - Classification results
- `[RESPONSE_GEN]` - Response generation
- `[CLOSING]` - Closing message generation

### Check Browser Console

Open browser DevTools (F12) and check:
- Network tab for API calls
- Console tab for errors
- Check that API calls are successful (200 status)

### Common Issues

1. **"Session not found"**
   - Make sure you initialized the session first
   - Check that session_id is being stored correctly

2. **"AZURE_OPENAI_API_KEY not set"**
   - Check that `.env` file exists in project root
   - Verify the API key is correct

3. **Frontend not connecting**
   - Check that backend is running on port 8000
   - Check `frontend/src/api/chatapi.js` for correct BASE_URL

4. **Intent misclassification**
   - Check backend logs for `[INTENT]` messages
   - Verify the user input is being passed correctly

## Automated Testing

Run the test scenarios:

```bash
# From project root
python tests/test_scenarios.py
```

## API Documentation

Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Next Steps

After testing:
1. Verify all scenarios work correctly
2. Check that responses are contextual (not template-based)
3. Verify no duplicate messages appear
4. Test edge cases (empty input, special characters, etc.)

