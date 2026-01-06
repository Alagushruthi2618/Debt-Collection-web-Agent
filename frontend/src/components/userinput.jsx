import { useState } from "react";

function UserInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  function handleSend() {
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  }

  function handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="input-area">
      <input
        type="text"
        value={text}
        disabled={disabled}
        onChange={(e) => setText(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your response..."
      />
      <button onClick={handleSend} disabled={disabled || !text.trim()}>
        Send
      </button>
    </div>
  );
}

export default UserInput;
