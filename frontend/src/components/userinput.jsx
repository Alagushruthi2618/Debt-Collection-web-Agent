import { useState } from "react";

function UserInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  function handleSend() {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  }

  return (
    <div style={{ display: "flex", gap: "8px" }}>
      <input
        type="text"
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type your response"
        style={{ flex: 1, padding: "6px" }}
      />
      <button onClick={handleSend} disabled={disabled}>
        Send
      </button>
    </div>
  );
}

export default UserInput;
