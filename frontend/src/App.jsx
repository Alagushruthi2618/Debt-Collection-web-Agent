import { useState } from "react";
import ChatWindow from "./components/chatwindow";
import UserInput from "./components/userinput";
import { startChat, sendChatMessage } from "./api/chatapi";

function App() {
  const [phone, setPhone] = useState("");          // store user phone input
  const [sessionId, setSessionId] = useState(null);
  const [callState, setCallState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [started, setStarted] = useState(false);  // track if session started

  // Start chat session
  async function initChat() {
    if (!phone) return alert("Please enter your phone number");
    setLoading(true);
    try {
      const data = await startChat(phone);
      setSessionId(data.session_id);
      setCallState(data);
      setStarted(true);
    } catch (err) {
      console.error("Init error:", err);
      alert("Failed to start chat. Check console.");
    }
    setLoading(false);
  }

  // Send user message
  async function handleSend(input) {
    if (!callState?.awaiting_user) return;
    setLoading(true);
    try {
      const data = await sendChatMessage(sessionId, input);
      setCallState(data);
    } catch (err) {
      console.error("Send error:", err);
    }
    setLoading(false);
  }

  // If session not started, show phone input
  if (!started) {
    return (
      <div className="app" style={{ 
        display: "flex", 
        flexDirection: "column", 
        justifyContent: "center", 
        alignItems: "center",
        padding: "40px 20px",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
      }}>
        <div style={{
          background: "white",
          padding: "40px",
          borderRadius: "20px",
          boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)",
          maxWidth: "500px",
          width: "100%"
        }}>
          <h2>Enter your phone number to start chat</h2>
          <input
            type="tel"
            placeholder="Enter phone number (e.g., +919876543210)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && phone && !loading) {
                initChat();
              }
            }}
            style={{ 
              width: "100%",
              padding: "14px 20px", 
              fontSize: "16px",
              marginTop: "24px",
              border: "2px solid #e5e7eb",
              borderRadius: "12px",
              outline: "none",
              transition: "all 0.2s ease"
            }}
          />
          <button
            onClick={initChat}
            disabled={loading || !phone}
            style={{ 
              width: "100%",
              padding: "14px 32px", 
              marginTop: "16px", 
              fontSize: "16px",
              fontWeight: "600",
              background: loading || !phone ? "#d1d5db" : "#8b5cf6",
              color: "white",
              border: "none",
              borderRadius: "12px",
              cursor: loading || !phone ? "not-allowed" : "pointer",
              transition: "all 0.2s ease"
            }}
          >
            {loading ? "Starting..." : "Start Chat"}
          </button>
        </div>
      </div>
    );
  }

  if (!callState) return <div className="app">Loading chat...</div>;

  return (
    <div className="app">
      <ChatWindow messages={callState.messages} isComplete={callState.is_complete} />

      {/* Only user input now */}
      <UserInput
        onSend={handleSend}
        disabled={!callState.awaiting_user || loading}
      />
    </div>
  );
}

export default App;
