function PaymentReminder({ outstandingAmount, daysPastDue, onPayNow, isVerified }) {
  if (!isVerified || !outstandingAmount || outstandingAmount === undefined || outstandingAmount === null) return null;
  
  // Ensure onPayNow is available
  if (!onPayNow) return null;

  const formatAmount = (amount) => {
    const numAmount = amount && typeof amount === 'number' ? amount : 0;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(numAmount);
  };

  // Show different urgency levels based on days past due
  const getUrgencyLevel = () => {
    const days = daysPastDue || 0;
    if (days >= 60) return 'critical';
    if (days >= 30) return 'high';
    if (days >= 15) return 'medium';
    return 'low';
  };

  const urgency = getUrgencyLevel();
  const urgencyConfig = {
    critical: {
      bg: 'bg-red-50 border-red-300',
      text: 'text-red-800',
      icon: '!',
      message: 'Urgent: Payment overdue by 60+ days'
    },
    high: {
      bg: 'bg-orange-50 border-orange-300',
      text: 'text-orange-800',
      icon: '!',
      message: 'Important: Payment overdue by 30+ days'
    },
    medium: {
      bg: 'bg-yellow-50 border-yellow-300',
      text: 'text-yellow-800',
      icon: '!',
      message: 'Reminder: Payment overdue'
    },
    low: {
      bg: 'bg-blue-50 border-blue-300',
      text: 'text-blue-800',
      icon: '!',
      message: 'Payment due'
    }
  };

  const config = urgencyConfig[urgency];

  return (
    <div className={`${config.bg} border-l-4 ${config.bg.includes('red') ? 'border-red-500' : config.bg.includes('orange') ? 'border-orange-500' : config.bg.includes('yellow') ? 'border-yellow-500' : 'border-blue-500'} p-4 mb-3 rounded-r-lg`}>
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <div className={`w-6 h-6 rounded-full ${config.text.includes('red') ? 'bg-red-600' : config.text.includes('orange') ? 'bg-orange-600' : config.text.includes('yellow') ? 'bg-yellow-600' : 'bg-blue-600'} text-white text-sm font-bold flex items-center justify-center flex-shrink-0`}>
            {config.icon}
          </div>
          <div className="flex-1">
            <div className={`${config.text} font-semibold text-sm mb-1`}>
              {config.message}
            </div>
            <div className={`${config.text} text-xl font-bold`}>
              {formatAmount(outstandingAmount)}
            </div>
            {daysPastDue > 0 && (
              <div className={`${config.text} text-xs mt-1 opacity-75`}>
                {daysPastDue} days past due
              </div>
            )}
          </div>
        </div>
        <button
          onClick={onPayNow}
          className={`btn ${
            urgency === 'critical' || urgency === 'high'
              ? 'btn-danger'
              : 'btn-primary'
          }`}
        >
          PAY NOW
        </button>
      </div>
    </div>
  );
}

export default PaymentReminder;

