import { useEffect, useRef, useState } from "react";
import MessageBubble from "./messagebubble";
import StaticHeader from "./staticheader";
import TypingIndicator from "./typingindicator";
import predixionLogo from "../assets/predixion-logo.png";


function ChatWindow({ 
  messages, 
  isComplete, 
  messagesEndRef, 
  onReset, 
  onOptionClick,
  isVerified,
  customerName,
  outstandingAmount,
  daysPastDue,
  loanId,
  onPayNow,
  isTyping,
  payNowClicked
}) {
  const scrollContainerRef = useRef(null);
  const [fullyTypedMessageIndex, setFullyTypedMessageIndex] = useState(-1);

  // Track when a new assistant message arrives
  useEffect(() => {
    const assistantMessages = messages.filter(m => m.role === "assistant");
    const lastAssistantIndex = messages.findLastIndex(m => m.role === "assistant");
    
    // If we have a new assistant message that hasn't been typed yet
    if (lastAssistantIndex >= 0 && lastAssistantIndex > fullyTypedMessageIndex) {
      // Don't auto-update - let the typing animation complete first
    }
  }, [messages, fullyTypedMessageIndex]);

  // Auto-scroll to bottom when messages change or typing indicator appears
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [messages, isComplete, isTyping]);

  return (
    <div className="flex flex-col h-full">
      {/* Header - StaticHeader when verified, otherwise default header */}
      {isVerified && outstandingAmount !== null && outstandingAmount !== undefined ? (
        <StaticHeader
          customerName={customerName || "Customer"}
          outstandingAmount={outstandingAmount}
          daysPastDue={daysPastDue ?? 0}
          loanId={loanId || "N/A"}
          onPayNow={onPayNow}
          onReset={onReset}
        />
      ) : (
        <div className="px-4 py-4 bg-white border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-md">
  <img
    src={predixionLogo}
    alt="Predixion"
    className="w-6 h-6 object-contain"
  />
</div>

              <div>
                <div className="text-base font-semibold text-gray-900">Predixion Finance Assistant</div>
                <div className="text-sm text-gray-500">Online</div>
              </div>
            </div>
            {onReset && (
              <button
                onClick={onReset}
                className="btn btn-secondary btn-sm"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      )}

      {/* Message area */}
      <div 
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto px-4 py-4 bg-gray-50 flex flex-col gap-3 min-h-0"
      >
        {messages.length === 0 ? (
          <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
            Start conversation...
          </div>
        ) : (
          <>
            {messages.map((m, i) => {
              // Generate timestamp for each message
              const timestamp = m.timestamp || new Date().toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: true 
              });
              
              // Only show typing effect for assistant messages that haven't been fully typed yet
              // The last assistant message that's newer than our tracked index should type out
              const isAssistantMessage = m.role === "assistant";
              const shouldShowTyping = isAssistantMessage && i > fullyTypedMessageIndex;
              
              return (
                <MessageBubble 
                  key={i} 
                  role={m.role} 
                  text={m.content} 
                  timestamp={timestamp} 
                  onOptionClick={onOptionClick}
                  isTyping={shouldShowTyping}
                  onTypingComplete={() => {
                    // Mark this message as fully typed
                    if (i > fullyTypedMessageIndex) {
                      setFullyTypedMessageIndex(i);
                    }
                  }}
                />
              );
            })}
            {/* Show typing indicator while waiting for response */}
            {isTyping && (
              <TypingIndicator />
            )}
            {/* Invisible element at the end for scrolling */}
            <div ref={messagesEndRef} />
          </>
        )}

        {isComplete && (
          <div className="px-4 py-3 bg-green-50 text-green-800 text-center font-medium border border-green-200 text-sm rounded-lg">
            Conversation completed
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatWindow;
