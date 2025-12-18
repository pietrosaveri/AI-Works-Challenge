<img width="3650" height="2116" alt="Screenshot 2025-12-14 at 16 10 45" src="https://github.com/user-attachments/assets/abac3b41-7339-41b5-9ffa-6a023009608c" />

# Plato: The Anti-Portfolio Generator

## Mission
**We exist to make humans irreplaceable.**

In an era where AI can write perfect resumes and polish every rough edge, we believe the most dangerous thing you can do is look like everyone else. The traditional portfolio—lists of job titles, skills, and polished achievements—has become a commodity. When AI can generate these at scale, the only thing that matters is what *cannot* be replicated: your unique professional fingerprint.

Plato doesn't create portfolios. It creates **interpretations**.

## Philosophy

### The Problem We're Solving
- **AI has made perfection cheap**: Anyone can generate an optimized CV in seconds.
- **Humans are becoming duplicates**: We're all starting to sound like low-temperature language models—standardized, risk-averse, predictable.
- **Representation vs. Interpretation**: A resume *represents* what you did. Plato *interprets* how you think.

### Our Core Beliefs
1. **The Portfolio is Dead**: Job titles, timelines, and skills lists are historical artifacts designed for a pre-AI world.
2. **Process Over Output**: A successful project can hide poor thinking. A failed project can reveal exceptional judgment.
3. **Anti-Standardization**: Most tools try to standardize uniqueness. We do the opposite.
4. **AI to Reveal Humanity**: We use AI not to enhance a CV, but as an analytical instrument to detect behavioral patterns, contradictions, and decision-making styles.

### Example of generated Sites
![WhatsApp Image 2025-12-13 at 23 57 06](https://github.com/user-attachments/assets/7ed2c062-9801-491a-88a0-ec82034d1da7)
<img width="1512" height="897" alt="Screenshot 2025-12-14 at 00 30 01" src="https://github.com/user-attachments/assets/69e2a6bf-7fc5-4ecb-83c9-6dbc8ef5db06" />

## How We Do It: The Multi-Agent System

Plato employs a **council of specialized AI agents**, each analyzing different dimensions of your professional identity. This isn't a single algorithm—it's a dialogue between analytical perspectives.

### The Agent Pipeline

1. **Mood Agent** 🎨
   - Translates your personality into a visual language
   - Determines colors, typography, spacing, and aesthetic mood
   - Creates a design system that *feels* like you

2. **Content Strategist Agent** 📝 (Central Orchestrator)
   - Reads between the lines of your history
   - Extracts behavioral patterns, not just accomplishments
   - Identifies your professional fingerprint: how you enter problems, make trade-offs, and learn from failures
   - Structures your narrative arc

3. **UX Architect Agent** 🏗️
   - Designs the information architecture
   - Determines navigation structure and page hierarchy
   - Ensures the site is intuitive yet unconventional

4. **Icon Curator Agent** 🎯
   - Selects symbolic representations for concepts
   - Ensures visual consistency with the mood system

5. **React Developer Agent** ⚛️
   - Generates the complete React website code
   - Implements sophisticated animations and interactions
   - Follows the design system precisely

6. **Orchestrator Agent** 🎭
   - Acts as the quality controller
   - Reviews the generated site for coherence, alignment, and quality
   - Requests regenerations if standards aren't met

7. **Selenium Validator Agent** ✅ (Optional)
   - Tests the generated site for technical issues
   - Validates navigation, responsiveness, and functionality

### The Result
A **fully functional, animated React website** that captures not what you've done, but how you think. Each site is structurally similar enough to be readable, but conceptually different enough to be unmistakably personal.

## Prerequisites

### Required Software
- **Python 3.8+**
- **Node.js 16+** and npm (for the frontend)
- **LLM Provider** (choose one):
  - **[LM Studio](https://lmstudio.ai/)** - Local LLM inference server (free, runs offline)
  - **[Google AI Studio](https://aistudio.google.com/)** - Gemini API (requires API key)

### LLM Options

#### Option 1: Local LLM with LM Studio (Recommended for Privacy)
**Recommended Model**: **Qwen 2.5 32B Instruct** or **GPT-OSS 20B**
- High reasoning capability for content analysis
- Strong instruction-following for structured outputs
- Good context window (8k+ tokens recommended)

**Alternative Models**:
- Mistral 7B+ (faster, but less nuanced analysis)
- Llama 3.1 8B+ (good balance of speed and quality)
- Any OpenAI-compatible model with 8B+ parameters

#### Option 2: Gemini API via Google AI Studio
- **Recommended Model**: `gemini-1.5-pro` (default)
- **Alternative**: `gemini-1.5-flash` (faster, cheaper)
- Get your API key from: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- No local installation required
- Pay-per-use pricing

## Installation

### 1. Configure Your LLM Provider

#### Option A: Using LM Studio (Local)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download a recommended model:
   - Search for "Qwen 2.5 32B Instruct" or "GPT-OSS 20B"
   - Download the GGUF format (Q4_K_M or Q5_K_M for good performance)
3. Start the **Local Server**:
   - Go to the "Local Server" tab in LM Studio
   - Load your chosen model
   - Click "Start Server"
   - Ensure it's running on `http://localhost:1234`

#### Option B: Using Gemini API

1. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and configure:
   ```env
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your-actual-api-key-here
   GEMINI_MODEL=gemini-1.5-pro
   ```

### 2. Install Backend Dependencies

```bash
# Clone the repository
cd challenge2
Configuration

The application uses a `.env` file for configuration. Copy `.env.example` to `.env` and adjust settings:

```env
# Choose your LLM provider: "local" or "gemini"
LLM_PROVIDER=local

# Local LLM Settings (if using LM Studio)
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=local-model

# Gemini API Settings (if using Google AI Studio)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro

# LLM Parameters (applies to both providers)
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=32000
```

**Configuration Options:**
- `LLM_PROVIDER`: Set to `local` for LM Studio or `gemini` for Google AI Studio
- `LLM_TEMPERATURE`: Lower values (0.1-0.3) for more consistent outputs
- `LLM_MAX_TOKENS`: Maximum response length (32000 recommended)

## Usage

### 1. Start Your LLM Provider
- **If using LM Studio**: Ensure LM Studio is running with your model loaded on port `1234`
- **If using Gemini**: Your API key in `.env` is all you need

# Install dependencies
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Usage

### 1. Start LM Studio Server
Ensure LM Studio is running with your model loaded on port `1234`.

### 2. Start the Backend Server

```bash
# From the project root
python backend/main.py
```

The backend API will start at `http://127.0.0.1:8000`.

### 3. Start the Frontend Development Server

```bash
# In a new terminal, from the frontend directory
cd frontend
npm run dev
```LM Connection Issues

#### Local LLM (LM Studio)
- Ensure LM Studio is running and the server is started
- Check that the port is `1234` (default)
- Verify the model is loaded in LM Studio
- Check `.env` has `LLM_PROVIDER=local`

#### Gemini API
- Verify your API key is correct in `.env`
- Check you have API credits/quota available
- Ensure `.env` has `LLM_PROVIDER=gemini`
- Visit [Google AI Studio](https://aistudio.google.com/) to check API status
### 4. Create Your Anti-Portfolio

1. **Navigate to** `http://localhost:5173`
2. **Answer the Questions**:
   - Upload your CV, slides, or any documents
   - Provide GitHub, LinkedIn, or personal site URLs (optional)
   - Share your hobbies, passions, failures, and what you love about your work
   - Tell us who you really are, beyond the job title
   - Choose your favorite color, an animal that describes you, and an abstract word
3. **Watch the Agents Work**:
   - The loading screen shows which agent is currently processing
   - Famous design quotes keep you company during generation
4. **View Your Site**:
   - Once complete, you'll see a success screen
   - Click "View Your Site" to see your generated portfolio
   - Your site is available at `http://127.0.0.1:8000/portfolio/`

## Project Structure

```
challenge2/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── llm_service.py       # Multi-agent system + LM Studio interface
│   ├── scraper.py           # URL and PDF processing
│   └── site_generator.py    # React site generation
├── frontend/               # React application (Vite)
│   ├── src/
│   │   ├── components/     # Navigation, LoadingScreen, SuccessScreen
│   │   ├── pages/          # Landing, Philosophy, About, Questionnaire
│   │   └── styles/         # Global CSS with BrotherSignature font
│   └── package.json
├── generated_site/         # Output directory for portfolio sites
├── uploads/                # Temporary storage for uploaded files
└── README.md
```

## Troubleshooting

### LM Studio Connection Issues
- Ensure LM Studio is running and the server is started
- Check that the port is `1234` (default)
- Verify the model is loaded in LM Studio

### Frontend Not Connecting to Backend
- Ensure backend is running on port `8000`
- Check browser console for CORS errors
- Verify both servers are running simultaneously

### Generated Site is Blank
- Check backend console for errors during generation
- Ensure the LLM generated valid content (look for "CONTENT_DATA" in logs)
- Try regenerating with a more powerful model
