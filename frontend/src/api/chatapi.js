const BASE_URL = "http://localhost:8000/api";

/**
 * Start a new chat session
 * @param {string} phone - User's phone number (required)
 */
export async function startChat(phone) {
  if (!phone) {
    throw new Error("Phone number is required to start chat");
  }

  try {
    const res = await fetch(`${BASE_URL}/init`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone })
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to start session: ${text}`);
    }

    return res.json(); // returns { session_id, messages, ... }
  } catch (error) {
    // Provide more detailed error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      throw new Error("Cannot connect to server. Please make sure the backend server is running on http://localhost:8000");
    }
    throw error;
  }
}

/**
 * Send a user message to the backend and get updated state
 * @param {string} sessionId - Current chat session ID
 * @param {string} userInput - User's message
 */
export async function sendChatMessage(sessionId, userInput) {
  if (!sessionId) throw new Error("Session ID is required");
  if (!userInput) throw new Error("User input cannot be empty");

  try {
    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, user_input: userInput })
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to send message: ${text}`);
    }

    return res.json(); // returns updated state
  } catch (error) {
    // Provide more detailed error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      throw new Error("Cannot connect to server. Please make sure the backend server is running on http://localhost:8000");
    }
    throw error;
  }
}

/**
 * Submit feedback after conversation completion
 * @param {string} sessionId - Current chat session ID
 * @param {number} rating - Rating from 1 to 5
 * @param {string} feedback - Optional feedback text
 */
export async function submitFeedback(sessionId, rating, feedback = "") {
  if (!sessionId) throw new Error("Session ID is required");
  if (!rating || rating < 1 || rating > 5) {
    throw new Error("Rating must be between 1 and 5");
  }

  try {
    const res = await fetch(`${BASE_URL}/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        session_id: sessionId, 
        rating,
        feedback: feedback || null
      })
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Failed to submit feedback: ${text}`);
    }

    return res.json();
  } catch (error) {
    // Provide more detailed error messages
    if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
      throw new Error("Cannot connect to server. Please make sure the backend server is running on http://localhost:8000");
    }
    throw error;
  }
}
