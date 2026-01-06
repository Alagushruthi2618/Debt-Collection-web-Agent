import { useState } from "react";

function NegotiationOptions({ plans, onSelect }) {
  if (!plans?.length) return null;

  return (
    <div className="negotiation-options" style={{ marginTop: "12px" }}>
      <p><strong>Select a payment option:</strong></p>
      {plans.map((plan, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(plan.name)} // send plan name to backend
          style={{
            display: "block",
            marginBottom: "6px",
            padding: "6px 12px",
            fontSize: "14px",
          }}
        >
          {plan.name}: {plan.description}
        </button>
      ))}
    </div>
  );
}

export default NegotiationOptions;
