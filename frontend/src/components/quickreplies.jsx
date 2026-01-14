function QuickReplies({ onSelect, disabled, showPayment = true, onPaymentClick }) {
  const quickActions = [
    { label: "Payment", action: "payment_options" },
    { label: "Account", action: "account_details" },
    { label: "Callback", action: "request_callback" },
    { label: "Help", action: "need_help" },
  ];

  function handleClick(action) {
    if (disabled) return;
    
    if (action === "payment_options" && onPaymentClick) {
      onPaymentClick();
    } else if (onSelect) {
      onSelect(action);
    }
  }

  return (
    <div className="px-4 py-2 bg-white border-t border-gray-200">
      <div className="flex flex-wrap gap-1.5">
        {quickActions.map((action) => {
          // Only show payment button if showPayment is true
          if (action.action === "payment_options" && !showPayment) {
            return null;
          }
          
          // Make payment button more prominent
          const isPaymentButton = action.action === "payment_options";
          
          return (
            <button
              key={action.action}
              onClick={() => handleClick(action.action)}
              disabled={disabled}
              className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${
                isPaymentButton
                  ? "bg-red-600 text-white hover:bg-red-700"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {action.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default QuickReplies;
