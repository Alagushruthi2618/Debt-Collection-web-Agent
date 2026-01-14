import predixionLogo from "../assets/predixion-logo.png";

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3">
      <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center mr-2 flex-shrink-0 shadow-sm">
  <img
    src={predixionLogo}
    alt="Predixion"
    className="w-5 h-5 object-contain"
  />
</div>

      <div className="flex flex-col items-start max-w-[75%]">
        <div className="text-xs text-gray-500 mb-1 px-1">Predixion Finance Assistant</div>
        <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms', animationDuration: '1.4s' }}></div>
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms', animationDuration: '1.4s' }}></div>
            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms', animationDuration: '1.4s' }}></div>
          </div>
        </div>
        <div className="text-xs text-gray-400 mt-1 px-1">
          {new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
          })}
        </div>
      </div>
    </div>
  );
}

export default TypingIndicator;

