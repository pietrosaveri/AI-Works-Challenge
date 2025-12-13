# The Anti-Portfolio Generator

## Philosophy
In a world saturated with AI-generated perfection, the Anti-Portfolio seeks to reclaim the human element. It rejects the standard CV format—lists of job titles and generic skills—in favor of a narrative that reveals the *human imprint*: how you think, how you fail, and what makes you irreplaceable.

## Features
- **Human-Centric Analysis**: Uses a local LLM to analyze your raw documents and deep thoughts to construct a philosophical profile.
- **The Anti-CV**: Generates a LaTeX resume that focuses on Manifestos, Methodologies, and Failures rather than just achievements.
- **Renaissance Aesthetic**: A web interface designed to evoke the elegance of humanism.
- **Privacy First**: Designed to run with a Local LLM (LM Studio), keeping your data on your machine.

## Prerequisites
- Python 3.8+
- [LM Studio](https://lmstudio.ai/) running a local model (e.g., Mistral, Llama 3)
  - **Important**: Start the Local Server in LM Studio on port `1234`.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Backend Server**:
   ```bash
   python backend/main.py
   ```
   The server will start at `http://0.0.0.0:8000`.

2. **Open the Application**:
   Navigate to `http://localhost:8000` in your web browser.

3. **Create Your Anti-Portfolio**:
   - **Step 1**: Upload your existing CV (PDF), project docs, or provide links to your GitHub/Website.
   - **Step 2**: Answer the "Inquiry" questions deeply. Be honest about your failures and passions.
   - **Step 3**: The system will generate your profile and provide the LaTeX source code.

4. **Compile the CV**:
   - Copy the generated LaTeX code.
   - Paste it into [Overleaf](https://www.overleaf.com) or compile locally using `pdflatex`.

## Project Structure
- `backend/`: FastAPI server and logic.
  - `llm_service.py`: Interface with LM Studio.
  - `scraper.py`: URL and PDF processing.
  - `latex_generator.py`: Jinja2 template rendering.
- `frontend/`: Static web assets (HTML/CSS/JS).
- `templates/`: LaTeX templates.

## The Challenge
This project was created as a solution to the "Anti-Portfolio" challenge, reimagining professional identity for the AI era.
