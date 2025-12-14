# Anti-Portfolio Generator Framework

## System Overview

The Anti-Portfolio Generator is a sophisticated multi-agent AI system that creates deeply personalized portfolio websites by analyzing user responses and external data sources. Unlike traditional portfolios that showcase achievements, this system focuses on authentic self-reflection, failures, and behavioral patterns.

## Architecture

### Core Components

1. **Backend (FastAPI)**
   - REST API endpoints for file uploads and profile analysis
   - Multi-agent orchestration system
   - Dynamic website generation
   - Static file serving

2. **Frontend (React + Vite)**
   - Interactive questionnaire interface
   - File upload and URL input management
   - Real-time preview and navigation
   - Success/loading screen states

3. **Multi-Agent System**
   - 7 specialized AI agents working in concert
   - Each agent has a specific domain of expertise
   - Feedback loops ensure quality output

## Multi-Agent System

### Agent Pipeline

```
User Input → Scraper → Content Strategist → Mood Agent
                            ↓
                    UX Architect → Icon Curator
                            ↓
                    React Developer → Orchestrator
                            ↓
                    Site Generator → Validation
```

### Agent Descriptions

#### 1. Mood Agent
- **Role:** Design system architect
- **Input:** Color, animal, abstract word from user
- **Output:** Complete design system (colors, fonts, layout style)
- **Method:** Deterministic selection from curated palettes
- **Example Styles:** Swiss Brutalist, Luxury Fashion, Dark Academia

#### 2. Content Strategist Agent (Central)
- **Role:** Content architect and narrative designer
- **Input:** Raw text from scraped data + questionnaire answers
- **Output:** Structured content for all pages (home, behavioral patterns, anti-claims, failures, decision architecture, proprietary method, about)
- **Key Innovation:** Extracts behavioral patterns and anti-claims from user responses
- **Validation:** Pydantic models ensure proper JSON structure

#### 3. UX Architect Agent
- **Role:** Information architecture and navigation designer
- **Input:** Design system + content strategy
- **Output:** Page structure, navigation hierarchy, section organization
- **Considerations:** User's personality influences layout choices

#### 4. Icon Curator Agent
- **Role:** Visual metaphor designer
- **Input:** Design system + content + UX plan
- **Output:** Icon library choice (Lucide, Heroicons, etc.) + specific icon suggestions for each section
- **Philosophy:** Icons must align with color palette and abstract concept

#### 5. React Developer Agent
- **Role:** Frontend code generator
- **Input:** All previous agent outputs
- **Output:** Complete single-page React application (embedded in HTML)
- **Technology Stack:** React 18, Tailwind CSS, Framer Motion, Lucide icons
- **Features:** Smooth animations, responsive design, dynamic routing

#### 6. Orchestrator Agent
- **Role:** Quality assurance and coordinator
- **Input:** All agent outputs + generated code
- **Output:** Validation report + regeneration instructions if needed
- **Feedback Loop:** Can trigger up to 2 regeneration cycles
- **Criteria:** Content completeness, design consistency, navigation logic

#### 7. Selenium Validator Agent (Optional)
- **Role:** Automated testing
- **Status:** Currently disabled per request
- **Function:** Validates links, checks for console errors, tests page navigation

## Data Flow

### 1. Input Processing
```python
Raw Inputs:
- Uploaded files (PDFs, documents, images)
- URLs (personal sites, GitHub, LinkedIn)
- Text input (additional notes)
- Questionnaire answers (8 questions)
- Vibe indicators (color, animal, abstract word)
```

### 2. Scraping & Extraction
```python
process_inputs(files, urls) → raw_text
- PDF extraction (PyPDF2)
- Web scraping (requests + BeautifulSoup)
- Image storage for layout integration
```

### 3. Multi-Agent Orchestration
```python
# Sequential processing with feedback loops
mood_system = mood_agent(vibe)
content_strategy = content_strategist_agent(raw_text, answers)
ux_plan = ux_architect_agent(mood_system, content_strategy, name, images)
icon_strategy = icon_curator_agent(mood_system, content_strategy, ux_plan, name)
react_code = react_developer_agent(mood, content, ux, name, images, icon_strategy)
orchestrator = orchestrator_agent(mood, content, ux, react_code, name, images)

# Feedback loop
while orchestrator.needs_regeneration and retries < 2:
    react_code = react_developer_agent(..., orchestrator_feedback=instructions)
    orchestrator = orchestrator_agent(...)
    retries += 1
```

### 4. Site Generation
```python
generate_dynamic_website(react_code, user_name, image_paths)
- Writes to generated_site/dist/index.html
- Copies image assets to assets/ folder
- Creates self-contained HTML with embedded React
```

## Page Structure

### Generated Site Pages

1. **Home**
   - Thesis statement
   - Personal introduction
   - Navigation prompt

2. **Behavioral Patterns**
   - Recurring mental habits
   - Evidence quotes from user input
   - Pattern analysis

3. **Anti-Claims**
   - Things user is NOT (debunking assumptions)
   - Evidence and explanations
   - Authentic positioning

4. **Failures & Lessons**
   - Biggest mistakes
   - Lessons learned
   - Growth narrative

5. **Decision Architecture**
   - How user makes important decisions
   - Key criteria and frameworks
   - Values-based decision making

6. **Proprietary Method**
   - Unique approach to work
   - Signature techniques
   - What makes user different

7. **About**
   - Extended bio
   - Current focus
   - Contact information

## Technology Stack

### Backend
- **Framework:** FastAPI
- **LLM:** OpenAI GPT-4
- **LangChain:** Agent orchestration and prompt management
- **Scraping:** BeautifulSoup4, requests, PyPDF2
- **Validation:** Pydantic models

### Frontend (Questionnaire)
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** Custom CSS (gradient backgrounds, glass morphism)
- **State Management:** React hooks

### Generated Sites
- **Runtime:** React 18 (CDN)
- **Styling:** Tailwind CSS (CDN)
- **Animation:** Framer Motion
- **Icons:** Lucide
- **Fonts:** Google Fonts (dynamically loaded)

## Key Design Principles

### 1. Authenticity Over Perfection
- Emphasizes mistakes and lessons learned
- Values vulnerability and honesty
- Anti-claims prevent misrepresentation

### 2. Personality-Driven Design
- Color palette derived from user's favorite color
- Animal metaphor influences icon choices
- Abstract word shapes layout philosophy

### 3. Content-First Approach
- Design follows content strategy
- UX adapts to narrative structure
- No template reuse—each site is unique

### 4. Multi-Agent Collaboration
- Specialized expertise per domain
- Feedback loops ensure quality
- Orchestrator prevents premature deployment

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here
```

### Agent Parameters
- **Temperature:** Varies by agent (0.3-0.8)
- **Max Tokens:** 4000-8000 depending on complexity
- **Retry Logic:** Up to 3 attempts with temperature adjustment
- **Validation:** Pydantic models with strict JSON parsing

## Deployment

### Local Development
```bash
# Backend
cd backend
python main.py  # Runs on http://localhost:8000

# Frontend (development mode)
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173
```

### Production Build
```bash
cd frontend
npm run build  # Outputs to frontend/dist
# Backend serves both frontend and generated sites
```

## Submission Structure

```
submission_sites/
├── README.md                 # Overview for judges
├── person1_linus.json        # Maya Rodriguez profile data
├── person1_linus/            # Maya's generated site
│   ├── index.html
│   └── assets/
├── person2_steve.json        # James Chen profile data
├── person2_steve/            # James's generated site
│   ├── index.html
│   └── assets/
├── person3_douglas.json      # Sofia Andersson profile data
└── person3_douglas/          # Sofia's generated site
    ├── index.html
    └── assets/
```

## Quality Assurance

### Validation Layers
1. **Content Validation:** Pydantic models ensure complete JSON structure
2. **Code Validation:** HTML structure checks, React syntax validation
3. **Orchestrator Review:** Holistic quality assessment before deployment
4. **Feedback Loops:** Automatic regeneration if critical issues detected

### Error Handling
- Scraping failures fall back to user text input
- Missing content triggers agent retry with temperature adjustment
- Malformed JSON gets post-processed with regex fixes
- Icon injection uses safe string replacement

## Extensibility

### Adding New Agents
1. Create new function in `llm_service.py`
2. Define Pydantic model for output structure
3. Write system prompt with clear output format
4. Integrate into orchestration pipeline
5. Update orchestrator to validate new agent output

### Adding New Pages
1. Update Content Strategist prompt to include new page
2. Modify Pydantic ContentStrategy model
3. Update UX Architect to handle new navigation item
4. Ensure React Developer includes page in routing

### Custom Design Styles
1. Add new palette to Mood Agent's PALETTES array
2. Add new font combination to FONTS array
3. Update layout style descriptions
4. Test deterministic selection logic

## Performance Considerations

- **Agent Calls:** Sequential (10-15 seconds per site)
- **LLM Costs:** ~$0.20-0.50 per site generation
- **Caching:** None (each generation is unique)
- **Optimization:** Retry logic minimizes failed generations

## Known Limitations

1. Wikipedia scraping blocked by 403 errors (solved by using empty URLs)
2. Selenium validation disabled (can be re-enabled)
3. Image processing basic (no AI vision integration yet)
4. Single-language support (English only)

## Future Enhancements

- AI vision for image analysis and integration
- Multi-language support
- PDF export of generated sites
- Analytics dashboard for site performance
- Custom domain deployment automation
- More design style variations
- Interactive elements (contact forms, etc.)

---

**Version:** 1.0  
**Last Updated:** December 14, 2025  
**License:** Proprietary
