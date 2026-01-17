# Release Notes

## Version Update - [Date]

### 🎯 Major Changes

**Simplified Identity Verification**
- Removed DOB verification - verification now happens automatically via phone number
- Removed verification confirmation message for smoother flow

**Enhanced Security & Guardrails**
- Added input validation and sanitization (max 5000 chars, format checks)
- Enhanced phone number validation (length, format, character validation)
- Added state validation across all nodes (verification, greeting, disclosure, payment_check, negotiation)

**Improved User Experience**
- Greeting flow now handles negative responses ("no", "not me", etc.) - shows error and ends call
- Removed "Start Again" button from conversation completion (backoffice campaign model)
- Increased attach image icon size from 18px to 20px

**Backend Improvements**
- Enhanced `/init` and `/chat` endpoints with validation functions
- Better error messages and state validation
- Removed unused code (`handleStartAgain`)

### 📋 Files Changed
- `backend/routes/chat.py`, `src/nodes/verification.py`, `src/nodes/greeting.py`
- `src/nodes/disclosure.py`, `src/nodes/payment_check.py`, `src/nodes/negotiation.py`
- `frontend/src/App.jsx`, `frontend/src/components/conversationcompletion.jsx`, `frontend/src/components/userinput.jsx`

### ⚠️ Breaking Changes
- DOB verification completely removed - phone number verification only

