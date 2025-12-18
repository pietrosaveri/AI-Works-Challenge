#!/usr/bin/env python3
"""
Quick test script to generate a portfolio site using sample data.
This simulates what happens when a user submits the questionnaire form.
"""
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import (
    art_director_agent,
    content_strategist_agent,
    ux_architect_agent,
    icon_curator_agent,
    react_developer_agent,
    orchestrator_agent,
    Workspace
)
from backend.scraper import process_inputs
from backend.site_generator import generate_dynamic_website

# Load sample person data
sample_file = "submission_sites/person1_linus.json"
print(f"Loading sample data from: {sample_file}")

with open(sample_file, 'r') as f:
    person_data = json.load(f)

name = person_data.get('name', 'Test User')
urls_list = person_data.get('urls', [])
text_input = person_data.get('text_input', '')
answers_dict = person_data.get('answers', {})
vibe_dict = person_data.get('vibe', {})

print(f"\n{'='*80}")
print(f"GENERATING TEST SITE FOR: {name}")
print(f"{'='*80}\n")

# Process inputs
print("Processing inputs...")
raw_text = process_inputs([], urls_list)
raw_text += f"\n\n--- User Additional Notes ---\n{text_input}"

# MULTI-AGENT ORCHESTRATION
print("\n=== ART DIRECTOR AGENT (DESIGN DNA) ===")
design_dna = art_director_agent(raw_text, answers_dict, vibe_dict)
print(f"✅ Design DNA: {design_dna.get('layout')} / {design_dna.get('theme')}")

print("\n=== CONTENT STRATEGIST AGENT ===")
content_strategy = content_strategist_agent(raw_text, answers_dict)
pages = content_strategy.get('pages', {})
home_data = pages.get('home', {}) or {}
print(f"✅ Content Strategy created")
print(f"   Thesis: {home_data.get('thesis', 'Unknown')[:80]}...")

print("\n=== UX ARCHITECT AGENT ===")
user_name = name
ux_plan = ux_architect_agent(design_dna, content_strategy, user_name, [])
print(f"✅ UX Plan: {len(ux_plan.get('pages', []))} pages")

print("\n=== ICON CURATOR AGENT ===")
icon_strategy = icon_curator_agent(design_dna, content_strategy, ux_plan, user_name)
print(f"✅ Icon Strategy: {icon_strategy.get('icon_library', 'Unknown')}")

print("\n=== REACT DEVELOPER AGENT ===")
react_code = react_developer_agent(
    design_dna, content_strategy, ux_plan, user_name, [],
    icon_strategy=icon_strategy
)
print(f"✅ Generated React Code: {len(react_code)} characters")

# Build workspace
workspace = Workspace(
    design_dna=design_dna,
    content_strategy=content_strategy,
    ux_plan=ux_plan,
    icon_plan=icon_strategy,
    react_code=react_code,
    action_log=["v0: initial generation"]
)

print("\n=== ORCHESTRATOR AGENT ===")
orchestrator = orchestrator_agent(
    design_dna=workspace.design_dna,
    content_strategy=workspace.content_strategy,
    ux_plan=workspace.ux_plan,
    react_code=workspace.react_code,
    user_name=user_name,
    image_paths=[]
)
print(f"✅ Orchestrator: {orchestrator.get('summary', 'No summary')[:100]}")

# Prepare site data
mood_system = {
    'colors': {
        'primary': design_dna['color_palette'][0],
        'secondary': design_dna['color_palette'][1],
        'accent': design_dna['color_palette'][2] if len(design_dna['color_palette']) > 2 else design_dna['color_palette'][1],
        'background': design_dna['color_palette'][3] if len(design_dna['color_palette']) > 3 else '#fff',
        'text': design_dna['color_palette'][4] if len(design_dna['color_palette']) > 4 else '#000'
    },
    'typography': design_dna.get('typography_pair'),
    'layout_style': design_dna.get('layout'),
    'theme': design_dna.get('theme')
}

site_data = {
    "user_name": user_name,
    "design_dna": design_dna,
    "content_strategy": workspace.content_strategy,
    "ux_plan": workspace.ux_plan,
    "icon_strategy": icon_strategy,
    "mood_system": mood_system
}

# Generate website
print("\n=== SITE GENERATOR ===")
# For now, pass empty dict as react_components - will use default components
react_components = {}
website_ready = generate_dynamic_website(react_components, user_name, [], site_data)

if website_ready:
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS! Test site generated")
    print(f"{'='*80}")
    print("\nTo view the site:")
    print("  cd generated_site")
    print("  npm run dev")
    print("\nThen visit: http://localhost:3000")
else:
    print(f"\n❌ Site generation failed!")
    sys.exit(1)
