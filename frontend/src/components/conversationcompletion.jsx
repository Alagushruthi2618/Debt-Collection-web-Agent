function ConversationCompletion({ onStartAgain, onRateConversation }) {
  return (
    <div className="px-4 py-4 bg-gray-50 border-t border-gray-200">
      <div className="text-center mb-4">
        <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-green-100 mb-2">
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p className="text-sm font-semibold text-gray-900 mb-1">Conversation completed</p>
        <p className="text-xs text-gray-500">Thank you for using our service</p>
      </div>
      
      <div className="flex gap-2">
        <button
          onClick={onStartAgain}
          className="btn btn-secondary flex-1"
        >
          Start again
        </button>
        <button
          onClick={onRateConversation}
          className="btn btn-primary flex-1"
        >
          Rate conversation
        </button>
      </div>
    </div>
  );
}

export default ConversationCompletion;
