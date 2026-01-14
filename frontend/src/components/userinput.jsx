import { useState, useRef, useEffect } from "react";

function UserInput({ onSend, disabled, onScreenshotUpload, showScreenshotButton = false, allowScreenshotAfterComplete = false, isThinking = false }) {
  const [text, setText] = useState("");
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  // Keep focus on input after sending message
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  function handleSend() {
    // Prevent sending if disabled or empty
    if (disabled || !text.trim()) return;
    
    const messageToSend = text.trim();
    setText("");
    
    // Call the onSend handler
    if (onSend) {
      onSend(messageToSend);
    }
    
    // Focus input after sending
    setTimeout(() => {
      if (inputRef.current && !disabled) {
        inputRef.current.focus();
      }
    }, 100);
  }

  function handleKeyPress(e) {
    // Only handle Enter key if not disabled
    if (e.key === "Enter" && !e.shiftKey && !disabled) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleScreenshotClick() {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    if (file && onScreenshotUpload) {
      onScreenshotUpload(file);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }

  return (
    <div className="flex-shrink-0">
      <div className="flex gap-2 px-4 py-3 bg-white border-t border-gray-200">
        {showScreenshotButton && (
          <button
            onClick={handleScreenshotClick}
            disabled={false}
            className="btn btn-secondary w-10 h-10 p-0 flex items-center justify-center"
            title="Upload screenshot"
          >
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        )}
        <input
          ref={fileInputRef}
          type="file"
          accept="*/*"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <input
          ref={inputRef}
          type="text"
          value={text}
          disabled={disabled}
          onChange={(e) => setText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            disabled && !isThinking 
              ? "Chat completed" 
              : isThinking 
              ? "Assistant is typing..." 
              : "Type your message..."
          }
          className="input"
        />
        <button
          onClick={handleSend}
          disabled={disabled || !text.trim()}
          className="btn btn-primary w-10 h-10 p-0 flex items-center justify-center"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M22 2L11 13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M22 2L15 22L11 13L2 9L22 2Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default UserInput;
