RELEASE NOTES

Version 1.3.0 (Current) – 20 January 2026
Major Features
Hinglish Language Support
Added comprehensive Hinglish phrase support with 180 test cases

30 variations per workflow covering authentic Indian English/Hindi mix

100% test pass rate achieved across all 6 workflows

Enhanced intent classification for regional language variations

Support for authentic customer phrases like "payement successfull ho gya", "paise nahi hain"


Comprehensive Test Suite
180 comprehensive test cases (30 per workflow)

100% pass rate (180/180 tests passing)

Hinglish test coverage with authentic phrases

Excel and JSON test report generation

Test utilities for results analysis and export


Technical Improvements
Fixed LangSmith rate limiting by disabling tracing programmatically

Added missing dependency python-multipart for form data handling

Enhanced rule-based classifier with expanded Hinglish patterns

Updated deployment URL to Render: https://debt-collection-web-agent-cvle.onrender.com

Improved .env file handling and encoding issues


Documentation Updates
Updated README.md with Hinglish test coverage details

Enhanced project structure documentation

Added comprehensive test examples and results

Created test utilities and reporting tools

Updated deployment and setup instructions


Bug Fixes
Resolved embedded null character issues in .env file

Fixed intent classification for "payement successfull ho gya"

Corrected missing comma syntax error in LLM patterns

Disabled LangSmith tracing to avoid API rate limits

Fixed dependency installation issues (python-multipart)


Files Updated
src/utils/llm.py – Enhanced Hinglish phrase patterns and LangSmith fix

tests/run_comprehensive_tests.py – Comprehensive test runner

tests/test_results.json – Detailed test results

test_results.xlsx – Excel-compatible test report

check_results.py – Test results summary utility

requirements.txt – Added python-multipart dependency

frontend/src/api/chatapi.js – Updated deployment URL

README.md – Updated with Hinglish test coverage

RELEASE_NOTES.md – Added latest version information


Test Results Summary
already_paid: 30/30 (100.0%) – Phrases like "main ne payment kar diya", "payement successfull ho gya"

dispute: 30/30 (100.0%) – Phrases like "maine liya hi nahi", "yeh mera nahi hai"

callback: 30/30 (100.0%) – Phrases like "baad mein call karna", "main abhi busy hoon"

unable_to_pay: 30/30 (100.0%) – Phrases like "paise nahi hain", "job chali gayi"

willing: 30/30 (100.0%) – Phrases like "installment mein pay kar sakta", "plan chahiye"

unknown: 30/30 (100.0%) – Questions, clarifications, and ambiguous responses

Overall: 180/180 (100.0%) – Perfect test coverage


Technical Notes
LangSmith tracing disabled programmatically to avoid rate limits

Hinglish phrases integrated into rule-based classification

Test suite covers authentic Indian customer scenarios

Deployment updated to Render platform

All environment variables properly configured

Version 1.2.0 – 22 January 2026
Major Features
Payment Screenshot Upload
Introduced /upload-screenshot endpoint for submitting payment proof


Screenshot upload button (📎) visible during Paid and Disputed flows


Screenshots stored in uploads/screenshots/ with timestamp-based filenames


Closing node now mandates payment proof before confirming a “Paid” outcome


Conversation automatically completes after successful screenshot upload


Supports common image formats



Feedback Collection
Added /feedback endpoint for post-call feedback submission


New FeedbackModal with a 5-star rating system


Optional text feedback for qualitative insights


Feedback captures session metadata, customer details, and call outcome


Feedback modal triggered via “Rate Conversation” button after call completion



Enhanced Closing Logic
Two-step closing flow for Paid status:


Request payment proof


Verify screenshot and finalize closure


Automatic detection of payment screenshots in conversation context


Context-aware closing messages based on payment state



UI Improvements
Phone number input replaced with dropdown containing predefined test numbers


Added test numbers:


+917219559972


+919876543210


+919876543211


+919876543212


Improved error handling and user-friendly messaging


Enhanced state management for screenshot upload flow



Backend Enhancements
Added FeedbackRequest model for structured feedback data


Session validation for screenshot upload and feedback submission


Automatic creation of upload directories


Improved error handling and graph-triggered conversation completion



Files Updated
backend/routes/chat.py – Screenshot & feedback endpoints


src/nodes/closing.py – Payment proof verification logic


frontend/src/App.jsx – Screenshot upload & feedback integration


frontend/src/components/userinput.jsx – Upload button support


frontend/src/components/feedbackmodal.jsx – New feedback component


frontend/src/components/floatingpaybutton.jsx – Added (currently disabled)


frontend/src/api/chatapi.js – Feedback submission API



Technical Notes
Screenshot naming format: {session_id}_{timestamp}.{extension}


Feedback fields include rating (1–5), optional text, and session metadata


Screenshot button visibility triggers:


Paid status


Disputed status


Payment-related user messages


Upload directories are auto-created if missing



Version 1.1.0 – 15 January 2026
Major Changes
Simplified Identity Verification
Removed DOB-based verification


Identity verification now happens automatically via phone number


Removed verification confirmation message for smoother flow



Enhanced Security & Guardrails
Added input validation and sanitization (max 5000 characters, format checks)


Improved phone number validation (length, format, character checks)


Added state validation across all nodes:


Verification


Greeting


Disclosure


Payment Check


Negotiation



Improved User Experience
Greeting flow now handles negative responses ("no", "not me", etc.)


Conversation ends gracefully on invalid identity confirmation


Removed “Start Again” button (campaign-style flow)


Increased attachment icon size from 18px to 20px



Backend Improvements
Enhanced /init and /chat endpoints with validation logic


Improved error messaging and state validation


Removed unused code (handleStartAgain)



Files Changed
backend/routes/chat.py


src/nodes/verification.py


src/nodes/greeting.py


src/nodes/disclosure.py


src/nodes/payment_check.py


src/nodes/negotiation.py


frontend/src/App.jsx


frontend/src/components/conversationcompletion.jsx


frontend/src/components/userinput.jsx





Breaking Changes
❗ DOB-based verification completely removed


Phone number is now the sole identity verification mechanism




