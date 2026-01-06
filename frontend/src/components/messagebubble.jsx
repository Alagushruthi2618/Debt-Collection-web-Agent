function MessageBubble({ role, text }) {
  return <div className={`bubble ${role}`}>{text}</div>;
}

export default MessageBubble;
