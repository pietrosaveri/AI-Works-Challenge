from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import shutil
import os
import json
from pydantic import BaseModel
import sys

# Add project root to sys.path to allow imports from backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_service import analyze_profile, mood_agent, content_strategist_agent, ux_architect_agent, icon_curator_agent, react_developer_agent, orchestrator_agent, selenium_validator_agent
from backend.scraper import process_inputs
from backend.site_generator import generate_dynamic_website

app = FastAPI(title="Anti-Portfolio Generator")

# Ensure generated site directory exists for StaticFiles
os.makedirs("generated_site/dist", exist_ok=True)

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
    
    print("\n=== MOOD AGENT ===")
    mood_system = mood_agent(vibe_dict)
    print(f"Design System: {mood_system.get('layout_style', 'Unknown')}")
    
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
    ux_plan = ux_architect_agent(mood_system, content_strategy, user_name, image_paths)
    nav_structure = (ux_plan.get('navigation') or {}).get('structure', [])
    print(f"UX Plan Navigation: {nav_structure}")
    print(f"UX Plan Pages: {len(ux_plan.get('pages', []))}")
    
    print("\n=== ICON CURATOR AGENT ===")
    icon_strategy = icon_curator_agent(mood_system, content_strategy, ux_plan, user_name)
    print(f"Icon Library: {icon_strategy.get('icon_library', 'Unknown')}")
    print(f"Icon Suggestions: {len(icon_strategy.get('suggestions', []))} icons")
    print(f"Usage Philosophy: {icon_strategy.get('usage_philosophy', 'N/A')[:80]}")
    
    print("\n=== REACT DEVELOPER AGENT ===")
    react_code = react_developer_agent(mood_system, content_strategy, ux_plan, user_name, image_paths, icon_strategy=icon_strategy)
    print(f"Generated React Code: {len(react_code)} characters")
    
    print("\n=== ORCHESTRATOR AGENT ===")
    orchestrator = orchestrator_agent(mood_system, content_strategy, ux_plan, react_code, user_name, image_paths)
    print(f"Orchestrator Summary: {orchestrator.get('summary', 'No summary')}"[:160])
    
    # If orchestrator regenerated code, use the new version
    if orchestrator.get('react_code_regenerated') and orchestrator.get('new_react_code'):
        print("✅ Using regenerated React code from Orchestrator feedback")
        react_code = orchestrator.get('new_react_code')
    
    # Legacy profile data for the analysis view (kept for backward compatibility)
    profile_data = analyze_profile(raw_text, answers_dict)
    
    # Generate Dynamic Website
    website_ready = False
    website_url = None
    
    print("\n=== SITE GENERATOR ===")
    website_ready = generate_dynamic_website(react_code, user_name, image_paths)
    if not website_ready:
        print("❌ Site generation failed!")
        return {
            "status": "error",
            "message": "Site generation failed",
            "website_ready": False
        }
    
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
            mood_system, 
            content_strategy, 
            ux_plan, 
            react_code, 
            user_name, 
            image_paths,
            validation_report=validation_report
        )
        
        # If orchestrator requests regeneration, do it
        if orchestrator.get('needs_regeneration') or len(validation_report.get('issues', [])) > 0:
            print(f"[REGENERATION] Orchestrator feedback: {orchestrator.get('regeneration_instructions', 'Fix validation issues')}")
            
            # Regenerate React code with orchestrator feedback
            react_code = react_developer_agent(
                mood_system,
                content_strategy,
                ux_plan,
                user_name,
                image_paths,
                orchestrator_feedback=orchestrator.get('regeneration_instructions', 'Fix validation issues: ' + ', '.join(validation_report.get('issues', []))),
                icon_strategy=icon_strategy
            )
            
            # Regenerate site
            website_ready = generate_dynamic_website(react_code, user_name, image_paths)
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

# Serve Frontend
app.mount("/portfolio", StaticFiles(directory="generated_site/dist", html=True), name="portfolio")
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
