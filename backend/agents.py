"""
Agent functions for the Professional Fingerprint application.
Contains all specialized agents for content generation, design, UX, and code generation.
"""
import json
import os
import time
import hashlib
from typing import List, Dict, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser

from .llm_config import get_llm_with_temp, get_llm_for_code_generation, llm
from .models import (
    IconStrategy, OrchestratorReport, DesignDNA, ContentStrategy,
    UXPlan, MoodSystem
)
from .utils import _sanitize_json_output, apply_react_patches


def icon_curator_agent(design_dna: dict, content_strategy: dict, ux_plan: dict, user_name: str) -> dict:
    """
    Selects the perfect icon set and usage strategy.
    """
    print("  ...Icon Curator is selecting iconography...")
    
    parser = PydanticOutputParser(pydantic_object=IconStrategy)
    
    system_prompt = """
You are an expert UI/UX Designer specializing in Iconography.
Your goal is to select a cohesive icon set that matches the Design DNA.

DESIGN DNA:
- Archetype: {archetype}
- Theme: {theme}
- Vibe: {vibe}

ICON LIBRARIES (Choose ONE):
- Lucide React: Modern, clean, consistent (Best for most)
- Heroicons: Friendly, rounded (Good for corporate/clean)
- Phosphor Icons: Versatile, multiple weights (Good for tech)
- Feather Icons: Super minimal (good for brutalist/clean)

PLACEMENT STRATEGY:
- Navigation: Small icons next to menu items (optional, only if adds value)
- Section Headers: Decorative icons for major sections (Patterns, Failures, etc.)
- Feature Cards: Icons to represent each pattern/skill
- Hero: ONE subtle decorative icon (optional)
- Footer/About: Contact/social icons

ICON SELECTION RULES:
- Match content meaning (e.g., target for goals, puzzle for patterns, bolt for decisions)
- Consider mood/personality (playful = rounded, serious = geometric)
- Use consistent style (all outlined OR all filled, never mixed)

COLOR SCHEMES:
- Accent: Icons use the accent color from mood system
- Gradient: Icons have gradient fills (for premium feel)
- Monochrome: Icons match text color (for minimal feel)

OUTPUT VALID JSON ONLY. NO EXPLANATIONS.

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """Curate icons for: {user_name}

MOOD SYSTEM:
{mood_system}

CONTENT STRUCTURE:
{content_structure}

UX PLAN:
{ux_plan}

Select 3-8 meaningful icons that enhance this design.""")
    ])
    
    chain = prompt | (llm or get_llm_with_temp(0.3)) | StrOutputParser()
    
    try:
        design_dna = design_dna or {}
        content_strategy = content_strategy or {}
        ux_plan = ux_plan or {}
        pages = content_strategy.get('pages', {}) if isinstance(content_strategy, dict) else {}
        content_structure = {
            'sections': list(pages.keys()),
            'pattern_count': len((pages.get('behavioral_patterns') or {}).get('patterns', [])),
            'has_failures': bool(pages.get('failures_and_lessons')),
            'has_decisions': bool(pages.get('decision_architecture')),
            'style': (design_dna.get('layout') if isinstance(design_dna, dict) else 'Unknown') or 'Unknown'
        }
        
        raw = chain.invoke({
            "user_name": user_name,
            "archetype": (design_dna.get('archetype') if isinstance(design_dna, dict) else 'Unknown') or 'Unknown',
            "theme": (design_dna.get('theme') if isinstance(design_dna, dict) else 'Unknown') or 'Unknown',
            "vibe": (design_dna.get('reasoning') if isinstance(design_dna, dict) else 'Professional') or 'Professional',
            "mood_system": json.dumps(design_dna, indent=2),
            "content_structure": json.dumps(content_structure, indent=2),
            "ux_plan": json.dumps(ux_plan, indent=2)[:1000],
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"[DEBUG] Icon Curator raw output length: {len(raw)} characters")
        
        data = _sanitize_json_output(raw)
        validated = IconStrategy.model_validate(data)
        return validated.model_dump()
    except Exception as e:
        print(f"Icon Curator Agent Error: {e}")
        return {
            "icon_library": "lucide",
            "cdn_url": "https://unpkg.com/lucide@latest/dist/umd/lucide.min.js",
            "color_scheme": "accent",
            "suggestions": [
                {"location": "navigation-home", "icon_name": "home", "purpose": "Home navigation"},
                {"location": "navigation-patterns", "icon_name": "puzzle", "purpose": "Patterns section"},
                {"location": "navigation-about", "icon_name": "user", "purpose": "About section"},
                {"location": "hero-decorative", "icon_name": "sparkles", "purpose": "Hero accent"},
                {"location": "pattern-cards", "icon_name": "target", "purpose": "Pattern indicators"}
            ],
            "usage_philosophy": "Minimal functional icons for navigation and section identification"
        }


def orchestrator_agent(
    design_dna: dict,
    content_strategy: dict,
    ux_plan: dict,
    react_code: str,
    user_name: str,
    image_paths: list = None
) -> dict:
    """
    Supervise agents to ensure cohesion, design quality, and completeness.
    """
    parser = PydanticOutputParser(pydantic_object=OrchestratorReport)

    system_prompt = """
You are the Orchestrator Agent supervising a multi-agent website generator.
You validate the output but RARELY request regeneration (only for critical issues).

CONSTRAINTS - THIS IS A SINGLE HTML FILE SYSTEM:
- CANNOT use build pipelines (Vite, Webpack, etc.)
- MUST use CDN imports (React UMD, Babel standalone, Tailwind)
- CANNOT require npm, node_modules, or compilation steps
- The HTML file must be ready to open directly in a browser

Responsibilities:
- Check if ALL CDN scripts are present (React, ReactDOM, Babel, Tailwind, Framer Motion)
- Verify content pages are populated (not just the home page)
- Ensure navigation matches available pages
- Check if colors from MOOD_SYSTEM are being used
- Validate that CONTENT_DATA is embedded in the script

REGENERATION RULES:
If CONTENT_DATA is missing/empty, Request "Content Strategist regeneration: pages are empty or missing"
If navigation does not match pages, Request "UX Architect regeneration: navigation mismatch with available pages"
If CDN scripts missing, Request "React Developer regeneration: missing CDN scripts [list them]"
If pages lack real content, Request "Content Strategist regeneration: pages contain placeholder text instead of real analysis"

ONLY REQUEST REGENERATION IF:
1. Critical CDN script is missing (e.g., Babel standalone)
2. CONTENT_DATA is not embedded or is empty (CONTENT ISSUE)
3. Navigation links do not work (UX ISSUE)
4. All pages show placeholder text instead of real content (CONTENT ISSUE)

DO NOT REQUEST REGENERATION FOR:
- Minor styling issues
- Font preferences
- Animation timing
- Accessibility attributes (nice to have)
- Color shade variations

Return JSON only.
Fields:
- validations: array of specific checks ("OK Babel CDN present", "X Missing CONTENT_DATA", etc.)
- needs_regeneration: boolean - ONLY true for critical issues
- regeneration_instructions: BRIEF, specific fix (1-2 sentences max)
- summary: assessment in 1 sentence
{format_instructions}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", (
            "USER: {user}\n\n"
            "MOOD_SYSTEM:\n{mood}\n\n"
            "CONTENT_STRATEGY:\n{content}\n\n"
            "UX_PLAN:\n{ux}\n\n"
            "REACT_CODE LENGTH: {code_length} characters\n"
            "REACT_CODE PREVIEW (first 2000 chars):\n{react}"
        ))
    ])

    chain = prompt | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "user": user_name,
            "mood": json.dumps(design_dna, indent=2),
            "content": json.dumps(content_strategy, indent=2),
            "ux": json.dumps(ux_plan, indent=2),
            "code_length": len(react_code),
            "react": react_code[:2000],
            "format_instructions": parser.get_format_instructions()
        })
        data = _sanitize_json_output(raw)
        validated = OrchestratorReport.model_validate(data)
        result = validated.model_dump()
        
        if result.get('needs_regeneration'):
            print(f"\n⚠️  ORCHESTRATOR DETECTED ISSUES (regeneration disabled):")
            print(f"Issues: {result.get('regeneration_instructions')}")
        
        return result
    except Exception as e:
        print(f"Orchestrator Agent Error: {e}")
        return {
            "validations": ["Fallback: unable to parse orchestrator output"],
            "needs_regeneration": False,
            "regeneration_instructions": None,
            "design_directives": {},
            "content_adjustments": {},
            "summary": "Proceed with current outputs; manual review recommended."
        }


def art_director_agent(raw_text: str, answers: dict, vibe: dict) -> dict:
    """
    Analyzes the user profile to generate a unique Design DNA.
    Selects specific Layout, Motion, Theme, and Archetype combinations.
    """
    print("  ...Art Director is curating the unique design DNA...")
    
    creative_llm = get_llm_with_temp(0.7)
    parser = PydanticOutputParser(pydantic_object=DesignDNA)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a world-class Art Director and Creative Technologist.
        Your goal is to design a COMPLETELY UNIQUE digital portfolio for a user based on their personality.
        
        We have a "Generative Design System" with 4 layers. You must select the perfect combination.
        
        USER PROFILE:
        - Answers: {answers}
        - Vibe Check: {vibe}
        - Content Excerpt: {raw_text_snippet}
        
        AVAILABLE OPTIONS:
        
        1. LAYOUT ENGINE (The Skeleton):
           - 'single_stream': Mobile-first, social media feed style. Good for influencers/creators.
           - 'bento_grid': Boxy, organized, dashboard style. Good for product managers/designers.
           - 'asymmetric_scatter': Elements placed randomly/artistically. Good for artists/rebels.
           - 'horizontal_gallery': Side-scrolling museum feel. Good for photographers/visual artists.
           - 'split_screen': Fixed left, scrolling right. Good for academics/writers.
           - 'terminal_console': Text-heavy, code-based. Good for backend devs/hackers.
           - 'magazine_editorial': Big typography, overlapping elements. Good for writers/strategists.
           
        2. MOTION ENGINE (The Nervous System):
           - 'parallax_deep': Backgrounds move slower than foregrounds. Immersive.
           - 'scroll_jacking': Snap to sections, full-screen wipes. Cinematic.
           - 'micro_interactions': Hover effects, cursor followers. Playful.
           - 'brutal_static': Zero animation, instant loading. Raw/Serious.
           - 'liquid_fluid': Smooth morphing shapes. Organic/Soft.
           - '3d_transforms': Cards flipping, perspective tilts. Tech-forward.
           - 'typewriter_reveal': Text appears as you read. Narrative-focused.
           
        3. VISUAL THEME (The Skin):
           - 'neo_brutalist': High contrast, thick borders, harsh shadows. Bold/Trendy.
           - 'glassmorphism': Blur, transparency, gradients. Modern/SaaS.
           - 'minimal_zen': Black/white, tons of whitespace. Sophisticated.
           - 'cyberpunk_neon': Dark mode, glitch effects. Futuristic.
           - 'paper_collage': Texture overlays, ripped edges. DIY/Creative.
           - 'corporate_clean': Safe blues, rounded corners. Professional.
           - 'swiss_international': Grid-based, helvetica, objective. Design-purist.
           - 'vaporwave_retro': Pink/blue, eighties aesthetics, nostalgia. Internet-native.
           
        4. CONTENT ARCHETYPE (The Soul):
           - 'manifesto': Philosophy first, work second. For thought leaders.
           - 'case_study': Deep dive into process. For UX/Engineers.
           - 'timeline_journey': Chronological story. For those with a rich history.
           - 'skill_tree': Gamified stats and abilities. For generalists.
           - 'anti_resume': Failures, learnings, opinions. For disruptors.
           - 'digital_garden': Interconnected notes and thoughts. For researchers.
           
        TASK:
        Analyze the user Vibe and Answers deeply. 
        Do NOT default to "bento_grid" or "minimal_zen". Be bold.
        Mix and match these layers to create a persona that fits them perfectly.
        
        Example: A chaotic creative might get 'asymmetric_scatter' + 'liquid_fluid' + 'neo_brutalist'.
        Example: A senior backend dev might get 'terminal_console' + 'typewriter_reveal' + 'cyberpunk_neon'.
        
        {format_instructions}
        """
    )
    
    raw_text_snippet = raw_text[:2000] if raw_text else "No text provided"
    # Use string parser first, then sanitize, then validate
    chain = prompt | creative_llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "answers": json.dumps(answers, indent=2),
            "vibe": json.dumps(vibe, indent=2),
            "raw_text_snippet": raw_text_snippet,
            "format_instructions": parser.get_format_instructions()
        })
        data = _sanitize_json_output(raw)
        validated = DesignDNA.model_validate(data)
        return validated.model_dump()
    except Exception as e:
        print(f"Error in Art Director Agent: {e}")
        return {
            "layout": "bento_grid",
            "motion": "micro_interactions",
            "theme": "minimal_zen",
            "archetype": "case_study",
            "color_palette": ["#ffffff", "#000000", "#f3f4f6", "#3b82f6", "#1f2937"],
            "typography_pair": {"heading": "Inter", "body": "Inter"},
            "rationale": "Fallback due to error"
        }


def mood_agent(vibe_data: dict) -> dict:
    """
    Mood Agent: Derives a visual design system from user vibe inputs.
    NOW DETERMINISTIC - Uses hash-based selection for consistent, diverse results.
    """
    vibe_string = f"{vibe_data.get('favorite_color', 'blue')}{vibe_data.get('animal', 'wolf')}{vibe_data.get('abstract_word', 'flow')}"
    vibe_hash = int(hashlib.md5(vibe_string.encode()).hexdigest(), 16)
    
    color_palettes = [
        {"primary": "#0071e3", "secondary": "#1d1d1f", "accent": "#2997ff", "background": "#000000", "text": "#f5f5f7"},
        {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D", "background": "#1A1A2E", "text": "#EAEAEA"},
        {"primary": "#6C5CE7", "secondary": "#A29BFE", "accent": "#FD79A8", "background": "#2D3436", "text": "#DFE6E9"},
        {"primary": "#00B894", "secondary": "#00CEC9", "accent": "#FDCB6E", "background": "#0A0E27", "text": "#F8F9FA"},
        {"primary": "#E17055", "secondary": "#FDCB6E", "accent": "#74B9FF", "background": "#FAF3E0", "text": "#2D3436"},
        {"primary": "#FF3838", "secondary": "#FF6348", "accent": "#FFC048", "background": "#F5F5F5", "text": "#1E272E"},
        {"primary": "#3742FA", "secondary": "#5352ED", "accent": "#FF6348", "background": "#FFFFFF", "text": "#2F3542"},
        {"primary": "#2ECC71", "secondary": "#27AE60", "accent": "#F39C12", "background": "#ECF0F1", "text": "#2C3E50"},
        {"primary": "#E91E63", "secondary": "#9C27B0", "accent": "#00BCD4", "background": "#1C1C1C", "text": "#FFFFFF"},
        {"primary": "#FF9500", "secondary": "#FF5722", "accent": "#4CAF50", "background": "#FAFAFA", "text": "#212121"},
        {"primary": "#607D8B", "secondary": "#455A64", "accent": "#FF5722", "background": "#ECEFF1", "text": "#263238"},
        {"primary": "#1DE9B6", "secondary": "#00E676", "accent": "#FFEA00", "background": "#121212", "text": "#E0E0E0"}
    ]
    
    font_pairings = [
        {"heading": "Inter, sans-serif", "body": "Inter, sans-serif"},
        {"heading": "Playfair Display, serif", "body": "Lora, serif"},
        {"heading": "Space Grotesk, sans-serif", "body": "Work Sans, sans-serif"},
        {"heading": "Syne, sans-serif", "body": "DM Sans, sans-serif"},
        {"heading": "Archivo Black, sans-serif", "body": "IBM Plex Sans, sans-serif"},
        {"heading": "Cormorant Garamond, serif", "body": "Source Serif Pro, serif"},
        {"heading": "JetBrains Mono, monospace", "body": "IBM Plex Mono, monospace"},
        {"heading": "Montserrat, sans-serif", "body": "Open Sans, sans-serif"},
        {"heading": "Bebas Neue, sans-serif", "body": "Roboto, sans-serif"},
        {"heading": "Crimson Text, serif", "body": "Merriweather, serif"}
    ]
    
    layout_styles = [
        "Apple Minimalist", "Swiss Brutalist", "Editorial Magazine", "Tech Dashboard",
        "Creative Studio", "Luxury Fashion", "Cyberpunk", "Academic Clean",
        "Startup Modern", "Artistic Portfolio"
    ]
    
    palette = color_palettes[vibe_hash % len(color_palettes)]
    fonts = font_pairings[vibe_hash % len(font_pairings)]
    layout_style = layout_styles[vibe_hash % len(layout_styles)]
    
    mood_keywords = [
        vibe_data.get('favorite_color', 'balanced').lower(),
        vibe_data.get('animal', 'adaptive').lower(),
        layout_style.split()[0].lower()
    ]
    
    print(f"[DETERMINISTIC] Selected palette #{vibe_hash % len(color_palettes)}, fonts #{vibe_hash % len(font_pairings)}, style: {layout_style}")
    
    return {
        "colors": palette,
        "fonts": fonts,
        "layout_style": layout_style,
        "mood_keywords": mood_keywords,
        "reasoning": f"Deterministically selected based on user vibe inputs (hash: {vibe_hash % 1000})"
    }


def content_strategist_agent(context_text: str, user_answers: dict) -> dict:
    """
    Content Strategist Agent: The CENTRAL agent that decides what goes on the website.
    Now with retry logic for reliability.
    """
    parser = PydanticOutputParser(pydantic_object=ContentStrategy)
    
    system_prompt = """
You are a Content Strategist and Behavioral Analyst for Professional Fingerprinting.

YOUR MISSION:
Extract and curate the user professional psyche into a comprehensive, multi-chapter thesis.
This is NOT a CV. This is NOT a portfolio. This is a deep, forensic interpretation of how they think, decide, and fail.

CRITICAL RULES:
1. DO NOT include job titles, employment timelines, or standard skill lists
2. DO NOT invent or exaggerate - use ONLY what is evident in the data
3. Generate DETAILED, MULTI-PARAGRAPH content for each section (3-5 paragraphs per insight)
4. Each paragraph must include: examples, context, reasoning, trade-offs, and concrete evidence
5. Be ruthlessly selective - choose only the MOST illustrative examples, but develop them fully
6. Write in FIRST PERSON from the user perspective (I, my, me) - this is THEIR voice
7. Keep headings CONCISE and IMPACTFUL (3-7 words max) - avoid long, academic titles
8. Vary tone per section: patterns can be analytical, failures reflective, method confident, anti-claims bold
9. Every piece of content must reveal something NON-OBVIOUS about the user
10. Plan content for MULTIPLE PAGES - each major section gets its own dedicated page
11. Break up long paragraphs with line breaks, subheadings, or bullet points for readability

OUTPUT REQUIREMENTS (CRITICAL):
- Return ONLY valid JSON
- NO markdown code blocks (no ```)
- NO explanatory text before or after the JSON
- NO special tokens like <|channel|> or <|message|>
- Start with {{ and end with }}
- MUST have this EXACT top-level structure:
  {{
    "pages": {{
      "home": {{ ... }},
      "behavioral_patterns": {{ ... }},
      ...
    }},
    "meta": {{
      "site_title": "...",
      "navigation_structure": [...]
    }}
  }}

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "USER INTERVIEW ANSWERS:\n{answers}\n\nRAW DATA:\n{context}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            temp = 0.3 + (attempt * 0.1)
            retry_llm = get_llm_with_temp(temp)
            retry_chain = prompt | retry_llm | StrOutputParser()
            
            raw = retry_chain.invoke({
                "answers": json.dumps(user_answers, indent=2),
                "context": context_text[:25000],
                "format_instructions": parser.get_format_instructions()
            })
            
            print(f"[DEBUG] Content Strategist attempt {attempt + 1}, raw output length: {len(raw)} characters")
            
            data = _sanitize_json_output(raw)
            
            # Auto-correct structure issues
            if not isinstance(data, dict):
                raise ValueError("Parsed data is not a dictionary")
            
            if 'pages' not in data and 'meta' not in data:
                if any(key in data for key in ['home', 'behavioral_patterns', 'anti_claims']):
                    data = {
                        'pages': data,
                        'meta': {
                            'site_title': user_answers.get('who_are_you', 'Professional Fingerprint'),
                            'navigation_structure': ['Home', 'Patterns', 'About']
                        }
                    }
            
            if 'pages' not in data:
                data['pages'] = {'home': {'thesis': 'Analysis in progress', 'introduction': ['Generating...'], 'navigation_prompt': 'Explore'}}
            
            if 'meta' not in data:
                data['meta'] = {
                    'site_title': user_answers.get('who_are_you', 'Professional Fingerprint'),
                    'navigation_structure': list(data.get('pages', {}).keys())
                }
            
            if 'home' not in data.get('pages', {}):
                data['pages']['home'] = {
                    'thesis': 'Analysis in progress',
                    'introduction': ['Generating content...'],
                    'navigation_prompt': 'Explore'
                }
            
            validated = ContentStrategy.model_validate(data)
            print(f"[SUCCESS] Content Strategist succeeded on attempt {attempt + 1}")
            return validated.model_dump()
            
        except Exception as e:
            print(f"[ERROR] Content Strategist attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                break
    
    # Minimal fallback
    return {
        "pages": {
            "home": {"thesis": "Analysis in progress", "introduction": ["Generating..."], "navigation_prompt": "Explore"},
            "behavioral_patterns": {"page_title": "Patterns", "introduction": ["Analyzing..."], "patterns": []},
            "about": {"page_title": "About", "introduction": ["Contact info..."], "guidelines": [], "contact_prompt": "Get in touch"}
        },
        "meta": {"site_title": "Professional Fingerprint", "navigation_structure": ["Home", "Patterns", "About"]}
    }


def ux_architect_agent(design_dna: dict, content_strategy: dict, user_name: str, image_paths: list) -> dict:
    """
    UX Architect Agent: Plans the site structure based on the Design DNA archetype.
    """
    parser = PydanticOutputParser(pydantic_object=UXPlan)
    
    system_prompt = """
You are a Senior UX Architect and Information Designer.
Your task is to design a UNIQUE site structure based on the Design DNA archetype.

DESIGN DNA RECEIVED:
- Archetype: {archetype}
- Layout: {layout}
- Theme: {theme}

OUTPUT VALID JSON ONLY.

{format_instructions}
"""

    image_info = ""
    if image_paths:
        image_info = f"\nAvailable images ({len(image_paths)} files):\n"
        for img in image_paths:
            filename = os.path.basename(img)
            image_info += f"  - {filename}\n"
    else:
        image_info = "\nNo images uploaded."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Design UX for: {user_name}\n\nCONTENT STRATEGY:\n{content_strategy}\n\n{image_info}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "user_name": user_name,
            "archetype": design_dna.get('archetype', 'case_study'),
            "layout": design_dna.get('layout', 'bento_grid'),
            "theme": design_dna.get('theme', 'minimal_zen'),
            "content_strategy": json.dumps(content_strategy, indent=2),
            "image_info": image_info,
            "format_instructions": parser.get_format_instructions()
        })
        
        data = _sanitize_json_output(raw)
        validated = UXPlan.model_validate(data)
        return validated.model_dump()
        
    except Exception as e:
        print(f"UX Architect Agent Error: {e}")
        archetype = design_dna.get('archetype', 'case_study')
        page_names = {
            'manifesto': ["Manifesto", "Beliefs", "Work", "Contact"],
            'case_study': ["Overview", "Process", "Work", "Contact"],
            'timeline_journey': ["Journey", "Milestones", "Now", "Contact"],
            'skill_tree': ["Skills", "Projects", "Tools", "Contact"],
            'anti_resume': ["Boundaries", "Failures", "Learnings", "Contact"],
            'digital_garden': ["Garden", "Notes", "Links", "Contact"]
        }.get(archetype, ["Home", "Work", "About", "Contact"])
        
        return {
            "navigation": {"type": "fixed-top-nav", "structure": page_names, "style": "Fixed header"},
            "pages": [{"id": "page1", "layout": "full-width", "components": ["Hero"], "typography": {"heading": "text-5xl", "body": "text-lg"}, "animations": [], "scroll_behavior": "smooth"}],
            "typography_system": {"custom_fonts": design_dna.get('typography_pair', {}).get('heading', 'Inter'), "font_scale": "Standard"},
            "animation_strategy": {"style": "Subtle and polished"}
        }


def react_developer_agent(
    design_dna: dict,
    content_strategy: dict,
    ux_plan: dict,
    user_name: str,
    image_paths: list,
    orchestrator_feedback: str = None,
    icon_strategy: dict = None,
    base_react_code: str = None,
) -> str:
    """
    React Developer Agent: Generates complete single-file React HTML with embedded React.
    Creates a fully functional, self-contained HTML file with CDN-based React.
    """
    print("[DEBUG] React Developer Agent starting generation...")
    
    # Extract design system colors and fonts
    primary_color = design_dna.get('color_palette', ['#0071e3'])[0] if design_dna.get('color_palette') else '#0071e3'
    accent_color = design_dna.get('color_palette', ['#0071e3', '#2997ff', '#2997ff'])[2] if len(design_dna.get('color_palette', [])) > 2 else '#2997ff'
    bg_color = design_dna.get('color_palette', ['#fff', '#fff', '#fff', '#000'])[3] if len(design_dna.get('color_palette', [])) > 3 else '#000000'
    text_color = design_dna.get('color_palette', ['#fff', '#fff', '#fff', '#000', '#f5f5f7'])[4] if len(design_dna.get('color_palette', [])) > 4 else '#f5f5f7'
    
    heading_font = design_dna.get('typography_pair', {}).get('heading', 'Inter, sans-serif')
    body_font = design_dna.get('typography_pair', {}).get('body', 'Inter, sans-serif')
    
    # Extract content
    pages = content_strategy.get('pages', {})
    home_page = pages.get('home', {})
    patterns_page = pages.get('behavioral_patterns', {})
    about_page = pages.get('about', {})
    
    hero_headline = home_page.get('thesis', 'Professional Portfolio')[:100]
    hero_intro = home_page.get('introduction', ['Welcome'])
    hero_subheadline = hero_intro[0][:150] if hero_intro else 'Portfolio'
    
    patterns = patterns_page.get('patterns', []) if patterns_page else []
    
    # Generate navigation items from UX plan
    nav_structure = ux_plan.get('navigation', {}).get('structure', ['Home', 'About'])
    
    print(f"[DEBUG] Generating site with {len(patterns)} patterns, {len(nav_structure)} nav items")
    
    # Build the complete HTML with embedded React
    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_name} - Professional Fingerprint</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/framer-motion@10/dist/framer-motion.js"></script>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family={heading_font.replace(' ', '+').replace(',', '%2C')}:wght@400;700;900&family={body_font.replace(' ', '+').replace(',', '%2C')}:wght@400&display=swap" rel="stylesheet">
    <style>
        body {{ 
            background: {bg_color}; 
            color: {text_color};
            font-family: {body_font};
            margin: 0;
            padding: 0;
        }}
        h1, h2, h3 {{ font-family: {heading_font}; color: {text_color}; }}
        .glass {{
            background: rgba(20, 20, 20, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .gradient-text {{
            background: linear-gradient(135deg, {primary_color}, {accent_color});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .text-accent {{ color: {accent_color}; }}
        .bg-accent {{ background: {accent_color}; }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const Motion = window.Motion || {{}};
        const motion = Motion.motion || (({{children, ...props}}) => React.createElement('div', props, children));
        const AnimatePresence = Motion.AnimatePresence || (({{children}}) => children);
        const {{ useState, useEffect }} = React;
        
        // Embed content data
        const CONTENT_DATA = {json.dumps(content_strategy, indent=2)};
        
        function Navigation({{ currentRoute, setRoute }}) {{
            const navItems = [
                {{ id: 'home', label: 'Home' }},
                {{ id: 'patterns', label: 'Patterns', count: {len(patterns)} }},
                {{ id: 'about', label: 'About' }}
            ];
            
            return (
                <nav className="fixed top-0 left-0 right-0 z-50 glass">
                    <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
                        <div className="text-xl font-bold gradient-text">{user_name}</div>
                        <div className="flex gap-8">
                            {{navItems.map(item => (
                                <button
                                    key={{item.id}}
                                    onClick={{() => setRoute(item.id)}}
                                    className={{`transition-all duration-200 ${{currentRoute === item.id ? 'opacity-100 font-semibold' : 'opacity-60 hover:opacity-100'}}`}}
                                    style={{{{ color: currentRoute === item.id ? '{accent_color}' : '{text_color}' }}}}
                                >
                                    {{item.label}} {{item.count > 0 && `({{item.count}})`}}
                                </button>
                            ))}}
                        </div>
                    </div>
                </nav>
            );
        }}
        
        function HomePage() {{
            return (
                <motion.div
                    initial={{{{ opacity: 0 }}}}
                    animate={{{{ opacity: 1 }}}}
                    transition={{{{ duration: 1 }}}}
                    className="min-h-screen flex flex-col items-center justify-center px-8 pt-20"
                >
                    <div className="absolute inset-0 opacity-20" 
                         style={{{{ background: `radial-gradient(circle at 50% 50%, {primary_color}, transparent 70%)` }}}} />
                    <div className="relative z-10 text-center max-w-5xl">
                        <motion.h1 
                            className="text-6xl md:text-8xl font-bold mb-8 tracking-tight gradient-text"
                            initial={{{{ opacity: 0, y: 50 }}}}
                            animate={{{{ opacity: 1, y: 0 }}}}
                            transition={{{{ delay: 0.2, duration: 0.8 }}}}
                        >
                            {hero_headline}
                        </motion.h1>
                        <motion.p 
                            className="text-xl md:text-2xl opacity-80 font-light leading-relaxed"
                            initial={{{{ opacity: 0, y: 20 }}}}
                            animate={{{{ opacity: 1, y: 0 }}}}
                            transition={{{{ delay: 0.5, duration: 0.8 }}}}
                        >
                            {hero_subheadline}
                        </motion.p>
                    </div>
                </motion.div>
            );
        }}
        
        function PatternsPage() {{
            const patterns = CONTENT_DATA?.pages?.behavioral_patterns?.patterns || [];
            
            if (patterns.length === 0) {{
                return (
                    <motion.div
                        initial={{{{ opacity: 0 }}}}
                        animate={{{{ opacity: 1 }}}}
                        className="min-h-screen flex items-center justify-center px-8 pt-20"
                    >
                        <div className="text-center max-w-2xl">
                            <h1 className="text-5xl font-bold mb-8 gradient-text">Patterns</h1>
                            <p className="text-xl opacity-70">No behavioral patterns identified yet.</p>
                        </div>
                    </motion.div>
                );
            }}
            
            return (
                <motion.div
                    initial={{{{ opacity: 0 }}}}
                    animate={{{{ opacity: 1 }}}}
                    className="min-h-screen px-8 pt-32 pb-20"
                >
                    <div className="max-w-6xl mx-auto">
                        <h1 className="text-5xl md:text-7xl font-bold mb-12 gradient-text">Behavioral Patterns</h1>
                        <div className="grid grid-cols-1 gap-8">
                            {{patterns.map((pattern, idx) => (
                                <motion.div
                                    key={{idx}}
                                    initial={{{{ opacity: 0, y: 30 }}}}
                                    animate={{{{ opacity: 1, y: 0 }}}}
                                    transition={{{{ delay: idx * 0.1 }}}}
                                    className="glass rounded-3xl p-8 hover:scale-[1.02] transition-transform"
                                >
                                    <h2 className="text-3xl font-bold mb-4 text-accent">{{pattern.name}}</h2>
                                    <p className="text-lg opacity-90 mb-4">{{pattern.summary}}</p>
                                    {{pattern.analysis && pattern.analysis.map((para, pIdx) => (
                                        <p key={{pIdx}} className="text-base opacity-80 mb-3 leading-relaxed">{{para}}</p>
                                    ))}}
                                </motion.div>
                            ))}}
                        </div>
                    </div>
                </motion.div>
            );
        }}
        
        function AboutPage() {{
            const aboutData = CONTENT_DATA?.pages?.about || {{}};
            const introduction = aboutData.introduction || [];
            
            return (
                <motion.div
                    initial={{{{ opacity: 0 }}}}
                    animate={{{{ opacity: 1 }}}}
                    className="min-h-screen flex items-center justify-center px-8 pt-20"
                >
                    <div className="max-w-4xl">
                        <h1 className="text-5xl font-bold mb-8 gradient-text text-center">About</h1>
                        {{introduction.length > 0 ? (
                            <div className="space-y-4">
                                {{introduction.map((para, idx) => (
                                    <p key={{idx}} className="text-lg opacity-80 leading-relaxed">{{para}}</p>
                                ))}}
                            </div>
                        ) : (
                            <p className="text-xl opacity-70 text-center">Get in touch to learn more.</p>
                        )}}
                    </div>
                </motion.div>
            );
        }}
        
        function App() {{
            const [route, setRoute] = useState('home');
            
            useEffect(() => {{
                const handleHashChange = () => {{
                    const hash = window.location.hash.slice(1) || 'home';
                    setRoute(hash);
                }};
                window.addEventListener('hashchange', handleHashChange);
                handleHashChange();
                return () => window.removeEventListener('hashchange', handleHashChange);
            }}, []);
            
            useEffect(() => {{
                window.location.hash = route;
            }}, [route]);
            
            return (
                <div className="min-h-screen" style={{{{ background: '{bg_color}', color: '{text_color}' }}}}>
                    <Navigation currentRoute={{route}} setRoute={{setRoute}} />
                    <AnimatePresence mode="wait">
                        {{route === 'home' && <HomePage key="home" />}}
                        {{route === 'patterns' && <PatternsPage key="patterns" />}}
                        {{route === 'about' && <AboutPage key="about" />}}
                    </AnimatePresence>
                </div>
            );
        }}
        
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>"""
    
    print(f"[SUCCESS] React Developer generated HTML: {len(html)} characters")
    return html
