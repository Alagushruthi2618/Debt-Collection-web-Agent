function StaticHeader({ customerName, outstandingAmount, daysPastDue, loanId, onPayNow, onReset }) {
  // Format amount with currency
  const formatAmount = (amount) => {
    const numAmount = amount && typeof amount === 'number' ? amount : 0;
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(numAmount);
  };

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="px-4 py-4">
        {/* Customer info row */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold text-sm">
              {customerName ? customerName.charAt(0).toUpperCase() : 'C'}
            </div>
            <div>
              <div className="text-base font-semibold text-gray-900">{customerName || "Customer"}</div>
              <div className="text-sm text-gray-500">Account {loanId || "N/A"}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {onPayNow && (
              <button
                onClick={onPayNow}
                className="btn btn-danger flex items-center gap-2"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 3h18v18H3V3zm16 16V5H5v14h14zm-8-2h2v-6h-2v6zm0-8h2V7h-2v2z" fill="currentColor"/>
                </svg>
                Abhi Pay Karein
              </button>
            )}
            <button
              onClick={() => window.open(`tel:${customerName ? '+917219559972' : '+919876543210'}`)}
              className="btn btn-secondary flex items-center gap-2"
              title="Call Support"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2H19a18.45 18.45 0 0 1-9.06-2.34 18.41 18.41 0 0 1-6.6-6.6A18.45 18.45 0 0 1 2 5V3a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v3a2 2 0 0 1-1.5 1.94l-1.89.76a15.48 15.48 0 0 0 6.59 6.59l.76-1.89A2 2 0 0 1 16 16h3a2 2 0 0 1 2 2v3z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Call
            </button>
          </div>
          {!onPayNow && onReset && (
            <button
              onClick={onReset}
              className="btn btn-secondary btn-sm"
            >
              Reset
            </button>
          )}
        </div>

        {/* Account details - Clean horizontal layout */}
        <div className="flex items-center gap-6">
          <div className="flex-1">
            <div className="text-xs text-gray-500 mb-1">Outstanding Amount</div>
            <div className="text-lg font-bold text-gray-900">{formatAmount(outstandingAmount ?? 0)}</div>
          </div>
          {daysPastDue > 0 && (
            <>
              <div className="divider-vertical"></div>
              <div>
                <div className="text-xs text-gray-500 mb-1">Days Past Due</div>
                <div className={`text-lg font-bold ${
                  (daysPastDue ?? 0) >= 30 ? 'text-red-600' : (daysPastDue ?? 0) >= 15 ? 'text-orange-600' : 'text-gray-900'
                }`}>
                  {daysPastDue} days
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default StaticHeader;
