# Debt Collection Agent (LangGraph + LangSmith)

An AI-powered Debt Collection Voice Agent built using LangGraph for conversational orchestration and LangSmith for observability and evaluation.

This agent simulates real-world debt collection calls by:

- Verifying customer identity
- Explaining outstanding dues
- Handling different customer responses (paid, disputed, unable, willing, callback)
- Negotiating payment options
- Closing calls professionally
- Tracking performance using LangSmith

## Architecture Overview

### Core Layers
- **Agent Orchestration**: LangGraph state machine
- **LLM Layer**: Azure OpenAI (with deterministic fallback)
- **Observability & Evaluation**: LangSmith
- **CLI Interface**: Manual call simulation via terminal
- **Web Interface**: React frontend with FastAPI backend

## Project Structure

```
debt-collection-agent/
├── backend/                                # FastAPI backend server
│   ├── app.py                             # FastAPI application
│   ├── routes/
│   │   └── chat.py                        # API endpoints
│   └── session_store.py                   # Session management
├── frontend/                               # React frontend
│   ├── src/
│   │   ├── components/                    # UI components
│   │   └── api/                           # API client
│   └── package.json
├── experiments/
│   └── langsmith_eval.py                   # LangSmith evaluation script
├── scripts/
│   └── create_langsmith_dataset.py         # Dataset creation for LangSmith
├── src/
│   ├── nodes/                              # Conversation flow nodes
│   │   ├── __init__.py
│   │   ├── closing.py                      # Call closing & outcome recording
│   │   ├── disclosure.py                   # Legal disclosure node
│   │   ├── greeting.py                     # Initial greeting node
│   │   ├── negotiation.py                  # Payment negotiation logic
│   │   ├── payment_check.py                # Payment intent classification
│   │   └── verification.py                 # Identity verification
│   ├── utils/
│   │   ├── __init__.py
│   │   └── llm.py                          # LLM + deterministic fallback
│   ├── __init__.py
│   ├── data.py                             # In-memory customer & call records
│   ├── graph.py                            # LangGraph flow definition
│   └── state.py                            # Shared call state
├── tests/                                  # Comprehensive test suite
│   ├── test_scenarios.py                  # Basic test scenarios
│   ├── test_cases_comprehensive.py        # Comprehensive test cases
│   ├── run_comprehensive_tests.py         # Test runner script (180 tests)
│   ├── generate_report.py                 # Test report generator
│   ├── export_to_csv.py                  # CSV export utility
│   ├── create_excel_report.py             # Excel report generator
│   ├── create_mock_results.py             # Mock results generator
│   ├── test_results.json                  # Test results (JSON format)
│   ├── test_results.xlsx                  # Test results (Excel format)
│   ├── TestReport_Comprehensive.md        # Comprehensive test report
│   └── export_to_excel.py                 # Excel export utility
├── uploads/                                # User uploads (screenshots, etc.)
│   └── screenshots/                        # Screenshot storage
├── .gitignore                             # Git ignore rules
├── .env.example                            # Environment variables template
├── main.py                                # CLI interface for manual testing
├── check_results.py                      # Test results summary utility
├── requirements.txt                       # Python dependencies
├── README.md                              # This file - project documentation
├── RUN_WEB_APP.md                         # Web app setup & running guide
├── DESIGN.md                              # System design document
├── TESTING_GUIDE.md                       # Testing guide and instructions
├── RELEASE_NOTES.md                       # Release notes and changelog
├── PRESENTATION_SPEAKER_NOTES.md          # Presentation notes for demos
├── test_azure_openai.py                   # Azure OpenAI connection test
├── test_gemini.py                         # Gemini API test (if applicable)
└── test_results.xlsx                      # Excel-compatible test results
```

## Team Contributions

### Mannan Gosrani (Owner / Integrator)
- Overall system architecture and orchestration
- LangGraph state machine and flow integration
- Git workflow, branching strategy, and conflict resolution
- LangSmith setup (tracing, datasets, evaluations)
- Deterministic LLM fallback logic
- CLI-based manual testing (main.py)
- Fixed evaluation script state propagation issues
- Debugged and resolved verification flow bugs
- Final integration, testing, and documentation

### Atharva Ghuge
- Identity verification flow implementation
- Verification node with DOB-based authentication
- Verification failure and retry logic (max 3 attempts)
- Added awaiting_user flags for proper flow control
- Implemented robust DOB matching with multiple format support

### Shruti
- Payment intent classification using LLM
- Negotiation flow (EMI, partial, deferred payments)
- Call closing logic and outcome recording
- Dispute and already-paid flow handling
- Payment status tracking and PTP recording

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/MannanGosrani/Debt-Collection-Agent.git
cd Debt-Collection-Agent
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: pytest is not required to run this project.

## Environment Variables

Create a `.env` file in the project root:

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://llm-3rdparty.cognitiveservices.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_MODEL=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2024-12-01-preview

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=debt-collection-agent

LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=debt-collection-agent
```

**Never commit .env to GitHub**

## Running the Agent

### Option 1: Web Interface (Recommended)

The web app provides a modern, user-friendly interface for interacting with the agent.

**Quick Start:**
1. Start the backend server:
   ```bash
   uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Start the frontend (in a new terminal):
   ```bash
   cd frontend
   npm install  # First time only
   npm run dev
   ```

3. Open your browser: http://localhost:5173

**Features:**
- Enter phone number and press Enter to start
- Real-time chat interface
- Automatic message handling
- Visual payment plan options
- See [RUN_WEB_APP.md](RUN_WEB_APP.md) for detailed setup instructions

### Option 2: CLI Interface

Start an interactive test call via terminal:

```bash
python main.py
```

Example:

```
=== Debt Collection Agent Test ===
Available test customers:
1. +919876543210 (Rajesh Kumar)
2. +919876543211 (Priya Sharma)
3. +919876543212 (Amit Patel)
```

You can then simulate a real conversation step-by-step.

## Testing & Evaluation

### Comprehensive Hinglish Test Suite

The project includes an extensive test suite with **180 comprehensive test cases** covering 6 core workflows with Hinglish language support:

**Run Comprehensive Tests:**
```bash
python tests/run_comprehensive_tests.py
```

**Test Results Summary:**
- **already_paid**: 30/30 (100.0%) - Hinglish phrases like "main ne payment kar diya", "payement successfull ho gya"
- **dispute**: 30/30 (100.0%) - Hinglish phrases like "yeh mera nahi hai", "maine liya hi nahi"
- **callback**: 30/30 (100.0%) - Hinglish phrases like "baad mein call karna", "main abhi busy hoon"
- **unable_to_pay**: 30/30 (100.0%) - Hinglish phrases like "paise nahi hain", "job chali gayi"
- **willing**: 30/30 (100.0%) - Hinglish phrases like "installment mein pay kar sakta", "plan chahiye"
- **unknown**: 30/30 (100.0%) - Questions, clarifications, and ambiguous responses

**Overall Pass Rate: 180/180 (100.0%)**

**Generate Test Reports:**
```bash
python check_results.py                    # View test summary
python tests/export_to_csv.py              # Export to CSV
```

**Test Results Files:**
- `tests/test_results.json` - Detailed JSON results
- `test_results.xlsx` - Excel-compatible CSV report
- `check_results.py` - Results summary utility

### Hinglish Test Coverage

The test suite covers **30 variations per workflow** with authentic Hinglish phrases:

**Already Paid Examples:**
- "Main ne pehle hi payment kar diya hai"
- "Payment ho gaya hai last week" 
- "Payement successfull ho gya"
- "Amount deduct ho gaya hai"
- "Transaction complete ho gaya"

**Unable to Pay Examples:**
- "Mere paas paise nahi hain"
- "Job chali gayi hai"
- "Financial problem hai"
- "Salary nahi a rahi"
- "Struggling kar raha hoon"

**Dispute Examples:**
- "Maine yeh loan liya hi nahi"
- "Yeh galat hai"
- "Fraud hai yeh"
- "Mera account nahi hai"
- "Kisi ne mere naam se liya hai"

**Willing to Pay Examples:**
- "Main pay kar sakta hoon"
- "Installment chahiye"
- "3 month plan mein kar sakta"
- "Partial payment karunga"
- "EMI option batao"

**Callback Examples:**
- "Baad mein call karna"
- "Kal phone karna"
- "Weekend mein time hai"
- "Office mein call karna"
- "Free time mein call karna"

**Unknown/Clarification Examples:**
- "Kya bol rahe ho?"
- "Samajh nahi aaya"
- "Kya matlab hai?"
- "Thoda explain karo"
- "Yeh kya hai?"

### LangSmith Observability & Evaluation

All agent runs are automatically logged to LangSmith, including:
- Node-level execution traces
- Latency metrics
- Token usage statistics
- Errors and exceptions
- Conversation flow visualization

**View Results:**
- **Evaluation Dataset**: [View all 6 test scenarios and results](https://smith.langchain.com/o/c2bf1b47-4401-464a-8074-2a60bb18ef20/datasets)

**Create Evaluation Dataset:**
```bash
python scripts/create_langsmith_dataset.py
```

**Run LangSmith Evaluation:**
```bash
python -m experiments.langsmith_eval
```

This evaluates:
- Verification correctness
- Agent behavior across predefined test scenarios
- Payment intent classification accuracy
- Call outcome recording

Results are viewable in:
- LangSmith → Datasets → debt-collection-eval
- LangSmith → Traces → Real-time conversation traces

## Test Scenarios Coverage

All 6 scenarios passing in LangSmith evaluation:

1. **Happy Path PTP** - Customer commits to payment on a specific date
   - Example: "I want to pay" → "5th January"
   - Expected: `is_verified: true`, `payment_status: willing`, `call_outcome: ptp_recorded`
   - PTP is automatically recorded with reference number

2. **Already Paid** - Customer claims payment was already made
   - Example: "I already paid last week"
   - Expected: `is_verified: true`, `payment_status: paid`, `call_outcome: paid`
   - Agent acknowledges and confirms verification will be done

3. **Dispute** - Customer disputes the debt validity
   - Example: "This is wrong, I never took this loan"
   - Expected: `is_verified: true`, `payment_status: disputed`, `call_outcome: disputed`
   - Dispute ticket created with reference number (e.g., DSP0001)

4. **Negotiate Accept** - Customer negotiates and accepts a payment plan
   - Example: "I can't pay full" → "3 month plan"
   - Expected: `is_verified: true`, `payment_status: willing`, `call_outcome: ptp_recorded`
   - Payment plan selected and PTP recorded with plan details

5. **Verification Failed** - Customer fails identity verification after 3 attempts
   - Example: Wrong DOB entered 3 times
   - Expected: `is_verified: false`, `call_outcome: verification_failed`
   - Call ends without disclosure

6. **Callback Request** - Customer requests a callback
   - Example: "Call me next week"
   - Expected: `is_verified: true`, `payment_status: callback`, `call_outcome: callback`
   - Callback request acknowledged

**Note:** The system handles various wordings and phrasings for each scenario. See "Robustness Features" below.

View detailed results: [LangSmith Dataset](https://smith.langchain.com/o/c2bf1b47-4401-464a-8074-2a60bb18ef20/datasets)

## Evaluation Logic

Custom evaluators implemented:

- **verified_correct**: Checks if agent verification outcome matches expected result
- **payment_status_correct**: Validates payment status classification
- **call_outcome_correct**: Verifies final call outcome
- **check_scenario_outcomes**: Scenario-specific validation (PTP recorded, dispute recorded, etc.)

Experiments are versioned automatically (v3-required-cases-*) for comparison.

## Key Features

### Core Capabilities
- **Secure DOB-based identity verification** (max 3 attempts, multiple format support)
- **Natural language intent classification** using Azure OpenAI with enhanced Hinglish support
- **Flexible negotiation** with multiple payment plans (EMI, partial, deferred)
- **PTP (Promise to Pay) recording** with automatic reference number generation
- **Dispute handling** with ticket creation and tracking
- **Complete LangSmith tracing and evaluation**
- **Proper state management** with awaiting_user flags
- **Robust error handling** and graceful failures
- **100% test scenario pass rate** (180/180 Hinglish test cases)
- **Hinglish language support** for authentic Indian customer interactions

### Robustness Features
- **Comprehensive intent classification** - Handles 50+ variations of customer responses:
  - Paid: "already paid", "payment done", "cleared", "settled", "transferred", "payement successfull ho gya"
  - Disputed: "never took", "not mine", "fraud", "wrong person", "unauthorized", "maine liya hi nahi"
  - Callback: "call later", "not available", "out of town", "busy now", "baad mein call karna"
  - Unable: "lost job", "no money", "struggling", "financial difficulty", "paise nahi hain", "job chali gayi"
  - Willing: "can't pay full", "installment", "payment plan", "will pay", "installment mein pay kar sakta"
  - **Hinglish phrases**: 30 variations per workflow with authentic Indian English/Hindi mix

- **Flexible date extraction** - Supports multiple formats:
  - Natural: "5th January", "January 5th", "Jan 5th"
  - Numeric: "05-01-2025", "05/01/2025"
  - Relative: "tomorrow", "next week", "next month"
  - Standalone: "15th" (assumes current/next month)

- **Smart amount extraction** - Handles various currency formats:
  - "₹45000", "Rs 45000", "45000 rupees", "45,000"

- **Intelligent plan detection** - Recognizes plan selection through:
  - Month count: "3 month", "3-month"
  - Plan numbers: "plan 1", "option 2"
  - Position words: "first", "second", "third"
  - Acceptance phrases: "works for me", "sounds good", "i accept"

### User Interface
- **Modern web interface** with React and Tailwind CSS
- **Enter key support** - Press Enter to submit phone number and messages
- **Real-time chat** with message bubbles
- **Visual payment plan options** display
- **Responsive design** for desktop and mobile

## Design Decisions

- **LangGraph** chosen for explicit state transitions and auditability
- **LangSmith** used for real-world observability (not mock logging)
- **Deterministic fallback** added to prevent LLM failures blocking execution
- **No external databases** — fully self-contained as per assignment scope
- **Awaiting_user flags** implemented for proper conversation flow control
- **State propagation** carefully managed in evaluation scripts to ensure accurate testing
- **Hybrid classification approach** - Rule-based patterns for speed + LLM for complex cases
- **Web-first architecture** - FastAPI backend with React frontend for modern UX

## Challenges Faced & Solutions

### 1. State Management in Evaluation
**Problem**: User inputs were not being propagated correctly to the graph, resulting in empty `last_user_input` during verification.

**Solution**: Refactored the `provide_input_and_continue` helper to create a new state dict instead of mutating in place, ensuring all state updates are properly passed to graph invocations.

### 2. Verification Flow Control
**Problem**: The graph was not waiting for user input at critical points, causing verification to run with empty responses.

**Solution**: Added `awaiting_user` flags to all nodes that require user input (greeting, verification, disclosure), allowing the evaluation script to properly pause and resume execution.

### 3. DOB Matching Reliability
**Problem**: Date of birth verification was failing due to format variations (e.g., "15-03-1985" vs "15/03/1985").

**Solution**: Implemented robust DOB matching with normalization, supporting multiple separators (-, /, space) and both exact and substring matching.

### 4. Merge Conflicts During Integration
**Problem**: Multiple team members working on the same files caused merge conflicts.

**Solution**: Established feature-branch workflow and used `git checkout --ours` strategy to resolve conflicts by keeping the most recent working versions.

### 5. Intent Classification Accuracy & Hinglish Support
**Problem**: Customer responses with different wordings (e.g., "I can't pay full") were being misclassified as "disputed" instead of "willing". Limited Hinglish language support for Indian customers.

**Solution**: 
- Expanded rule-based patterns to cover 50+ variations per intent category
- **Added comprehensive Hinglish phrase support** with 30 variations per workflow
- Improved Azure OpenAI prompt with clear examples and edge case guidance
- Enhanced fallback logic to default to "willing" for payment-related responses
- Added smart pattern matching for partial payment willingness
- **Implemented authentic Indian English/Hindi mix phrases** like "payement successfull ho gya", "paise nahi hain", "job chali gayi"
- **Achieved 100% test pass rate** (180/180 Hinglish test cases)

### 6. PTP Recording and Plan Detection
**Problem**: Payment commitments weren't being properly recorded, and plan selection wasn't detected reliably.

**Solution**:
- Integrated `save_ptp()` function in negotiation node when commitment is made
- Enhanced plan detection with multiple strategies (month count, position words, acceptance phrases)
- Improved date extraction to handle natural language dates ("5th January", "tomorrow")
- Added automatic amount detection for direct payment commitments

### 7. Date and Amount Extraction
**Problem**: Limited support for various date and amount formats used by customers.

**Solution**:
- Implemented comprehensive date parsing supporting natural language, numeric, and relative dates
- Enhanced amount extraction with multiple currency symbol patterns
- Added relative date calculation ("tomorrow", "next week", "next month")
