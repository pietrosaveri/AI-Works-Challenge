#!/usr/bin/env python3
"""
Script to generate a single portfolio site based on JSON configuration.
Usage: python generate_single_site.py <json_file> <output_folder>
"""
import json
import os
import sys
import shutil

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm_service import (
    mood_agent, content_strategist_agent, ux_architect_agent, 
    icon_curator_agent, react_developer_agent, orchestrator_agent
)
from backend.scraper import process_inputs
from backend.site_generator import generate_dynamic_website


def generate_site_for_person(json_file_path, output_folder):
    """Generate a portfolio site for a person based on their JSON configuration."""
    
    # Load person's data
    with open(json_file_path, 'r') as f:
        person_data = json.load(f)
    
    name = person_data.get('name', 'Unknown')
    urls_list = person_data.get('urls', [])
    text_input = person_data.get('text_input', '')
    answers_dict = person_data.get('answers', {})
    vibe_dict = person_data.get('vibe', {})
    
    print(f"\n{'='*80}")
    print(f"GENERATING SITE FOR: {name}")
    print(f"{'='*80}\n")
    
    # Process inputs
    raw_text = process_inputs([], urls_list)
    raw_text += f"\n\n--- User Additional Notes ---\n{text_input}"
    
    # MULTI-AGENT ORCHESTRATION
    print("\n=== MOOD AGENT ===")
    mood_system = mood_agent(vibe_dict)
    print(f"Design System: {mood_system.get('layout_style', 'Unknown')}")
    
    print("\n=== CONTENT STRATEGIST AGENT ===")
    content_strategy = content_strategist_agent(raw_text, answers_dict)
    pages = content_strategy.get('pages', {})
    home_data = pages.get('home', {}) or {}
    print(f"Thesis: {home_data.get('thesis', 'Unknown')[:80]}...")
    
    print("\n=== UX ARCHITECT AGENT ===")
    user_name = name
    ux_plan = ux_architect_agent(mood_system, content_strategy, user_name, [])
    print(f"UX Plan Pages: {len(ux_plan.get('pages', []))}")
    
    print("\n=== ICON CURATOR AGENT ===")
    icon_strategy = icon_curator_agent(mood_system, content_strategy, ux_plan, user_name)
    print(f"Icon Library: {icon_strategy.get('icon_library', 'Unknown')}")
    
    print("\n=== REACT DEVELOPER AGENT ===")
    react_code = react_developer_agent(
        mood_system, content_strategy, ux_plan, user_name, [], 
        icon_strategy=icon_strategy
    )
    print(f"Generated React Code: {len(react_code)} characters")
    
    print("\n=== ORCHESTRATOR AGENT ===")
    orchestrator = orchestrator_agent(
        mood_system, content_strategy, ux_plan, react_code, user_name, []
    )
    print(f"Orchestrator Summary: {orchestrator.get('summary', 'No summary')[:160]}")
    
    # Orchestrator feedback loop
    max_orchestrator_retries = 2
    orchestrator_retry_count = 0
    
    while orchestrator.get('needs_regeneration') and orchestrator_retry_count < max_orchestrator_retries:
        print(f"\n=== ORCHESTRATOR REQUESTS REGENERATION (Attempt {orchestrator_retry_count + 1}/{max_orchestrator_retries}) ===")
        
        react_code = react_developer_agent(
            mood_system, content_strategy, ux_plan, user_name, [],
            orchestrator_feedback=orchestrator.get('regeneration_instructions', 'Fix the issues'),
            icon_strategy=icon_strategy
        )
        
        orchestrator = orchestrator_agent(
            mood_system, content_strategy, ux_plan, react_code, user_name, []
        )
        orchestrator_retry_count += 1
    
    # Generate website
    print("\n=== SITE GENERATOR ===")
    website_ready = generate_dynamic_website(react_code, user_name, [])
    
    if not website_ready:
        print(f"❌ Site generation failed for {name}!")
        return False
    
    print(f"✅ Site generated successfully!")
    
    # Copy generated site to submission folder
    source_dir = "generated_site/dist"
    if os.path.exists(source_dir):
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Copy all files
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            dest_path = os.path.join(output_folder, item)
            
            if os.path.isdir(source_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
        
        print(f"✅ Site copied to: {output_folder}")
        return True
    else:
        print(f"❌ Generated site directory not found!")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_single_site.py <json_file> <output_folder>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_folder = sys.argv[2]
    
    success = generate_site_for_person(json_file, output_folder)
    
    if success:
        print(f"\n✅ SUCCESS: Site generated at {output_folder}")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED: Could not generate site")
        sys.exit(1)
