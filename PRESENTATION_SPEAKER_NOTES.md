# Debt Collection Web Agent - Presentation Speaker Notes

## Slide 1: Title Slide
**"AI-Powered Debt Collection Agent"**

**Opening:**
- Good morning/afternoon everyone. Today I'm excited to present our Debt Collection Web Agent project.
- This is an AI-powered conversational agent built using LangGraph and LangSmith for debt collection calls.
- I worked primarily on the backend architecture and integration, while my colleague Shruthi developed the frontend interface.
- Let me walk you through what we've built and how it works.

---

## Slide 2: Project Overview

**Key Points:**
- **What it does:** Simulates real-world debt collection phone calls through a web interface
- **Core Purpose:** Automates the debt collection conversation flow while maintaining professionalism and compliance
- **Key Capabilities:**
  - Verifies customer identity using DOB-based authentication
  - Explains outstanding dues and legal disclosures
  - Handles multiple customer response scenarios (paid, disputed, unable, willing, callback)
  - Negotiates payment plans (EMI, partial, deferred payments)
  - Records Promise-to-Pay (PTP) commitments
  - Tracks call outcomes and generates summaries

**Transition:** Now let me show you the architecture that makes this possible.

---

## Slide 3: Architecture Overview

**System Architecture:**
- **Three-Layer Architecture:**
  1. **Frontend Layer** (React + Vite) - Modern web interface built by Shruthi
  2. **Backend Layer** (FastAPI) - REST API that I developed to bridge frontend and agent
  3. **Agent Layer** (LangGraph) - State machine orchestrating the conversation flow

**Technology Stack:**
- **Frontend:** React 19, Vite, Tailwind CSS
- **Backend:** FastAPI, Python, Uvicorn
- **Agent Core:** LangGraph for state machine, Google Gemini for LLM, LangSmith for observability
- **Session Management:** In-memory storage (designed for easy upgrade to Redis)

**Key Design Decision:**
- We chose LangGraph because it provides explicit state transitions, making the conversation flow auditable and debuggable
- This is critical for debt collection where compliance and traceability are essential

---

## Slide 4: Backend Architecture (My Work)

**What I Built:**

### 1. FastAPI Application (`backend/app.py`)
- **Purpose:** Main entry point for the web API
- **Features:**
  - CORS middleware configured for frontend communication
  - Health check endpoint for monitoring
  - Clean separation of concerns with route modules

### 2. Session Management (`backend/session_store.py`)
- **Challenge:** Each conversation needs isolated state
- **Solution:** 
  - Unique session IDs generated using UUID
  - In-memory dictionary mapping session_id → CallState
  - Designed for easy migration to Redis in production
- **Why it matters:** Allows multiple concurrent conversations without state conflicts

### 3. API Endpoints (`backend/routes/chat.py`)
- **Two main endpoints:**
  
  **POST `/api/init`**
  - Initializes new conversation session
  - Takes phone number, creates initial state, invokes graph for greeting
  - Returns session_id and initial messages
  
  **POST `/api/chat`**
  - Handles user input during conversation
  - Validates session exists and call isn't complete
  - Updates state with user input
  - Invokes LangGraph agent
  - Returns updated messages, stage, and flags

**Key Implementation Details:**
- State is never mutated in place - always use returned state from graph invocation
- Proper error handling with HTTP status codes (404 for missing session, 400 for invalid input, 500 for server errors)
- Recursion limit set to 25 to prevent infinite loops

---

## Slide 5: Backend State Flow

**How Backend Orchestrates Conversations:**

1. **Initialization Flow:**
   - Frontend sends phone number → `/api/init`
   - Backend calls `create_initial_state(phone)` to load customer/loan data
   - Backend invokes LangGraph with initial state
   - Graph processes through greeting node
   - Returns session_id and initial greeting message

2. **Conversation Flow:**
   - Frontend sends user input → `/api/chat` with session_id
   - Backend retrieves state from session store
   - Adds user message to messages array
   - Sets `last_user_input` and `awaiting_user = False`
   - Invokes `app.invoke(state)` - this triggers LangGraph processing
   - Graph nodes process input, update state, set `awaiting_user = True` when waiting
   - Backend updates session store and returns response

3. **State Management:**
   - Backend reads/writes: `messages`, `stage`, `awaiting_user`, `offered_plans`, `is_complete`
   - Never directly modifies business logic (handled by nodes)
   - Ensures clean separation between API layer and agent logic

**Why This Design:**
- Backend is a thin orchestration layer
- All business logic lives in LangGraph nodes
- Makes testing and debugging easier
- Allows frontend to be framework-agnostic

---

## Slide 6: LangGraph Agent Flow (Backend Integration)

**The Conversation State Machine:**

**Nodes in the Flow:**
1. **Greeting Node** - Initial call greeting and customer confirmation
2. **Verification Node** - DOB-based identity verification (max 3 attempts)
3. **Disclosure Node** - Legal disclosure and outstanding amount
4. **Payment Check Node** - Classifies customer intent (paid/disputed/callback/unable/willing)
5. **Negotiation Node** - Offers payment plans and handles plan selection
6. **Closing Node** - Records outcome and ends call

**Routing Logic:**
- `should_continue()` function determines next node based on state
- Uses flags: `awaiting_user`, `is_verified`, `payment_status`, `is_complete`
- Prevents infinite loops and ensures proper sequencing

**Backend's Role:**
- Backend doesn't make routing decisions - that's handled by `should_continue()`
- Backend simply invokes the graph and returns the updated state
- This keeps the API stateless and the agent logic centralized

---

## Slide 7: Frontend Architecture (Shruthi's Work)

**What Shruthi Built:**

### Component Structure:
- **App.jsx** - Main application component managing session state
- **ChatWindow** - Displays conversation messages
- **MessageBubble** - Individual message rendering (user/assistant)
- **UserInput** - Input field with Enter key support
- **NegotiationsOption** - Visual display of payment plans
- **StatusBanner** - Shows call status and stage

### Key Features:
- **Modern UI** with Tailwind CSS
- **Real-time chat interface** with message bubbles
- **Enter key support** for quick input
- **Visual payment plan options** when offered
- **Responsive design** for desktop and mobile
- **Loading states** and disabled states for better UX

### API Integration (`api/chatapi.js`):
- Clean separation of API calls from UI
- `startChat(phone)` - Initializes session
- `sendChatMessage(sessionId, input)` - Sends user input
- Error handling and user feedback

**Why This Matters:**
- Professional, user-friendly interface
- Makes the agent accessible to non-technical users
- Provides visual feedback throughout the conversation

---

## Slide 8: Key Features - Intent Classification

**Robust Payment Intent Classification:**

**The Challenge:**
- Customers express themselves in many different ways
- "I already paid" vs "payment done" vs "cleared" - all mean the same thing
- Need to handle 50+ variations per intent category

**The Solution:**
- **Hybrid Approach:** Rule-based patterns + LLM classification
- **Primary:** Google Gemini LLM for complex cases
- **Fallback:** Deterministic rule-based patterns for reliability
- **Priority Order:** paid → disputed → callback → unable → willing

**Intent Categories:**
1. **Paid:** "already paid", "payment done", "cleared", "settled", "transferred"
2. **Disputed:** "never took", "not mine", "fraud", "wrong person", "unauthorized"
3. **Callback:** "call later", "not available", "out of town", "busy now"
4. **Unable:** "lost job", "no money", "struggling", "financial difficulty"
5. **Willing:** "can't pay full", "installment", "payment plan", "will pay"

**Why This Matters:**
- Handles real-world language variations
- Prevents misclassification that could lead to poor customer experience
- Fallback ensures system never fails due to LLM issues

---

## Slide 9: Key Features - Negotiation & Plan Detection

**Intelligent Payment Plan Negotiation:**

**What Happens:**
1. Agent offers multiple payment plans (3-month, 6-month, etc.)
2. Customer can select plan in various ways:
   - "3 month plan" or "3-month"
   - "plan 1" or "option 2"
   - "first plan" or "second option"
   - "works for me" (accepts default)
3. Agent extracts payment date from natural language:
   - "5th January", "January 5th", "Jan 5th"
   - "05-01-2025", "05/01/2025"
   - "tomorrow", "next week", "next month"
   - "15th" (assumes current/next month)

**Smart Detection:**
- Multiple strategies for plan selection (month count, position words, acceptance phrases)
- Flexible date parsing supporting natural language
- Amount extraction from various currency formats (₹45000, Rs 45000, 45,000 rupees)

**When Commitment is Complete:**
- Agent detects both amount AND date
- Automatically saves PTP record with reference number
- Moves to closing and ends call professionally

**Backend's Role:**
- Backend receives `offered_plans` array from negotiation node
- Passes it to frontend in API response
- Frontend displays plans visually
- User selection flows back through backend to agent

---

## Slide 10: Key Features - Verification & Security

**DOB-Based Identity Verification:**

**The Process:**
1. Agent asks for date of birth
2. Customer provides DOB in any format
3. System normalizes and matches against customer record
4. Maximum 3 attempts allowed
5. If verification fails after 3 attempts, call ends without disclosure

**Format Support:**
- Multiple separators: "15-03-1985", "15/03/1985", "15 03 1985"
- Flexible matching with normalization
- Handles common variations

**Security Considerations:**
- Verification prevents unauthorized access to account information
- Call terminates if identity cannot be verified
- No disclosure of sensitive information without verification

**Backend Implementation:**
- Verification attempts tracked in state: `verification_attempts`
- `is_verified` flag controls flow to disclosure
- Backend doesn't handle verification logic - that's in verification node
- Backend ensures state is properly persisted between attempts

---

## Slide 11: Test Scenarios & Evaluation

**Comprehensive Test Coverage:**

**6 Core Scenarios (All Passing):**

1. **Happy Path PTP**
   - Customer commits to payment on specific date
   - Expected: `is_verified: true`, `payment_status: willing`, `call_outcome: ptp_recorded`
   - PTP automatically recorded with reference number

2. **Already Paid**
   - Customer claims payment was already made
   - Expected: `payment_status: paid`, `call_outcome: paid`
   - Agent acknowledges and confirms verification

3. **Dispute**
   - Customer disputes debt validity
   - Expected: `payment_status: disputed`, `call_outcome: disputed`
   - Dispute ticket created with reference number (e.g., DSP0001)

4. **Negotiate Accept**
   - Customer negotiates and accepts payment plan
   - Expected: Plan selected, PTP recorded with plan details

5. **Verification Failed**
   - Customer fails identity verification after 3 attempts
   - Expected: `is_verified: false`, `call_outcome: verification_failed`
   - Call ends without disclosure

6. **Callback Request**
   - Customer requests callback
   - Expected: `payment_status: callback`, `call_outcome: callback`
   - Callback request acknowledged

**Evaluation Using LangSmith:**
- All scenarios evaluated automatically
- Custom evaluators validate verification, payment status, and call outcome
- 100% pass rate achieved

---

## Slide 12: Challenges & Solutions

**Challenge 1: State Management in Evaluation**
- **Problem:** User inputs not propagating correctly to graph during evaluation
- **Solution:** Refactored state update logic to create new state dict instead of mutating in place
- **Impact:** Ensured accurate testing and debugging

**Challenge 2: Verification Flow Control**
- **Problem:** Graph not waiting for user input at critical points
- **Solution:** Added `awaiting_user` flags to all nodes requiring input
- **Impact:** Proper pause/resume execution in both web and CLI interfaces

**Challenge 3: Intent Classification Accuracy**
- **Problem:** Different wordings misclassified (e.g., "I can't pay full" as "disputed")
- **Solution:** Expanded rule-based patterns to 50+ variations, improved Gemini prompts, enhanced fallback logic
- **Impact:** Handles real-world language variations reliably

**Challenge 4: Session Management**
- **Problem:** Need to support multiple concurrent conversations
- **Solution:** Implemented session store with unique session IDs, designed for Redis migration
- **Impact:** Scalable architecture ready for production

**Challenge 5: Date and Amount Extraction**
- **Problem:** Limited support for various formats
- **Solution:** Comprehensive parsing supporting natural language, numeric, and relative dates
- **Impact:** Better user experience with flexible input

---

## Slide 13: Demo Flow

**Let me walk you through a typical conversation:**

1. **Initialization:**
   - User enters phone number: `+919876543210`
   - Frontend calls `/api/init`
   - Backend creates session, invokes graph
   - Agent greets: "Hello Rajesh, good day. This is a call from ABC Finance..."

2. **Verification:**
   - Agent: "To verify your identity, could you please provide your date of birth?"
   - User: "15-03-1985"
   - Agent: "Thank you for confirming. I can now discuss your account."

3. **Disclosure:**
   - Agent: "You have an outstanding payment of ₹45,000..."
   - Legal disclosure provided

4. **Payment Check:**
   - User: "I can't pay the full amount"
   - Agent classifies as "willing"

5. **Negotiation:**
   - Agent offers payment plans (3-month, 6-month, etc.)
   - User: "I'll take the 3 month plan"
   - Agent: "Great! When would you like to make your first payment?"
   - User: "5th January"
   - Agent: "Perfect! I've documented your commitment. Your PTP reference number is PTP0001..."

6. **Closing:**
   - Call ends with confirmation message

**Backend's Role Throughout:**
- Manages session state
- Routes messages between frontend and agent
- Ensures state consistency
- Handles errors gracefully

---

## Slide 14: Technical Highlights - Backend

**What Makes the Backend Robust:**

1. **Clean API Design:**
   - RESTful endpoints with proper HTTP methods
   - Standardized request/response models using Pydantic
   - Clear error messages and status codes

2. **State Management:**
   - Immutable state updates (never mutate in place)
   - Proper session isolation
   - Designed for horizontal scaling

3. **Error Handling:**
   - Try-catch blocks around graph invocations
   - Detailed error logging
   - User-friendly error messages

4. **CORS Configuration:**
   - Properly configured for frontend communication
   - Ready for production with domain restrictions

5. **Separation of Concerns:**
   - API layer (routes) separate from business logic (nodes)
   - Session management isolated
   - Easy to test and maintain

**Code Quality:**
- Type hints throughout
- Docstrings for all functions
- Clear variable naming
- Modular structure

---

## Slide 15: Integration Points

**How Backend and Frontend Work Together:**

**Data Flow:**
1. Frontend → Backend: User input via POST `/api/chat`
2. Backend → LangGraph: Invokes agent with state
3. LangGraph → Nodes: Process input, update state
4. Nodes → LangGraph: Return updated state
5. LangGraph → Backend: Return final state
6. Backend → Frontend: Return messages, stage, plans, flags

**State Synchronization:**
- Frontend tracks: `sessionId`, `callState`
- Backend maintains: `session_id → CallState` mapping
- Both stay in sync through API calls

**Key Integration Points:**
- **Session Initialization:** Frontend calls `/api/init`, gets `session_id`
- **Message Exchange:** Frontend sends user input, gets updated messages
- **Plan Display:** Backend sends `offered_plans`, frontend displays visually
- **Call Completion:** Backend sends `is_complete: true`, frontend disables input

**Why This Works:**
- Clear contract between frontend and backend
- Backend is stateless (state in session store)
- Frontend is reactive (updates UI based on state)
- Easy to debug (can test backend independently)

---

## Slide 16: Observability & Monitoring

**LangSmith Integration:**

**What We Track:**
- Every graph invocation is logged
- Node-level execution traces
- Latency metrics for each node
- Token usage for LLM calls
- Errors and exceptions

**Benefits:**
- **Debugging:** Can see exactly what happened in any conversation
- **Performance:** Identify bottlenecks
- **Evaluation:** Automated testing with custom evaluators
- **Compliance:** Full audit trail of all conversations

**Backend's Role:**
- Backend doesn't directly log to LangSmith
- LangGraph automatically traces all invocations
- Backend ensures proper state propagation for accurate traces

**Production Readiness:**
- All conversations are traceable
- Can replay any conversation for debugging
- Performance metrics available
- Error tracking enabled

---

## Slide 17: Production Considerations

**Current State:**
- ✅ Fully functional web application
- ✅ Session management (in-memory)
- ✅ Error handling
- ✅ CORS configured
- ✅ Health check endpoint

**For Production Deployment:**

1. **Session Storage:**
   - Current: In-memory dictionary
   - Production: Redis or database
   - Easy migration path already designed

2. **Security:**
   - Add authentication/authorization
   - Rate limiting
   - Input validation and sanitization
   - HTTPS only

3. **Scalability:**
   - Load balancing
   - Horizontal scaling
   - Database for persistent storage

4. **Monitoring:**
   - Application logging (beyond LangSmith)
   - Health checks and alerts
   - Performance monitoring

5. **Frontend:**
   - Build for production (`npm run build`)
   - Serve static files via CDN or web server
   - Environment-specific API URLs

**Backend is Production-Ready:**
- Clean architecture
- Proper error handling
- Scalable design
- Easy to extend

---

## Slide 18: Key Achievements

**What We Accomplished:**

1. **Complete Web Application:**
   - Functional backend API
   - Modern frontend interface
   - Seamless integration

2. **Robust Agent:**
   - Handles 6 core scenarios
   - 100% test pass rate
   - Handles real-world language variations

3. **Production-Ready Architecture:**
   - Clean separation of concerns
   - Scalable session management
   - Proper error handling

4. **Developer Experience:**
   - Easy to test (CLI and web interfaces)
   - Comprehensive documentation
   - Clear code structure

5. **Observability:**
   - Full LangSmith integration
   - Traceable conversations
   - Performance metrics

**Team Collaboration:**
- Clear division of responsibilities (backend vs frontend)
- Clean API contract
- Successful integration
- Both components work independently and together

---

## Slide 19: Future Enhancements

**Potential Improvements:**

1. **Backend Enhancements:**
   - Redis session storage
   - Authentication/authorization
   - Rate limiting
   - WebSocket support for real-time updates
   - Database integration for persistent storage

2. **Agent Improvements:**
   - Multi-language support
   - Voice integration (text-to-speech, speech-to-text)
   - Sentiment analysis
   - Escalation to human agents

3. **Frontend Enhancements:**
   - Dark mode
   - Conversation history
   - Export conversation transcripts
   - Analytics dashboard

4. **Integration:**
   - CRM system integration
   - Payment gateway integration
   - Email/SMS notifications
   - Reporting and analytics

**Why Current Architecture Supports This:**
- Modular design makes extensions easy
- Clear interfaces between components
- State management is flexible
- API can be extended without breaking changes

---

## Slide 20: Q&A Preparation

**Anticipated Questions & Answers:**

**Q: Why FastAPI instead of Flask/Django?**
- A: FastAPI provides automatic API documentation, type validation with Pydantic, and async support. It's modern, fast, and perfect for API development.

**Q: Why in-memory session storage?**
- A: It's simple for development and demo. The architecture is designed for easy migration to Redis. In production, we'd use Redis for persistence and scalability.

**Q: How does error handling work?**
- A: Backend catches exceptions from graph invocations, logs them, and returns appropriate HTTP status codes. Frontend displays user-friendly error messages.

**Q: Can this handle multiple concurrent users?**
- A: Yes! Each session is isolated with unique session IDs. The current in-memory storage works for moderate load. For high concurrency, we'd use Redis.

**Q: How do you ensure conversation flow correctness?**
- A: LangGraph's state machine enforces proper sequencing. The `should_continue()` function ensures nodes execute in correct order. We also have comprehensive test scenarios.

**Q: What if the LLM fails?**
- A: We have deterministic fallback logic. If Gemini fails, rule-based patterns take over. The system never fails due to LLM issues.

**Q: How do you test the backend?**
- A: We can test API endpoints directly with curl or Postman. We also have CLI interface for manual testing. LangSmith provides automated evaluation.

---

## Slide 21: Closing

**Summary:**
- Built a complete AI-powered debt collection web agent
- Backend provides robust API layer with session management
- Frontend offers modern, user-friendly interface
- Agent handles real-world scenarios with high accuracy
- Full observability and testing in place

**Key Takeaways:**
1. **Architecture Matters:** Clean separation enables independent development and testing
2. **Robustness:** Fallback mechanisms ensure reliability
3. **Observability:** LangSmith integration provides full visibility
4. **Teamwork:** Clear API contract enabled seamless frontend-backend integration

**Thank You:**
- Questions?
- Contact: [Your contact info]

---

## Additional Notes for Presenter

### Timing Guide:
- **Total Presentation:** ~15-20 minutes
- **Overview & Architecture:** 3-4 minutes
- **Backend Deep Dive:** 5-6 minutes (your main section)
- **Frontend Overview:** 2-3 minutes
- **Features & Demo:** 4-5 minutes
- **Q&A:** 5 minutes

### Emphasis Points:
- **Highlight your backend work:** Session management, API design, state orchestration
- **Show integration:** How backend bridges frontend and agent
- **Demonstrate robustness:** Error handling, fallback mechanisms
- **Production readiness:** Scalability considerations, easy migration paths

### Demo Tips:
- Have test phone numbers ready: `+919876543210`, `+919876543211`, `+919876543212`
- Show different scenarios: happy path, dispute, negotiation
- Point out backend logs if possible
- Show LangSmith traces if available

### If Technical Questions Arise:
- Refer to code structure and design decisions
- Explain trade-offs (in-memory vs Redis, etc.)
- Show how architecture supports future enhancements
- Emphasize test coverage and evaluation results

### Confidence Boosters:
- You built a production-ready backend
- Clean architecture with proper separation of concerns
- Comprehensive error handling
- Designed for scalability
- Full integration with frontend and agent
- 100% test pass rate

Good luck with your presentation!


