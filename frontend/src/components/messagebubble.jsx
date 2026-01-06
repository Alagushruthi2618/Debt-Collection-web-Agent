function MessageBubble({ role, text }) {
  return (
    <div className="message-row">
      <div className={`bubble ${role}`}>{text}</div>
    </div>
  );
}

export default MessageBubble;
