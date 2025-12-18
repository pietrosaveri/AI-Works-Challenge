# Why is /portfolio/ Empty?

## The Issue
When you visit `http://127.0.0.1:8000/portfolio/`, you see an empty page because the `generated_site` folder contains placeholder content. This is expected behavior!

## How It Works

### Normal Flow (User Submission)
1. User visits `http://127.0.0.1:8000/` (the main Plato site)
2. User clicks "Begin" and fills out the questionnaire
3. User submits the form
4. Backend processes the input through the multi-agent system
5. **Generated site is created** in `generated_site/dist/`
6. User is redirected to `http://127.0.0.1:8000/portfolio/` with their new site

### Current State
- The server is serving whatever is in `generated_site/dist/`
- That folder currently has placeholder/empty content
- You need to either:
  - Submit the questionnaire form, OR
  - Run a test generation using sample data

## How to Test with Sample Data

### Option 1: Run the test generation script
```bash
# Make sure you're in the project root
cd /Users/pietrosaveri/Desktop/challenge2

# Activate virtual environment
source .venv/bin/activate

# Run the test generation
python test_generation.py
```

This will:
- Load sample data from `submission_sites/person1_linus.json`
- Run all agents (Art Director, Content Strategist, UX Architect, etc.)
- Generate a complete portfolio site
- Save it to `generated_site/dist/`

### Option 2: Submit the form manually
1. Make sure backend server is running:
   ```bash
   cd /Users/pietrosaveri/Desktop/challenge2
   source .venv/bin/activate
   cd backend
   uvicorn main:app --reload
   ```

2. Open `http://127.0.0.1:8000/` in your browser
3. Click "Begin"
4. Fill out the questionnaire
5. Submit
6. Wait for generation (takes ~30-60 seconds)
7. View your generated site at `/portfolio/`

## Verify It's Working
After generating a site, check:
```bash
# Should show real content (not "Analysis in progress")
cat generated_site/dist/data/site_data.json | head -50

# Should have a user name (not empty string)
grep "user_name" generated_site/dist/data/site_data.json
```

## Architecture Note
- `/` (root) → Serves the **frontend** folder (Plato main site)
- `/portfolio/` → Serves **generated_site/dist/** (dynamically generated portfolio)

The frontend is static and always available. The generated site is dynamic and created on-demand when users submit the questionnaire.
