# Quick Start Guide

This project has **three ways** to run it:

1. **CLI Mode** - Interactive terminal-based testing
2. **Web App** - Full-stack web application (Backend + Frontend)
3. **API Only** - Just the backend API server

---

## Prerequisites

- Python 3.8+ installed
- Node.js and npm installed (for web app)
- Google Gemini API key

---

## Step 1: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: LangSmith (for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=debt-collection-agent
```

**Note**: At minimum, you need `GOOGLE_API_KEY` to run the agent.

---

## Option A: Run CLI Mode (Simplest)

For quick testing in the terminal:

```bash
python main.py
```

Then follow the prompts:
- Enter a phone number (e.g., `+919876543210`)
- Type your responses to the agent

**Available test customers:**
- `+919876543210` - Rajesh Kumar (DOB: 15-03-1985)
- `+919876543211` - Priya Sharma (DOB: 22-07-1990)
- `+919876543212` - Amit Patel (DOB: 05-11-1988)

---

## Option B: Run Web Application (Full Stack)

### 1. Start the Backend Server

**Terminal 1 - Backend:**

```bash
# From project root directory
python backend/app.py
```

Or using uvicorn directly:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

The backend will run on `http://localhost:8000`

**Verify it's working:**
```bash
curl http://localhost:8000/health
```

### 2. Start the Frontend

**Terminal 2 - Frontend:**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will run on `http://localhost:5173` (or another port if 5173 is busy)

### 3. Open in Browser

Open `http://localhost:5173` in your browser to use the web interface.

---

## Option C: Run Backend API Only

If you just want to test the API:

```bash
# Start backend
python backend/app.py
```

Then test with curl or the test script:

```bash
# Test script
python backend/test_api.py

# Or manually with curl
curl -X POST http://localhost:8000/api/init \
  -H "Content-Type: application/json" \
  -d '{"phone": "+919876543210"}'
```

---

## Troubleshooting

### Backend Issues

**Import errors?**
- Make sure you're running from the project root directory
- Activate your virtual environment
- Check dependencies: `pip install -r requirements.txt`

**API key errors?**
- Verify `.env` file exists in project root
- Check that `GOOGLE_API_KEY` is set correctly
- Restart the server after creating/updating `.env`

**Port already in use?**
- Change port: `uvicorn backend.app:app --port 8001`
- Update frontend `chatapi.js` to use new port

### Frontend Issues

**npm install fails?**
- Make sure Node.js is installed: `node --version`
- Try deleting `node_modules` and `package-lock.json`, then run `npm install` again

**Can't connect to backend?**
- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify `BASE_URL` in `frontend/src/api/chatapi.js` matches your backend URL

**Frontend shows errors?**
- Check browser console (F12) for errors
- Verify backend is running and accessible

---

## Project Structure

```
Debt-Collection-web-Agent/
├── backend/          # FastAPI backend server
│   ├── app.py       # Main FastAPI app
│   └── routes/      # API endpoints
├── frontend/        # React + Vite frontend
│   └── src/         # React components
├── src/             # Core LangGraph agent logic
├── main.py          # CLI testing tool
└── requirements.txt # Python dependencies
```

---

## Next Steps

- **API Documentation**: Visit `http://localhost:8000/docs` when backend is running
- **Test Customers**: Use the phone numbers listed above for testing
- **Read More**: Check `README.md` for detailed architecture and features


