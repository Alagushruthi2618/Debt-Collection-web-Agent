import MessageBubble from "./messagebubble";

function ChatWindow({ messages, isComplete }) {
  return (
    <div className="chat-window">
      <div className="chat-header">
        ABC Finance • Virtual Agent
      </div>

      <div className="chat-body">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.content} />
        ))}

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
