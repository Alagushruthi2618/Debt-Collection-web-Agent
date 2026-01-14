import { useState, useEffect } from "react";
import TypingText from "./typingtext";
import predixionLogo from "../assets/predixion-logo.png";

function MessageBubble({ role, text, timestamp, onOptionClick, isTyping: isCurrentlyTyping, onTypingComplete }) {
  const [typingComplete, setTypingComplete] = useState(!isCurrentlyTyping);
  
  // Reset typing complete state when a new typing session starts
  useEffect(() => {
    if (isCurrentlyTyping) {
      setTypingComplete(false);
    }
  }, [isCurrentlyTyping, text]);
  const isUser = role === "user";
  const currentTime = timestamp || new Date().toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true 
  });
  
  // Check if this is a payment options message
  // Look for patterns that indicate payment options: numbered list format (1. ... 2. ...) or key phrases
  const hasNumberedOptions = /\d+\.\s+[^:]+:\s+/.test(text);
  const hasPaymentOptionPhrases = text.includes("Let me show you some options") || 
    text.includes("Here are some payment options") ||
    text.includes("Here are some options") ||
    text.includes("payment options") ||
    text.includes("Which option works best");
  const isPaymentOptionsMessage = !isUser && (hasNumberedOptions || hasPaymentOptionPhrases);
  
  // Parse payment options from text
  const parsePaymentOptions = (text) => {
    const lines = text.split('\n');
    const intro = [];
    const options = [];
    let inOptions = false;
    let closingQuestion = null;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      
      // Check if line starts with a number followed by a dot (e.g., "1. ", "2. ")
      const optionMatch = trimmed.match(/^(\d+)\.\s+(.+?):\s+(.+)$/);
      if (optionMatch) {
        inOptions = true;
        // Remove markdown asterisks from the name
        const cleanName = optionMatch[2].replace(/\*\*/g, '').trim();
        options.push({
          number: optionMatch[1],
          name: cleanName,
          description: optionMatch[3]
        });
      } else if (trimmed && !inOptions) {
        intro.push(trimmed);
      } else if (trimmed && inOptions && !optionMatch) {
        // This is the closing question
        closingQuestion = trimmed;
      }
    }
    
    return { 
      intro: intro.join(' '), 
      options,
      closingQuestion 
    };
  };
  
  // For typing effect, we need the full text to type out
  // But for display, we parse it if it's a payment options message
  const fullTextForTyping = text;
  const formattedContent = isPaymentOptionsMessage ? parsePaymentOptions(text) : null;
  
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center mr-2 flex-shrink-0 shadow-sm">
  <img
    src={predixionLogo}
    alt="Predixion"
    className="w-5 h-5 object-contain"
  />
</div>

      )}
      <div className={`flex flex-col ${isUser ? "items-end" : "items-start"} max-w-[75%]`}>
        {!isUser && (
          <div className="text-xs text-gray-500 mb-1 px-1">Predixion Finance Assistant</div>
        )}
        <div
          className={`px-4 py-3 text-sm leading-relaxed rounded-lg break-words ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-white text-gray-900 border border-gray-200"
          }`}
        >
          {formattedContent ? (
            <div>
              {!isUser && isCurrentlyTyping && !typingComplete ? (
                // While typing, show the typing effect on the full text
                <TypingText 
                  text={fullTextForTyping} 
                  speed={30}
                  onComplete={() => {
                    setTypingComplete(true);
                    if (onTypingComplete) {
                      onTypingComplete();
                    }
                  }}
                />
              ) : (
                // After typing is complete, show formatted content
                <>
                  {formattedContent.intro && (
                    <div className="mb-3">{formattedContent.intro}</div>
                  )}
                  {formattedContent.options.length > 0 && (
                    <div className="space-y-2 mb-3">
                      {formattedContent.options.map((option, idx) => (
                        <div 
                          key={idx}
                          onClick={() => onOptionClick && onOptionClick(`${option.number}. ${option.name}`)}
                          className="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:bg-gray-100 hover:border-gray-300 transition-colors cursor-pointer active:bg-gray-200"
                        >
                          <div className="flex items-start gap-2">
                            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-semibold flex items-center justify-center mt-0.5">
                              {option.number}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-semibold text-gray-900 mb-1">
                                {option.name}
                              </div>
                              <div className="text-gray-700 text-sm leading-relaxed">
                                {option.description}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {formattedContent.closingQuestion && (
                    <div className="text-gray-800 font-medium">
                      {formattedContent.closingQuestion}
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="whitespace-pre-wrap">
              {!isUser && isCurrentlyTyping && !typingComplete ? (
                <TypingText 
                  text={text} 
                  speed={30} 
                  onComplete={() => {
                    setTypingComplete(true);
                    if (onTypingComplete) {
                      onTypingComplete();
                    }
                  }}
                />
              ) : (
                text
              )}
            </div>
          )}
        </div>
        <div className={`text-xs text-gray-400 mt-1 px-1 ${isUser ? "text-right" : "text-left"}`}>
          {currentTime}
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
