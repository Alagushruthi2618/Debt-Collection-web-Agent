# GitHub Push Guide - What Files to Commit

This guide explains what files you should push to GitHub and what you should **NOT** push.

---

## ✅ **Files You SHOULD Push**

### **1. Source Code Files**

#### Backend (Python)
- ✅ `backend/app.py` - FastAPI application
- ✅ `backend/routes/chat.py` - API routes
- ✅ `backend/session_store.py` - Session management
- ✅ `backend/__init__.py` - Package init
- ✅ `backend/routes/__init__.py` - Package init
- ✅ `backend/test_api.py` - API test script (useful for others)
- ✅ `backend/README.md` - Backend documentation
- ✅ `backend/QUICKSTART.md` - Backend quick start guide

#### Core Agent Logic
- ✅ `src/` directory (all Python files)
  - `src/graph.py` - LangGraph flow
  - `src/state.py` - State management
  - `src/data.py` - Mock customer data
  - `src/utils/llm.py` - Gemini integration
  - `src/nodes/` - All node files (greeting, verification, etc.)
  - `src/__init__.py` - Package init files

#### Frontend (React)
- ✅ `frontend/src/` - All source files
  - `frontend/src/App.jsx`
  - `frontend/src/main.jsx`
  - `frontend/src/components/` - All components
  - `frontend/src/api/` - API client
  - `frontend/src/styles.css` - Styles
- ✅ `frontend/index.html` - HTML entry point
- ✅ `frontend/vite.config.js` - Vite configuration
- ✅ `frontend/eslint.config.js` - ESLint configuration
- ✅ `frontend/package.json` - Dependencies
- ✅ `frontend/package-lock.json` - Lock file (important!)
- ✅ `frontend/README.md` - Frontend documentation

### **2. Configuration Files**

- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Git ignore rules
- ✅ `frontend/.gitignore` - Frontend git ignore rules
- ✅ `frontend/robots.txt` - SEO robots file
- ✅ `frontend/_redirects` - Deployment redirects (if using Netlify/Vercel)
- ✅ `frontend/favicon.ico` - Favicon

### **3. Documentation**

- ✅ `README.md` - Main project README
- ✅ `QUICKSTART.md` - Quick start guide
- ✅ `TESTING_GUIDE.md` - Testing documentation
- ✅ `GEMINI_USAGE.md` - Gemini usage documentation
- ✅ `DESIGN.md` - Design documentation (if exists)
- ✅ `backend/README.md` - Backend docs
- ✅ `backend/QUICKSTART.md` - Backend quick start

### **4. Test & Script Files**

- ✅ `tests/test_scenarios.py` - Test scenarios
- ✅ `experiments/langsmith_eval.py` - Evaluation script
- ✅ `scripts/create_langsmith_dataset.py` - Dataset creation script
- ✅ `main.py` - CLI mode entry point

### **5. Static Assets (if small)**

- ⚠️ `frontend/lovable-uploads/` - **Optional:** Only for social media meta tags (og:image, twitter:image) - not used in chat UI
- ✅ `frontend/public/vite.svg` - Vite logo (if used)
- ✅ `frontend/src/assets/react.svg` - React logo (if used)

### **6. Optional Deployment/SEO Files**

These are **optional** and don't affect chat functionality:

- ⚠️ `frontend/favicon.ico` - Browser tab icon (optional, browsers auto-detect from root)
- ⚠️ `frontend/_redirects` - **Only if deploying to Netlify** (for SPA routing)
- ⚠️ `frontend/robots.txt` - **Only if you want SEO/search engine indexing**

**Note:** You can skip these if you don't need SEO or specific deployment features.

---

## ❌ **Files You SHOULD NOT Push**

### **1. Environment & Secrets**

- ❌ `.env` - **NEVER commit this!** Contains API keys
- ❌ `.env.local` - Local environment variables
- ❌ `.env.production` - Production secrets
- ❌ Any file containing `GEMINI_API_KEY` or other secrets

### **2. Build Artifacts**

- ❌ `frontend/dist/` - Production build output
- ❌ `frontend/build/` - Build output
- ❌ `frontend/assets/index-*.js` - Generated bundle files
- ❌ `frontend/assets/index-*.css` - Generated CSS files
- ❌ `*.pyc` - Python bytecode
- ❌ `__pycache__/` - Python cache directories

### **3. Dependencies**

- ❌ `node_modules/` - Node.js dependencies (install via `npm install`)
- ❌ `.venv/` or `venv/` - Python virtual environments
- ❌ `*.egg-info/` - Python package metadata

### **4. IDE & Editor Files**

- ❌ `.vscode/` - VS Code settings (unless team-specific)
- ❌ `.idea/` - IntelliJ/PyCharm settings
- ❌ `*.swp` - Vim swap files
- ❌ `*.swo` - Vim swap files
- ❌ `.DS_Store` - macOS system files
- ❌ `Thumbs.db` - Windows system files

### **5. Logs & Temporary Files**

- ❌ `*.log` - Log files
- ❌ `*.tmp` - Temporary files
- ❌ `.pytest_cache/` - Test cache
- ❌ `.coverage` - Coverage reports

---

## 📋 **Current Status Check**

Based on your current git status, here's what you should commit:

### **Modified Files (Should Commit)**
```bash
git add backend/app.py
git add backend/routes/chat.py
git add frontend/eslint.config.js
git add frontend/index.html
git add frontend/package-lock.json
git add frontend/src/App.css
git add frontend/src/App.jsx
git add frontend/src/assets/react.svg
git add frontend/src/components/chatwindow.jsx
git add frontend/src/components/messagebubble.jsx
git add frontend/src/components/negotiationsoption.jsx
git add frontend/src/components/statusbanner.jsx
git add frontend/src/components/userinput.jsx
git add frontend/src/index.css
git add frontend/src/styles.css
git add src/graph.py
git add src/nodes/greeting.py
```

### **New Files (Should Commit)**
```bash
git add GEMINI_USAGE.md
git add QUICKSTART.md
git add TESTING_GUIDE.md

# Optional: Only if you need SEO/deployment features
# git add frontend/_redirects      # Only for Netlify deployment
# git add frontend/favicon.ico      # Optional browser icon
# git add frontend/lovable-uploads/ # Only for social media previews
# git add frontend/robots.txt       # Only for SEO
```

---

## 🚀 **Quick Commit Command**

Run these commands to commit everything that should be pushed:

```bash
# Add all modified and new files
git add backend/
git add frontend/src/
git add frontend/index.html
git add frontend/vite.config.js
git add frontend/eslint.config.js
git add frontend/package.json
git add frontend/package-lock.json
# Optional deployment/SEO files (skip if not needed):
# git add frontend/_redirects      # Only for Netlify
# git add frontend/favicon.ico     # Optional
# git add frontend/lovable-uploads/ # Only for social previews
# git add frontend/robots.txt      # Only for SEO
git add src/
git add tests/
git add experiments/
git add scripts/
git add main.py
git add requirements.txt
git add README.md
git add QUICKSTART.md
git add TESTING_GUIDE.md
git add GEMINI_USAGE.md

# Commit
git commit -m "Update application: improved UI, fixed greeting denial handling, added documentation"

# Push
git push origin main
```

---

## ⚠️ **Before Pushing - Double Check**

1. **Verify .env is NOT tracked:**
   ```bash
   git ls-files | grep .env
   ```
   Should return nothing!

2. **Verify node_modules is NOT tracked:**
   ```bash
   git ls-files | grep node_modules
   ```
   Should return nothing!

3. **Verify __pycache__ is NOT tracked:**
   ```bash
   git ls-files | grep __pycache__
   ```
   Should return nothing!

4. **Check for API keys:**
   ```bash
   git grep -i "GEMINI_API_KEY" -- "*.py" "*.js" "*.jsx"
   ```
   Should only show code that reads from environment variables, not actual keys!

---

## 📝 **Recommended .gitignore Additions**

Make sure your `.gitignore` includes:

```gitignore
# Environment variables
.env
.env.local
.env.*.local

# Build outputs
frontend/dist/
frontend/build/
frontend/assets/index-*.js
frontend/assets/index-*.css

# Dependencies
node_modules/
.venv/
venv/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

---

## ✅ **Summary**

**Push:**
- ✅ All source code
- ✅ Configuration files
- ✅ Documentation
- ✅ Package files (package.json, requirements.txt)
- ✅ Static assets (images, etc.)

**Don't Push:**
- ❌ `.env` files
- ❌ `node_modules/`
- ❌ `__pycache__/`
- ❌ Build artifacts (`dist/`, `build/`)
- ❌ Virtual environments
- ❌ IDE settings
- ❌ Log files

