import { useState, useEffect, useRef } from "react";
import ChatWindow from "./components/chatwindow";
import UserInput from "./components/userinput";
import QuickReplies from "./components/quickreplies";
import ConversationCompletion from "./components/conversationcompletion";
import FeedbackModal from "./components/feedbackmodal";
import FloatingPayButton from "./components/floatingpaybutton";
import ErrorBoundary from "./components/errorboundary";
import { startChat, sendChatMessage, submitFeedback } from "./api/chatapi";
import predixionLogo from "./assets/predixion-logo.png";

import "./styles/design-system.css";

// Force cache refresh
console.log('App loaded at:', new Date().toISOString());

function App() {
  const [phone, setPhone] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [callState, setCallState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);
  const [error, setError] = useState(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [payNowClicked, setPayNowClicked] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [callState?.messages]);

  // Reset error when starting new chat
  useEffect(() => {
    if (started) {
      setError(null);
    }
  }, [started]);

  async function initChat() {
    if (!phone.trim()) {
      setError("Please enter a valid phone number");
      return;
    }
    
    setLoading(true);
    setError(null);
    setIsTyping(true); // Show typing indicator while initializing
    
    try {
      // Add a small delay to make the initial greeting feel natural
      const data = await startChat(phone.trim());
      
      // Add delay before showing the greeting (1-2 seconds)
      const delay = 1000 + Math.random() * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
      
      setIsTyping(false);
      setSessionId(data.session_id);
      // Ensure all required fields are present with safe defaults
      const initialState = {
        messages: data.messages || [],
        stage: data.stage || "init",
        awaiting_user: data.awaiting_user !== undefined ? data.awaiting_user : false,
        offered_plans: data.offered_plans || [],
        is_complete: data.is_complete || false,
        payment_status: data.payment_status || null,
        is_verified: data.is_verified || false,
        customer_name: data.customer_name || null,
        outstanding_amount: data.outstanding_amount !== undefined ? data.outstanding_amount : null,
        days_past_due: data.days_past_due !== undefined ? data.days_past_due : 0,
        loan_id: data.loan_id || null,
      };
      setCallState(initialState);
      setStarted(true);
    } catch (err) {
      console.error("Init error:", err);
      setIsTyping(false);
      const errorMessage = err.message || "Failed to start chat. Please check if the phone number is valid.";
      setError(errorMessage);
      // Show specific error for customer not found
      if (errorMessage.includes("not found") || errorMessage.includes("404")) {
        setError("Customer not found. Please use a valid test phone number (e.g., +919876543210)");
      }
    } finally {
      setLoading(false);
    }
  }

  function handlePayNow() {
    handleSend("I'd like to see payment options");
  }

  async function handleSend(input) {
    // Prevent sending if not awaiting user or if conversation is complete
    if (!callState?.awaiting_user || callState?.is_complete) {
      return;
    }

    // Prevent sending empty messages
    if (!input || !input.trim()) {
      return;
    }

    // Prevent sending if already loading
    if (loading) {
      return;
    }

    setLoading(true);
    setError(null);
    
    // Show typing indicator immediately
    setIsTyping(true);
    
    // Add a minimum delay to make it feel natural (1-2 seconds)
    const minDelay = 1000 + Math.random() * 1000; // 1-2 seconds
    
    try {
      const startTime = Date.now();
      const data = await sendChatMessage(sessionId, input.trim());
      const elapsedTime = Date.now() - startTime;
      
      console.log("[DEBUG] Received response:", {
        is_verified: data.is_verified,
        customer_name: data.customer_name,
        outstanding_amount: data.outstanding_amount,
        days_past_due: data.days_past_due,
        loan_id: data.loan_id,
        stage: data.stage
      });
      
      // If response came too fast, add delay to make it feel natural
      if (elapsedTime < minDelay) {
        await new Promise(resolve => setTimeout(resolve, minDelay - elapsedTime));
      }
      
      // Update state with response (this will trigger the typing animation)
      // Preserve existing state values if new ones aren't provided
      setCallState(prevState => {
        try {
          const updatedState = {
            ...prevState,
            ...data,
            messages: Array.isArray(data.messages) ? data.messages : (prevState?.messages || []),
            stage: data.stage || prevState?.stage || "unknown",
            awaiting_user: data.awaiting_user !== undefined ? data.awaiting_user : (prevState?.awaiting_user ?? false),
            offered_plans: Array.isArray(data.offered_plans) ? data.offered_plans : (prevState?.offered_plans || []),
            is_complete: data.is_complete || false,
            payment_status: data.payment_status || prevState?.payment_status || null,
            is_verified: data.is_verified !== undefined ? data.is_verified : (prevState?.is_verified || false),
            customer_name: data.customer_name || prevState?.customer_name || null,
            outstanding_amount: data.outstanding_amount !== undefined && data.outstanding_amount !== null ? data.outstanding_amount : (prevState?.outstanding_amount ?? null),
            days_past_due: data.days_past_due !== undefined && data.days_past_due !== null ? data.days_past_due : (prevState?.days_past_due ?? 0),
            loan_id: data.loan_id || prevState?.loan_id || null,
          };
          console.log("[DEBUG] Updated state:", {
            is_verified: updatedState.is_verified,
            has_customer_name: !!updatedState.customer_name,
            has_outstanding_amount: updatedState.outstanding_amount !== null && updatedState.outstanding_amount !== undefined,
            outstanding_amount: updatedState.outstanding_amount,
            days_past_due: updatedState.days_past_due,
            loan_id: updatedState.loan_id
          });
          return updatedState;
        } catch (error) {
          console.error("[ERROR] Failed to update state:", error, { data, prevState });
          // Return previous state if update fails, but merge in new messages
          return {
            ...(prevState || {}),
            messages: Array.isArray(data.messages) ? data.messages : (prevState?.messages || []),
            is_verified: prevState?.is_verified || false,
          };
        }
      });
      
      // Keep typing indicator visible briefly, then hide it so the message can type out
      // The message itself will handle the character-by-character animation
      await new Promise(resolve => setTimeout(resolve, 200));
      setIsTyping(false);
    } catch (err) {
      console.error("Send error:", err);
      setIsTyping(false);
      const errorMessage = err.message || "Failed to send message. Please try again.";
      setError(errorMessage);
      
      // If session expired or not found, allow restart
      if (errorMessage.includes("not found") || errorMessage.includes("404")) {
        setError("Session expired. Please start a new chat.");
        setTimeout(() => {
          handleReset();
        }, 2000);
      }
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setPhone("");
    setSessionId(null);
    setCallState(null);
    setStarted(false);
    setError(null);
    setPayNowClicked(false); // Reset Pay Now clicked state
  }

  // Check if screenshot button should be shown (when payment is disputed or customer says they paid)
  function shouldShowScreenshotButton() {
    if (!callState?.messages) return false;
    
    const paymentStatus = callState.payment_status;
    
    // Show if payment is disputed (even after completion)
    if (paymentStatus === "disputed") {
      console.log("[DEBUG] Showing screenshot button: payment_status is disputed");
      return true;
    }
    
    // Show if payment status is "paid" (even after completion)
    if (paymentStatus === "paid") {
      console.log("[DEBUG] Showing screenshot button: payment_status is paid");
      return true;
    }
    
    // Show if customer mentioned they paid (check all user messages, not just recent)
    // This should work even after completion
    const userMessages = callState.messages.filter(msg => msg.role === "user");
    
    const hasPaidMention = userMessages.some(msg => {
      const content = msg.content?.toLowerCase() || "";
      return content.includes("paid") || 
             content.includes("already paid") || 
             content.includes("i paid") ||
             content.includes("made payment") ||
             content.includes("payment done");
    });
    
    // Show screenshot button if customer says they paid (regardless of completion status)
    if (hasPaidMention) {
      console.log("[DEBUG] Showing screenshot button: user mentioned payment", { paymentStatus, hasPaidMention });
      return true;
    }
    
    console.log("[DEBUG] NOT showing screenshot button", { paymentStatus, messagesCount: callState.messages?.length });
    return false;
  }

  async function handleScreenshotUpload(file) {
    if (!file || !sessionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('screenshot', file);
      formData.append('session_id', sessionId);
      
      const response = await fetch('http://localhost:8000/api/upload-screenshot', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to upload screenshot');
      }
      
      const data = await response.json();
      
      // Update state with the response (includes updated messages and state)
      if (data.messages && data.stage !== undefined) {
        setCallState({
          ...callState,
          messages: data.messages || [],
          stage: data.stage,
          awaiting_user: data.awaiting_user || false,
          offered_plans: data.offered_plans || [],
          is_complete: data.is_complete || false,
          payment_status: data.payment_status || null,
          is_verified: data.is_verified || callState?.is_verified || false,
          customer_name: data.customer_name || callState?.customer_name || null,
          outstanding_amount: data.outstanding_amount || callState?.outstanding_amount || null,
          days_past_due: data.days_past_due || callState?.days_past_due || 0,
          loan_id: data.loan_id || callState?.loan_id || null,
        });
      }
      
      // Show success message (optional - the backend already added a message to state)
      // No need to send another message since backend already added it
    } catch (err) {
      console.error("Screenshot upload error:", err);
      setError("Failed to upload screenshot. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleQuickReply(action) {
    if (action === "payment_options") {
      handleSend("I'd like to see payment options");
    } else if (action === "account_details") {
      handleSend("Can you provide my account details?");
    } else if (action === "request_callback") {
      handleSend("I would like to request a callback. What times are available?");
    } else if (action === "need_help") {
      handleSend("I need help");
    }
  }

  function handlePaymentClick() {
    handleSend("I'd like to see payment options");
  }

  function handleRateConversation() {
    setShowFeedbackModal(true);
  }

  async function handleFeedbackSubmit(feedbackData) {
    try {
      await submitFeedback(sessionId, feedbackData.rating, feedbackData.feedback);
      // Success is handled by the modal closing
    } catch (err) {
      console.error("Feedback submission error:", err);
      throw err; // Let the modal handle the error display
    }
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      {!started ? (
        <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 space-y-6 border border-gray-100">
          {/* Logo and Header */}
          <div className="text-center mb-6">
            <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center bg-black rounded-2xl shadow-lg">
  <img
    src={predixionLogo}
    alt="Predixion"
    className="w-10 h-10 object-contain"
  />
</div>

            <h1 className="text-2xl font-semibold text-gray-900">
              Welcome to Predixion Finance
            </h1>
            <p className="text-gray-600">
              Enter your phone number to get started with your debt collection assistant
            </p>
          </div>

          {error && (
            <div className="px-4 py-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">Phone Number</label>
            <div className="relative">
              <select
                value={phone}
                onChange={(e) => {
                  setPhone(e.target.value);
                  setError(null);
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && phone.trim() && !loading) {
                    e.preventDefault();
                    initChat();
                  }
                }}
                disabled={loading}
                className="input appearance-none bg-white pr-10"
              >
                <option value="">Select phone number</option>
                <option value="+917219559972">+91 72195 59972</option>
                <option value="+919876543210">+91 98765 43210</option>
                <option value="+919876543211">+91 98765 43211</option>
                <option value="+919876543212">+91 98765 43212</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                </svg>
              </div>
            </div>
            <p className="text-xs text-gray-500">
              Test numbers available for demo
            </p>
          </div>

          <button
            onClick={initChat}
            disabled={loading || !phone.trim()}
            className="btn btn-primary btn-lg w-full"
          >
            {loading ? "Starting..." : "Start Chat"}
          </button>
        </div>
      ) : (
        <div className="w-full max-w-md h-[600px] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-gray-100 relative">
          <div className="flex-1 min-h-0 flex flex-col">
            <ChatWindow
              messages={callState?.messages || []}
              isComplete={callState?.is_complete || false}
              messagesEndRef={messagesEndRef}
              onReset={handleReset}
              onOptionClick={handleSend}
              isVerified={callState?.is_verified || false}
              customerName={callState?.customer_name || null}
              outstandingAmount={callState?.outstanding_amount ?? null}
              daysPastDue={callState?.days_past_due ?? 0}
              loanId={callState?.loan_id || null}
              onPayNow={callState?.is_verified ? handlePayNow : null}
              isTyping={isTyping}
              payNowClicked={payNowClicked}
            />
          </div>

          {error && (
            <div className="px-4 py-3 bg-red-50 border-t border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}

          {callState?.is_complete && (
            <ConversationCompletion
              onRateConversation={handleRateConversation}
            />
          )}

          {!callState?.is_complete && (
            <QuickReplies
              onSelect={handleQuickReply}
              onPaymentClick={handlePaymentClick}
              disabled={!callState?.awaiting_user || loading}
              showPayment={true}
            />
          )}

          <UserInput
            onSend={handleSend}
            disabled={callState?.is_complete || !callState?.awaiting_user || loading}
            onScreenshotUpload={handleScreenshotUpload}
            showScreenshotButton={shouldShowScreenshotButton()}
            allowScreenshotAfterComplete={true}
            isThinking={isTyping}
          />

          {/* Floating Pay Now Button - Inside chat container */}
          {callState?.is_verified && !payNowClicked && (
            <FloatingPayButton
              outstandingAmount={callState?.outstanding_amount}
              daysPastDue={callState?.days_past_due}
              onPayNow={handlePayNow}
              isVerified={callState?.is_verified}
            />
          )}
        </div>
      )}

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
        onSubmit={handleFeedbackSubmit}
      />
      </div>
    </ErrorBoundary>
  );
}

export default App;
