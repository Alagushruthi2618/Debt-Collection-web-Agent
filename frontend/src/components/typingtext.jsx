import { useState, useEffect } from "react";

function TypingText({ text, speed = 30, onComplete }) {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!text) {
      setDisplayedText("");
      setIsComplete(false);
      return;
    }

    // Show the full text immediately like WhatsApp
    setDisplayedText(text);
    setIsComplete(true);
    
    if (onComplete) {
      setTimeout(() => {
        onComplete();
      }, 100); // Small delay for natural feel
    }
  }, [text, onComplete]);

  return (
    <span>
      {displayedText}
    </span>
  );
}

export default TypingText;

