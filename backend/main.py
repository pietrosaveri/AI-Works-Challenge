from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import shutil
import os
import json
from pydantic import BaseModel
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to sys.path to allow imports from backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_service import (
    # analyze_profile,  # Legacy function - removed during refactoring
    mood_agent,
    content_strategist_agent,
    ux_architect_agent,
    icon_curator_agent,
    react_developer_agent,
    orchestrator_agent,
    # selenium_validator_agent,  # Legacy function - removed during refactoring
    Workspace,
)
from backend.scraper import process_inputs
from backend.site_generator import generate_dynamic_website

def save_frontend_data(data: dict):
    """Saves the aggregated site data to the frontend source folder."""
    frontend_data_dir = os.path.join("frontend", "src", "data")
    try:
        os.makedirs(frontend_data_dir, exist_ok=True)
        file_path = os.path.join(frontend_data_dir, "site_data.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Frontend data saved to: {file_path}")
    except Exception as e:
        print(f"❌ Failed to save frontend data: {e}")

app = FastAPI(title="Anti-Portfolio Generator")

# No longer mounting generated_site as it's now a standalone Node.js project

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class AnalysisRequest(BaseModel):
    urls: List[str]
    text_input: str
    answers: dict

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(file_path)
    return {"message": "Files uploaded successfully", "files": saved_files}

@app.post("/api/analyze")
async def analyze_profile_endpoint(
    urls: str = Form("[]"),
    text_input: str = Form(""),
    answers: str = Form("{}"),
    vibe: str = Form("{}"),
    files: List[UploadFile] = File(None)
):
    # Save files and separate images from documents
    saved_file_paths = []
    image_paths = []
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
    
    if files:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Check if it's an image
            if file.filename.lower().endswith(image_extensions):
                image_paths.append(file_path)
            else:
                saved_file_paths.append(file_path)
    
    # Parse JSON inputs
    try:
        urls_list = json.loads(urls)
        answers_dict = json.loads(answers)
        vibe_dict = json.loads(vibe)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form data")

    # Process inputs
    raw_text = process_inputs(saved_file_paths, urls_list)
    
    # Append text input
    raw_text += f"\n\n--- User Additional Notes ---\n{text_input}"

    # ============================================================================
    # MULTI-AGENT ORCHESTRATION
    # ============================================================================
    
    print("\n=== ART DIRECTOR AGENT (DESIGN DNA) ===")
    # Import here to avoid circular imports if placed at top
    from backend.llm_service import art_director_agent
    design_dna = art_director_agent(raw_text, answers_dict, vibe_dict)
    print(f"Design DNA Generated:")
    print(f"  - Layout: {design_dna.get('layout')}")
    print(f"  - Motion: {design_dna.get('motion')}")
    print(f"  - Theme: {design_dna.get('theme')}")
    print(f"  - Archetype: {design_dna.get('archetype')}")
    print(f"  - Color Palette: {design_dna.get('color_palette')}")
    print(f"  - Typography: {design_dna.get('typography_pair')}")
    
    # Design DNA replaces the Mood Agent - it contains all design system info
    mood_system = {
        'colors': {
            'primary': design_dna['color_palette'][0],
            'secondary': design_dna['color_palette'][1],
            'accent': design_dna['color_palette'][3],
            'background': design_dna['color_palette'][0],
            'text': design_dna['color_palette'][4]
        },
        'typography': design_dna.get('typography_pair'),
        'layout_style': design_dna.get('layout'),
        'theme': design_dna.get('theme')
    }
    
    print("\n=== CONTENT STRATEGIST AGENT (CENTRAL) ===")
    content_strategy = content_strategist_agent(raw_text, answers_dict)
    pages = content_strategy.get('pages', {})
    home_data = pages.get('home', {}) or {}
    patterns_data = pages.get('behavioral_patterns') or {}
    anticlaims_data = pages.get('anti_claims') or {}
    print(f"Thesis: {home_data.get('thesis', 'Unknown')[:80]}...")
    print(f"Behavioral Patterns: {len(patterns_data.get('patterns', []))}")
    print(f"Anti-Claims: {len(anticlaims_data.get('anti_claims', []))}")
    
    print("\n=== UX ARCHITECT AGENT ===")
    user_name = answers_dict.get('who_are_you', 'Professional')[:50]
    ux_plan = ux_architect_agent(design_dna, content_strategy, user_name, image_paths)
    nav_structure = (ux_plan.get('navigation') or {}).get('structure', [])
    print(f"UX Plan Navigation: {nav_structure}")
    print(f"UX Plan Pages: {len(ux_plan.get('pages', []))}")
    
    print("\n=== ICON CURATOR AGENT ===")
    icon_strategy = icon_curator_agent(design_dna, content_strategy, ux_plan, user_name)
    print(f"Icon Library: {icon_strategy.get('icon_library', 'Unknown')}")
    print(f"Icon Suggestions: {len(icon_strategy.get('suggestions', []))} icons")
    print(f"Usage Philosophy: {icon_strategy.get('usage_philosophy', 'N/A')[:80]}")
    
    print("\n=== REACT DEVELOPER AGENT ===")
    react_code = react_developer_agent(
        design_dna,
        content_strategy, 
        ux_plan, 
        user_name, 
        image_paths, 
        icon_strategy=icon_strategy
    )
    print(f"Generated React Code: {len(react_code)} characters")

    # Build collaborative workspace and let orchestrator drive incremental fixes
    workspace = Workspace(
        design_dna=design_dna,
        content_strategy=content_strategy,
        ux_plan=ux_plan,
        icon_plan=icon_strategy,
        react_code=react_code,
        action_log=["v0: initial generation"]
    )

    print("\n=== ORCHESTRATOR AGENT (COLLAB) ===")
    orchestrator = orchestrator_agent(
        design_dna=workspace.design_dna,
        content_strategy=workspace.content_strategy,
        ux_plan=workspace.ux_plan,
        react_code=workspace.react_code,
        user_name=user_name,
        image_paths=image_paths
    )
    print(f"Orchestrator Summary: {orchestrator.get('summary', 'No summary')}"[:160])
    if orchestrator.get('needs_regeneration'):
        print("⚠️  Issues remain after orchestrator attempts")
    else:
        print("✅ Orchestrator approved - workspace clean")

    # Update locals from workspace after orchestration
    content_strategy = workspace.content_strategy
    ux_plan = workspace.ux_plan
    icon_strategy = workspace.icon_plan
    react_code = workspace.react_code
    
    # ============================================================================
    # SAVE DATA FOR FRONTEND (Complex Site Generation)
    # ============================================================================
    site_data = {
        "user_name": user_name,
        "design_dna": design_dna,
        "content_strategy": content_strategy,
        "ux_plan": ux_plan,
        "icon_strategy": icon_strategy,
        "mood_system": mood_system
    }
    
    # DISABLED: User requested frontend to be clean. Data is now saved to generated_site/dist/data/site_data.json
    # frontend_data_path = os.path.join("frontend", "src", "data", "site_data.json")
    # try:
    #     os.makedirs(os.path.dirname(frontend_data_path), exist_ok=True)
    #     with open(frontend_data_path, "w") as f:
    #         json.dump(site_data, f, indent=2)
    #     print(f"✅ Frontend data injected at: {frontend_data_path}")
    # except Exception as e:
    #     print(f"❌ Failed to save frontend data: {e}")

    # Legacy profile data for the analysis view (kept for backward compatibility)
    # NOTE: analyze_profile was removed during refactoring - using content_strategy instead
    profile_data = workspace.content_strategy  # Use the modern content strategy
    
    # Generate Dynamic Website (Standalone Node.js Project)
    website_ready = False
    website_url = None
    
    print("\n=== SITE GENERATOR ===")
    react_components = {}  # Use default components for now
    website_ready = generate_dynamic_website(react_components, user_name, image_paths, site_data)
    if not website_ready:
        print("❌ Site generation failed!")
        return {
            "status": "error",
            "message": "Site generation failed",
            "website_ready": False
        }
    
    # The generated site is a standalone Node.js project at /generated_site
    # User needs to run: cd generated_site && npm run dev
    website_url = "http://localhost:3000"  # Default Vite dev server port
    
    website_url = "/portfolio/"
    print(f"✅ Dynamic site ready at: {website_url}")
    
    # ============================================================================
    # SELENIUM VALIDATOR - Disabled per request (kept code, commented out)
    # ============================================================================
    # validation_report = selenium_validator_agent(f"http://localhost:8000{website_url}")
    validation_report = {"success": True, "validation_skipped": True, "issues": [], "pages_tested": 0}
    
    # If validation found critical issues, attempt ONE regeneration
    max_retries = 1
    retry_count = 0
    
    # Disabled validation loop while Selenium agent is off
    while False and not validation_report.get("success") and retry_count < max_retries and not validation_report.get("validation_skipped"):
        print(f"\n=== VALIDATION FAILED - ATTEMPTING REGENERATION (Retry {retry_count + 1}/{max_retries}) ===")
        
        # Re-run orchestrator with validation feedback
        orchestrator = orchestrator_agent(
            design_dna=workspace.design_dna,
            content_strategy=workspace.content_strategy,
            ux_plan=workspace.ux_plan,
            react_code=workspace.react_code,
            user_name=user_name,
            image_paths=image_paths
        )
        
        # If orchestrator requests regeneration, do it
        if orchestrator.get('needs_regeneration') or len(validation_report.get('issues', [])) > 0:
            print(f"[REGENERATION] Orchestrator feedback: {orchestrator.get('regeneration_instructions', 'Fix validation issues')}")
            
            # Regenerate React code with orchestrator feedback
            react_code = react_developer_agent(
                design_dna,
                content_strategy,
                ux_plan,
                user_name,
                image_paths,
                orchestrator_feedback=orchestrator.get('regeneration_instructions', 'Fix validation issues: ' + ', '.join(validation_report.get('issues', []))),
                icon_strategy=icon_strategy
            )
            
            # Regenerate site
            website_ready = generate_dynamic_website(react_code, user_name, image_paths, site_data)
            if not website_ready:
                print("❌ Regeneration failed!")
                break
            
            # Re-validate
            print("\n=== RE-VALIDATION SKIPPED (Selenium disabled) ===")
        else:
            print("[INFO] Orchestrator declined regeneration despite validation issues")
            break
        
        retry_count += 1
    
    # Final status
    if validation_report.get("validation_skipped"):
        print("\nℹ️  SITE READY (validation disabled per request)")

    return {
        "status": "success",
        "profile": profile_data,
        "website_ready": website_ready,
        "website_url": website_url,
        "design_system": mood_system,
        "content_strategy": content_strategy,
        "ux_plan": ux_plan,
        "orchestrator": orchestrator,
        "validation": validation_report
    }

# CV generation removed: this app only generates the dynamic site.

# Serve Frontend (Plato main site)
# Note: Generated portfolios are now standalone Node.js projects
# Users run them separately with: cd generated_site && npm run dev
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
