import { useEffect, useRef } from "react";
import MessageBubble from "./messagebubble";

function ChatWindow({ messages, isComplete }) {
  const chatBodyRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-window">
      <div className="chat-header">
        ABC Finance • Virtual Agent
      </div>

      <div className="chat-body" ref={chatBodyRef}>
        {messages.length === 0 ? (
          <div style={{ 
            textAlign: "center", 
            color: "#9ca3af", 
            padding: "40px 20px",
            fontSize: "15px"
          }}>
            Start the conversation...
          </div>
        ) : (
          messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} text={m.content} />
          ))
        )}

        {isComplete && (
          <div className="complete-banner">
            ✅ Call Completed
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatWindow;
