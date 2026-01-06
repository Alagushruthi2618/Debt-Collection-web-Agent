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
      <div className="app">
        <h2>Enter your phone number to start chat</h2>
        <input
          type="tel"
          placeholder="Enter phone number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          style={{ padding: "8px", fontSize: "16px" }}
        />
        <button
          onClick={initChat}
          disabled={loading || !phone}
          style={{ padding: "8px 16px", marginLeft: "10px", fontSize: "16px" }}
        >
          {loading ? "Starting..." : "Start Chat"}
        </button>
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
