import json
import os
import re
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

# Configure for LM Studio (local)
# Lower temperature for more consistent, reliable outputs
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="local-model",
    temperature=0.3,
    max_tokens=32000
)


# ============================================================================
# PYDANTIC MODELS (For Strict JSON Validation)
# ============================================================================

# --- Mood Agent Models ---
class Colors(BaseModel):
    primary: str = Field(description="Main brand color hex code")
    secondary: str = Field(description="Secondary brand color hex code")
    accent: str = Field(description="Accent color hex code")
    background: str = Field(description="Background color hex code")
    text: str = Field(description="Main text color hex code")

class Fonts(BaseModel):
    heading: str = Field(description="Font family for headings")
    body: str = Field(description="Font family for body text")

class MoodSystem(BaseModel):
    colors: Colors
    fonts: Fonts
    layout_style: str = Field(description="Name of the visual style (e.g. Minimalist, Brutalist)")
    mood_keywords: List[str] = Field(description="3-5 keywords describing the mood")
    reasoning: str = Field(description="Brief explanation of design choices")

# --- Content Strategist Models ---
class Pattern(BaseModel):
    name: str
    summary: str
    analysis: List[str] = Field(description="3-5 paragraphs analyzing the pattern")
    evidence_quotes: List[str]

class AntiClaim(BaseModel):
    claim: str
    analysis: List[str] = Field(description="3 paragraphs explaining the boundary")
    quote: str

class Failure(BaseModel):
    title: str
    analysis: List[str] = Field(description="4 paragraphs analyzing the failure")
    key_lesson: str

class Decision(BaseModel):
    title: str
    analysis: List[str] = Field(description="4 paragraphs analyzing the decision")
    key_insight: str

class MethodStep(BaseModel):
    step_number: int
    step_name: str
    description: List[str] = Field(description="3 paragraphs describing the step")

class Method(BaseModel):
    page_title: str = Field(default="Proprietary Method")
    method_name: str = Field(default="Unique Approach")
    introduction: List[str] = Field(default_factory=list)
    steps: List[MethodStep] = Field(default_factory=list)
    when_works: List[str] = Field(default_factory=list)
    when_fails: List[str] = Field(default_factory=list)
    conclusion: List[str] = Field(default_factory=list)

class Guideline(BaseModel):
    guideline: str
    explanation: List[str]

class AboutPage(BaseModel):
    page_title: str = Field(default="Working With Me")
    introduction: List[str] = Field(default_factory=list)
    guidelines: List[Guideline] = Field(default_factory=list)
    contact_prompt: str = Field(default="Get in touch")

class HomePage(BaseModel):
    thesis: str = Field(default="Analysis in progress...")
    introduction: List[str] = Field(default_factory=lambda: ["Please wait while we analyze your profile."])
    navigation_prompt: str = Field(default="Explore the sections below")

class PatternsPage(BaseModel):
    page_title: str = Field(default="Behavioral Patterns")
    introduction: List[str] = Field(default_factory=list)
    patterns: List[Pattern] = Field(default_factory=list)

class AntiClaimsPage(BaseModel):
    page_title: str = Field(default="Boundaries & Refusals")
    introduction: List[str] = Field(default_factory=list)
    anti_claims: List[AntiClaim] = Field(default_factory=list)

class FailuresPage(BaseModel):
    page_title: str = Field(default="Failure Map")
    introduction: List[str] = Field(default_factory=list)
    failures: List[Failure] = Field(default_factory=list)

class DecisionsPage(BaseModel):
    page_title: str = Field(default="Decision Log")
    introduction: List[str] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)

class Pages(BaseModel):
    home: HomePage
    behavioral_patterns: Optional[PatternsPage] = Field(default=None)
    anti_claims: Optional[AntiClaimsPage] = Field(default=None)
    failures_and_lessons: Optional[FailuresPage] = Field(default=None)
    decision_architecture: Optional[DecisionsPage] = Field(default=None)
    proprietary_method: Optional[Method] = Field(default=None)
    about: Optional[AboutPage] = Field(default=None)

class Meta(BaseModel):
    site_title: str = Field(default="Professional Fingerprint")
    navigation_structure: List[str] = Field(default_factory=lambda: ["Home", "Patterns", "Anti-Claims", "Failures", "Decisions", "Method", "About"])

class ContentStrategy(BaseModel):
    pages: Pages
    meta: Meta

# --- UX Architect Models ---
class Navigation(BaseModel):
    type: str
    structure: List[str]
    style: str

class PageLayout(BaseModel):
    id: str
    layout: str
    components: List[str]
    typography: Dict[str, str]
    animations: List[str]
    scroll_behavior: str

class TypographySystem(BaseModel):
    custom_fonts: str
    font_scale: str = "Standard"

class AnimationStrategy(BaseModel):
    style: str = "Subtle and polished"

class UXPlan(BaseModel):
    navigation: Navigation
    pages: List[PageLayout]
    typography_system: TypographySystem
    animation_strategy: AnimationStrategy

# --- Legacy Profile Models (For Backward Compatibility) ---
class LegacyPattern(BaseModel):
    name: str
    description: str
    evidence: str

class LegacyAntiClaim(BaseModel):
    claim: str
    reasoning: str
    consequence: str

class LegacyFailure(BaseModel):
    situation: str
    decision: str
    lesson: str

class LegacyDecision(BaseModel):
    context: str
    choice: str
    outcome: str

class LegacyMethod(BaseModel):
    name: str
    steps: List[str]
    when_works: str
    when_fails: str

class LegacyFingerprint(BaseModel):
    patterns: List[LegacyPattern]
    anti_claims: List[LegacyAntiClaim]
    failure_map: List[LegacyFailure]
    decision_log: List[LegacyDecision]
    method: LegacyMethod
    working_with_me: List[str]

class LegacyMeta(BaseModel):
    name: str
    thesis: str
    social: Dict[str, str] = Field(default_factory=dict)

class LegacyProfile(BaseModel):
    meta: LegacyMeta
    fingerprint: LegacyFingerprint

# ============================================================================
# MULTI-AGENT SYSTEM (LangChain Implementation)
# ============================================================================

class OrchestratorReport(BaseModel):
    validations: Optional[List[str]] = Field(default_factory=list)
    needs_regeneration: Optional[bool] = False
    regeneration_instructions: Optional[str] = None
    design_directives: Optional[dict] = Field(default_factory=dict)
    content_adjustments: Optional[dict] = Field(default_factory=dict)
    summary: Optional[str] = ""

def orchestrator_agent(
    mood_system: dict,
    content_strategy: dict,
    ux_plan: dict,
    react_code: str,
    user_name: str,
    image_paths: list = None
) -> dict:
    """Supervise agents to ensure cohesion, design quality, and completeness.
    Now with ACTION-TAKING capability - can re-invoke agents with fixes.
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

ONLY REQUEST REGENERATION IF:
1. Critical CDN script is missing (e.g., Babel standalone)
2. CONTENT_DATA is not embedded or is empty
3. Navigation links don't work (missing routes)
4. All pages show placeholder text instead of real content

DO NOT REQUEST REGENERATION FOR:
- Minor styling issues
- Font preferences
- Animation timing
- Accessibility attributes (nice-to-have)
- Color shade variations

Return JSON only.
Fields:
- validations: array of specific checks ("✓ Babel CDN present", "✗ Missing CONTENT_DATA", etc.)
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
            "mood": json.dumps(mood_system, indent=2),
            "content": json.dumps(content_strategy, indent=2),
            "ux": json.dumps(ux_plan, indent=2),
            "code_length": len(react_code),
            "react": react_code[:2000],
            "format_instructions": parser.get_format_instructions()
        })
        data = _sanitize_json_output(raw)
        validated = OrchestratorReport.model_validate(data)
        result = validated.model_dump()
        
        # ACTION-TAKING: If regeneration is needed, do it
        # DISABLED: Orchestrator regeneration often makes things worse
        # Only enable when orchestrator is more reliable
        if False and result.get('needs_regeneration') and result.get('regeneration_instructions'):
            print(f"\n🔄 ORCHESTRATOR REQUESTING REGENERATION")
            print(f"Reason: {result.get('regeneration_instructions')}")
            
            # Re-invoke React Developer with additional instructions
            new_react_code = react_developer_agent(
                mood_system, 
                content_strategy, 
                ux_plan, 
                user_name, 
                image_paths or [],
                orchestrator_feedback=result.get('regeneration_instructions')
            )
            
            result['react_code_regenerated'] = True
            result['new_react_code'] = new_react_code
        elif result.get('needs_regeneration'):
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

def mood_agent(vibe_data: dict) -> dict:
    """
    Mood Agent: Derives a visual design system from user's vibe inputs.
    """
    parser = PydanticOutputParser(pydantic_object=MoodSystem)
    
    system_prompt = """
You are a Visual Design Strategist and Mood Analyst.
Your task is to translate abstract personal traits into a concrete design system.

DESIGN PERSONALITY MAPPING (MANDATORY - CREATE DISTINCT STYLES):
- If Color=Blue/Cold tones + Animal=Aquatic/Bird → Use: Dark blues, teals, fluid layouts, wave animations
- If Color=Red/Warm tones + Animal=Predator → Use: Bold reds/oranges, sharp angles, aggressive animations
- If Color=Green/Earth tones + Animal=Land/Plant → Use: Organic greens, rounded shapes, smooth transitions
- If Color=Purple/Pink + Animal=Mythical → Use: Gradients, ethereal effects, dreamy animations
- If Color=Black/White + Animal=Minimal → Use: Stark contrasts, geometric, Swiss/Brutalist style
- If Word=Technical/Abstract → Favor: Grid systems, monospace fonts, data viz aesthetics
- If Word=Creative/Emotional → Favor: Asymmetric layouts, script fonts, artistic flourishes
- If Word=Professional/Serious → Favor: Clean lines, serif fonts, corporate minimalism

COLOR PALETTE RULES:
- PRIMARY: Derived from favorite color (exact hue or close variant)
- SECONDARY: Complementary or analogous to primary
- ACCENT: High contrast for CTAs and highlights
- BACKGROUND: Should create mood (dark for dramatic, light for airy)
- TEXT: High contrast with background for readability

FONT PAIRING RULES:
- Heading: Choose from [Inter, Playfair Display, Space Grotesk, Syne, Archivo Black, Cormorant Garamond, JetBrains Mono]
- Body: Choose from [Inter, Lora, Work Sans, IBM Plex Sans, Source Serif Pro, DM Sans]
- NEVER use Arial, Georgia, or Times New Roman
- Ensure heading and body fonts contrast (e.g., serif heading + sans body OR vice versa)

LAYOUT STYLE OPTIONS (CHOOSE BASED ON PERSONALITY):
- Apple Minimalist: Clean, spacious, glass effects
- Swiss Brutalist: Bold typography, stark contrasts, geometric
- Editorial Magazine: Asymmetric grids, large type, image-heavy
- Tech Dashboard: Data viz, monospace, dark mode
- Creative Studio: Playful animations, color blocks, organic shapes
- Luxury Fashion: Elegant serifs, generous whitespace, refined

OUTPUT VALID JSON ONLY. NO EXPLANATIONS BEFORE OR AFTER THE JSON BLOCK.
Be OPINIONATED - make distinct, bold choices that create unique visual identities.

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Favorite Color: {color}\nSpirit Animal: {animal}\nAbstract Word: {word}")
    ])
    
    # Use string parser first to sanitize output
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "color": vibe_data.get('favorite_color', 'Unknown'),
            "animal": vibe_data.get('animal', 'Unknown'),
            "word": vibe_data.get('abstract_word', 'Unknown'),
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"[DEBUG] Mood Agent raw output length: {len(raw)} characters")
        
        try:
            data = _sanitize_json_output(raw)
            validated = MoodSystem.model_validate(data)
            return validated.model_dump()
        except Exception as inner:
            print(f"Mood Agent Validation Error: {inner}")
            print(f"[DEBUG] Raw output snippet: {raw[:500]}...")
            raise inner
    except Exception as e:
        print(f"Mood Agent Error: {e}")
        # Fallback
        return {
            "colors": {"primary": "#0071e3", "secondary": "#1d1d1f", "accent": "#2997ff", "background": "#000000", "text": "#f5f5f7"},
            "fonts": {"heading": "Inter, -apple-system, sans-serif", "body": "Inter, -apple-system, sans-serif"},
            "layout_style": "Apple Minimalist",
            "mood_keywords": ["premium", "clean", "sophisticated"],
            "reasoning": "Fallback to Apple-style default"
        }


def content_strategist_agent(context_text: str, user_answers: dict) -> dict:
    """
    Content Strategist Agent: The CENTRAL agent that decides what goes on the website.
    """
    parser = PydanticOutputParser(pydantic_object=ContentStrategy)
    
    system_prompt = """
You are a Content Strategist and Behavioral Analyst for Professional Fingerprinting.

YOUR MISSION:
Extract and curate the user's professional psyche into a comprehensive, multi-chapter thesis.
This is NOT a CV. This is NOT a portfolio. This is a deep, forensic interpretation of how they think, decide, and fail.

CRITICAL RULES:
1. DO NOT include job titles, employment timelines, or standard skill lists
2. DO NOT invent or exaggerate - use ONLY what is evident in the data
3. Generate DETAILED, MULTI-PARAGRAPH content for each section (3-5 paragraphs per insight)
4. Each paragraph must include: examples, context, reasoning, trade-offs, and concrete evidence
5. Be ruthlessly selective - choose only the MOST illustrative examples, but develop them fully
6. Write in FIRST PERSON from the user's perspective ("I", "my", "me") - this is THEIR voice
7. Keep headings CONCISE and IMPACTFUL (3-7 words max) - avoid long, academic titles
8. Vary tone per section: patterns can be analytical, failures reflective, method confident, anti-claims bold
9. Every piece of content must reveal something NON-OBVIOUS about the user
10. Plan content for MULTIPLE PAGES - each major section gets its own dedicated page
11. Break up long paragraphs with line breaks, subheadings, or bullet points for readability

OUTPUT VALID JSON ONLY. NO EXPLANATIONS BEFORE OR AFTER THE JSON BLOCK.

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "USER INTERVIEW ANSWERS:\n{answers}\n\nRAW DATA:\n{context}")
    ])
    
    # Use string parser first to sanitize output, then validate via Pydantic
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "answers": json.dumps(user_answers, indent=2),
            "context": context_text[:25000],
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"[DEBUG] Content Strategist raw output length: {len(raw)} characters")
        
        try:
            data = _sanitize_json_output(raw)
            validated = ContentStrategy.model_validate(data)
            return validated.model_dump()
        except Exception as inner:
            print(f"Content Strategist Agent Validation Error: {inner}")
            print(f"[DEBUG] Raw output snippet: {raw[:500]}...")
            # Bubble into outer except to trigger safe fallback payload
            raise inner
    except Exception as e:
        print(f"Content Strategist Agent Error: {e}")
        # Minimal fallback to prevent crash
        return {
            "pages": {
                "home": {"thesis": "Analysis failed.", "introduction": ["Please try again."], "navigation_prompt": "Retry"},
                "behavioral_patterns": {"page_title": "Patterns", "introduction": [], "patterns": []},
                "anti_claims": {"page_title": "Boundaries", "introduction": [], "anti_claims": []},
                "failures_and_lessons": {"page_title": "Failures", "introduction": [], "failures": []},
                "decision_architecture": {"page_title": "Decisions", "introduction": [], "decisions": []},
                "proprietary_method": {"page_title": "Method", "method_name": "Unknown", "introduction": [], "steps": [], "when_works": [], "when_fails": [], "conclusion": []},
                "about": {"page_title": "About", "introduction": [], "guidelines": [], "contact_prompt": "Contact"}
            },
            "meta": {"site_title": "Error", "navigation_structure": []}
        }


def content_agent(context_text: str, user_answers: dict) -> dict:
    """
    Content Agent: Structures the user's professional data into site sections.
    Input: Raw text, user answers
    Output: Structured content for Hero, About, Projects, etc.
    """
    
    system_prompt = """
You are a Content Strategist and Copywriter.
Your task is to analyze raw professional data and structure it into compelling website sections.
Generate content for: Hero, About, Expertise, Projects, and a CTA.
Tone: Bold, personal, human-first. No corporate buzzwords.
"""

    user_prompt = f"""
Analyze the following data and generate structured content for a personal website.

USER INTERVIEW ANSWERS:
{json.dumps(user_answers, indent=2)}

RAW DATA:
{context_text[:15000]}

Generate a JSON object with this structure:
{{
  "hero": {{
    "headline": "A bold, attention-grabbing headline",
    "subheadline": "Supporting tagline",
    "cta_text": "Call to action button text"
  }},
  "about": {{
    "title": "About section title",
    "paragraphs": ["Paragraph 1", "Paragraph 2"]
  }},
  "expertise": {{
    "title": "Expertise/Skills section title",
    "items": [
      {{"name": "Skill/Area 1", "description": "Brief desc"}},
      {{"name": "Skill/Area 2", "description": "Brief desc"}}
    ]
  }},
  "projects": [
    {{"title": "Project Name", "description": "What it is", "impact": "What it achieved"}},
    {{"title": "Project Name 2", "description": "What it is", "impact": "What it achieved"}}
  ],
  "cta": {{
    "headline": "Final call to action headline",
    "text": "Supporting text",
    "button": "Button text"
  }}
}}
"""
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Content Agent Error: {e}")
        return {
            "hero": {
                "headline": "Professional Portfolio",
                "subheadline": "Builder. Creator. Problem Solver.",
                "cta_text": "Get In Touch"
            },
            "about": {
                "title": "About Me",
                "paragraphs": ["Content generation failed. Using fallback."]
            },
            "expertise": {
                "title": "Expertise",
                "items": []
            },
            "projects": [],
            "cta": {
                "headline": "Let's Work Together",
                "text": "Reach out to discuss your project.",
                "button": "Contact"
            }
        }


def ux_architect_agent(mood_system: dict, content_strategy: dict, user_name: str, image_paths: list) -> dict:
    """
    UX Architect Agent: Plans the site structure, component hierarchy, and interactions.
    """
    parser = PydanticOutputParser(pydantic_object=UXPlan)
    
    system_prompt = """
You are a Senior UX Architect and Information Designer.
Your task is to design the architecture of a multi-page Professional Fingerprint website.

THIS IS NOT A STANDARD PORTFOLIO. This is a comprehensive, multi-chapter thesis on the user's professional psyche.

The Content Strategist has provided detailed, multi-paragraph content for multiple pages:
- Home/Thesis page
- Behavioral Patterns page (3-5 patterns, each with 3+ paragraphs)
- Anti-Claims page (boundaries/refusals, each with 3+ paragraphs)
- Failures & Lessons page (1-2 failures, each with 4+ paragraphs)
- Decision Architecture page (1-2 decisions, each with 5+ paragraphs)
- Proprietary Method page (step-by-step approach with examples)
- About/Contact page

Your job is to translate this multi-page content structure into a compelling visual architecture.

CRITICAL DESIGN REQUIREMENTS (APPLE-STYLE AESTHETIC):
1. FIXED HEADER navigation with links to all pages - always visible, glassmorphism effect
2. IMMERSIVE LAYOUTS - Use full-screen sections, bento-grids, and asymmetric layouts. Avoid simple centered text.
3. Consistent spacing, typography, and visual hierarchy across all pages
4. Custom fonts per user from Google Fonts (Inter, SF Pro display style)
5. RICH ANIMATIONS - Scroll-triggered reveals, parallax effects, smooth transitions.
6. Optimal reading experience: max-w-6xl containers, generous spacing, clear breaks between sections
7. Desktop-first but responsive - prioritize PC viewing experience with large visuals
8. Smooth page transitions without jarring jumps

You plan:
1. Fixed header navigation (top nav, glassmorphism)
2. Page layouts for each section (Bento grids, Split screens, Parallax)
3. Component hierarchy for displaying multi-paragraph content
4. Sophisticated animation/transition strategies
5. Typography hierarchy with custom fonts (Huge headings, clean body)
6. Reading flow with visual breaks to avoid walls of text
7. Responsive strategy ensuring nothing breaks

Focus on POLISH, CONSISTENCY, and READABILITY. This should feel like a high-end product landing page.

OUTPUT VALID JSON ONLY. NO EXPLANATIONS BEFORE OR AFTER THE JSON BLOCK.

{format_instructions}
"""
    
    image_info = ""
    if image_paths:
        image_info = f"\\nAvailable images ({len(image_paths)} files):\\n"
        for img in image_paths:
            filename = os.path.basename(img)
            image_info += f"  - {filename}\\n"
    else:
        image_info = "\\nNo images uploaded. Use abstract backgrounds or data visualizations."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Design the UX architecture for: {user_name}\n\nDESIGN SYSTEM:\n{mood_system}\n\nCONTENT STRATEGY:\n{content_strategy}\n\n{image_info}")
    ])
    
    # Use string parser first to sanitize output
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "user_name": user_name,
            "mood_system": json.dumps(mood_system, indent=2),
            "content_strategy": json.dumps(content_strategy, indent=2),
            "image_info": image_info,
            "format_instructions": parser.get_format_instructions()
        })
        
        print(f"[DEBUG] UX Architect raw output length: {len(raw)} characters")
        
        try:
            data = _sanitize_json_output(raw)
            validated = UXPlan.model_validate(data)
            return validated.model_dump()
        except Exception as inner:
            print(f"UX Architect Validation Error: {inner}")
            print(f"[DEBUG] Raw output snippet: {raw[:500]}...")
            raise inner
    except Exception as e:
        print(f"UX Architect Agent Error: {e}")
        # Minimal fallback
        return {
            "navigation": {
                "type": "fixed-top-nav",
                "structure": ["Home", "Patterns", "Anti-Claims", "Failures", "Decisions", "Method", "About"],
                "style": "Clean fixed header"
            },
            "pages": [
                {"id": "home", "layout": "centered max-w-4xl", "components": ["Hero", "Introduction"], "typography": {"heading": "text-5xl font-bold", "body": "text-lg leading-relaxed"}, "animations": ["fade-in"], "scroll_behavior": "smooth"}
            ],
            "typography_system": {
                "custom_fonts": "Inter, sans-serif",
                "font_scale": "Standard"
            },
            "animation_strategy": {
                "style": "Subtle and polished"
            }
        }


def react_developer_agent(mood_system: dict, content_strategy: dict, ux_plan: dict, user_name: str, image_paths: list, orchestrator_feedback: str = None) -> str:
    """
    React Developer Agent: Writes a complete single-file React app for Professional Fingerprinting.
    Can receive feedback from Orchestrator for regeneration.
    """
    from langchain_core.output_parsers import StrOutputParser
    
    system_prompt = """
You are an Elite React Developer and Creative Technologist specializing in Awwwards-winning, Apple-style websites.
Your task is to write a complete, production-ready single-file React application for a Professional Fingerprint site.

THE GOAL: Create a site that feels like an Apple product landing page.
- IMMERSIVE: Full-screen sections, huge typography, deep blacks or crisp whites.
- INTERACTIVE: Everything should feel alive. Scroll animations, hover effects, parallax.
- POLISHED: Perfect spacing, glassmorphism, subtle gradients, high-end feel.

CRITICAL: YOU MUST USE ALL THE CONTENT DATA PROVIDED IN CONTENT_STRATEGY.
- The CONTENT_STRATEGY JSON contains all the text content for every page
- Extract data from content_strategy.pages.home, content_strategy.pages.behavioral_patterns, etc.
- DO NOT leave pages empty - populate them with the actual content from the JSON
- Each page should display its introduction, patterns, failures, decisions, method steps, etc.

CONTENT MAPPING (MANDATORY):
1. HOME PAGE: Use content_strategy.pages.home.thesis and content_strategy.pages.home.introduction
2. PATTERNS PAGE: Use content_strategy.pages.behavioral_patterns.patterns array (each has name, summary, analysis, evidence_quotes)
3. ANTI-CLAIMS PAGE: Use content_strategy.pages.anti_claims.anti_claims array (each has claim, analysis, quote)
4. FAILURES PAGE: Use content_strategy.pages.failures_and_lessons.failures array (each has title, analysis, key_lesson)
5. DECISIONS PAGE: Use content_strategy.pages.decision_architecture.decisions array (each has title, analysis, key_insight)
6. METHOD PAGE: Use content_strategy.pages.proprietary_method (method_name, steps array, when_works, when_fails)
7. ABOUT PAGE: Use content_strategy.pages.about (guidelines array with guideline and explanation)

TECHNICAL REQUIREMENTS (Desktop-first, premium feel):
- Use React 18 via CDN (unpkg)
- Use Tailwind CSS via CDN
- Use Framer Motion via CDN for animations
- Use Google Fonts via CDN (Inter, SF Pro Display equivalent)
- Use HASH-BASED ROUTING for multi-page navigation (e.g., #/patterns, #/failures)
- Everything in ONE HTML file (React code in inline script)
- Use modern React (hooks, functional components, useState for routing)
- Implement FIXED HEADER navigation - glassmorphism (backdrop-blur-md bg-white/70 or bg-black/70)
- Use SOPHISTICATED animations - staggerChildren, parallax, smooth reveals
- Follow the design system colors/fonts EXACTLY but elevate them with gradients/transparency
- Prioritize desktop experience: use the full width (max-w-7xl), grid layouts, bento grids
- Use proper semantic HTML
- Include smooth scroll behavior within pages
- Support browser back/forward buttons with hash navigation
- Ensure NOTHING is misaligned or broken - test layout carefully

CDN SETUP (CRITICAL - COPY EXACTLY):
```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/framer-motion@10/dist/framer-motion.js"></script>
```

REACT SCRIPT STRUCTURE (CRITICAL):
```html
<script type="text/babel">
const {{ motion, AnimatePresence, useScroll, useTransform }} = window.Motion;  // Declare INSIDE the babel script
const {{ useState, useEffect, useRef }} = React;

// EMBED CONTENT DATA AS A CONSTANT (MANDATORY)
const CONTENT_DATA = {{content_strategy_json_here}};

// Build components that READ from CONTENT_DATA
// Example: CONTENT_DATA.pages.home.thesis, CONTENT_DATA.pages.behavioral_patterns.patterns, etc.

// Your components here...
</script>
```

DESIGN GUIDELINES (APPLE STYLE):
1. **Typography**: Use `tracking-tight` for headings. Huge sizes (`text-6xl` to `text-9xl`).
2. **Glassmorphism**: Use `backdrop-blur-xl bg-white/10` (or black) for cards and nav.
3. **Bento Grids**: Use `grid grid-cols-1 md:grid-cols-3 gap-6` for content cards.
4. **Gradients**: Use subtle mesh gradients as backgrounds or text gradients (`bg-clip-text text-transparent bg-gradient-to-r`).
5. **Spacing**: Huge padding (`py-32`, `py-40`). Let content breathe.
6. **Images**: Large, high-quality, with `rounded-3xl` and subtle shadows (`shadow-2xl`).
7. **Interactive**: Buttons should scale down slightly on click (`whileTap={{ scale: 0.95 }}`). Cards should lift on hover (`whileHover={{ y: -10 }}`).

LAYOUT REQUIREMENTS (CRITICAL):
- FIXED HEADER navigation - always visible at top (sticky top-0 z-50)
- Hero uses full-bleed gradient background with subtle noise overlay
- Centered content: max-w-7xl mx-auto for all pages (desktop)
- Generous padding: py-32 px-10 for main content areas (desktop)
- Clear section breaks: mb-32 between major sections
- Display ALL paragraphs in analysis arrays - these are multi-paragraph essays
- NEVER allow misaligned, broken, or "spaghettified" layouts
- Test responsive breakpoints to ensure nothing breaks

IMAGE HANDLING:
- Reference images as: ./assets/filename.jpg
- If no images, use abstract CSS shapes or gradients.

Generate ONLY the complete HTML file. No explanations. No markdown code blocks. Just raw HTML.
The HTML must be valid and ready to run in a browser.
"""

    image_list = []
    if image_paths:
        for img in image_paths:
            filename = os.path.basename(img)
            image_list.append(f"assets/{filename}")

    feedback_section = f"\n\nORCHESTRATOR FEEDBACK (MUST ADDRESS):\n{orchestrator_feedback}\n" if orchestrator_feedback else ""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", """Generate React App for: {user_name}

DESIGN SYSTEM:
{mood_system}

CONTENT STRATEGY (USE THIS DATA TO POPULATE ALL PAGES):
{content_strategy}

UX ARCHITECTURE:
{ux_plan}

AVAILABLE IMAGES:
{image_list}
{feedback}

CRITICAL REMINDER: 
- Embed the CONTENT_STRATEGY JSON as a constant in your React code
- Map each route to display content from CONTENT_DATA.pages
- DO NOT leave pages blank - they must show the actual content
- Example: For the Patterns page, iterate over CONTENT_DATA.pages.behavioral_patterns.patterns and display each pattern's name, summary, analysis paragraphs, and quotes""")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        # Log content summary for debugging
        pages_info = content_strategy.get('pages', {})
        print(f"[DEBUG] React Dev Agent - Content pages available:")
        for page_key, page_data in pages_info.items():
            if page_data:
                print(f"  - {page_key}: {type(page_data).__name__}")
        
        html_content = chain.invoke({
            "user_name": user_name,
            "mood_system": json.dumps(mood_system, indent=2),
            "content_strategy": json.dumps(content_strategy, indent=2),
            "ux_plan": json.dumps(ux_plan, indent=2),
            "image_list": json.dumps(image_list, indent=2) if image_list else "[]",
            "feedback": feedback_section
        })
        
        print(f"[DEBUG] React Developer generated HTML: {len(html_content)} characters")
        
        # Validate essential CDN scripts are present
        required_cdns = [
            ('react@18/umd/react.production.min.js', 'React'),
            ('react-dom@18/umd/react-dom.production.min.js', 'ReactDOM'),
            ('@babel/standalone/babel.min.js', 'Babel'),
            ('cdn.tailwindcss.com', 'Tailwind'),
            ('framer-motion', 'Framer Motion')
        ]
        
        missing_cdns = []
        for cdn_url, name in required_cdns:
            if cdn_url not in html_content:
                missing_cdns.append(name)
        
        if missing_cdns:
            print(f"[WARNING] Missing CDN scripts: {', '.join(missing_cdns)}")
            print("[INFO] Attempting to add missing CDN scripts...")
            
            # Add missing scripts to head
            cdn_scripts = ""
            if 'React' in missing_cdns:
                cdn_scripts += '<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>\n    '
            if 'ReactDOM' in missing_cdns:
                cdn_scripts += '<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>\n    '
            if 'Babel' in missing_cdns:
                cdn_scripts += '<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>\n    '
            if 'Tailwind' in missing_cdns:
                cdn_scripts += '<script src="https://cdn.tailwindcss.com"></script>\n    '
            if 'Framer Motion' in missing_cdns:
                cdn_scripts += '<script src="https://unpkg.com/framer-motion@10/dist/framer-motion.js"></script>\n    '
            
            # Insert before </head>
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', f'{cdn_scripts}</head>')
                print(f"[INFO] Added missing CDN scripts")
        
        # Clean up markdown code blocks if present
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
        
        # Fix common errors
        # Remove standalone motion declaration script tags
        import re
        html_content = re.sub(r'<script>\s*const\s*{\s*motion\s*}\s*=\s*window\.Motion;\s*</script>', '', html_content)
        html_content = re.sub(r"<script>\s*const\s*{\s*motion\s*}\s*=\s*window\['framer-motion'\];\s*</script>", '', html_content)
        
        # Fix Framer Motion access patterns
        html_content = html_content.replace("window['framer-motion']", "window.Motion")
        html_content = html_content.replace('window["framer-motion"]', "window.Motion")
        
        # CRITICAL: Fix malformed JavaScript object syntax
        # Replace ],[ with proper comma separation ], 
        # This catches errors like: prop1:[...]],[prop2:[...]]
        html_content = re.sub(r'\],\s*\[', '], ', html_content)
        
        # Ensure motion is declared inside the babel script
        # Check if motion is already declared (including destructuring like { motion, useAnimation })
        babel_script_content = ""
        if 'type="text/babel"' in html_content:
            parts = html_content.split('type="text/babel"')
            if len(parts) > 1:
                babel_script_content = parts[1].split('</script>')[0]
        
        motion_declared = re.search(r'const\s*{[^}]*motion[^}]*}\s*=\s*window\.Motion', babel_script_content)
        
        if 'type="text/babel"' in html_content and not motion_declared:
            # Add motion declaration at the start of the babel script
            html_content = html_content.replace(
                '<script type="text/babel">',
                '<script type="text/babel">\nconst { motion } = window.Motion;\n'
            )
        
        # Fix ReactDOM render method for React 18
        if "ReactDOM.render(" in html_content and "createRoot" not in html_content:
            html_content = html_content.replace(
                "ReactDOM.render(<App/>",
                "ReactDOM.createRoot(document.getElementById('root')).render(<App/>"
            )
            html_content = html_content.replace(
                "ReactDOM.render(<App />",
                "ReactDOM.createRoot(document.getElementById('root')).render(<App />"
            )
            
        return html_content
    except Exception as e:
        print(f"React Developer Agent Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Enhanced fallback React template with working setup
        primary_color = mood_system.get('colors', {}).get('primary', '#0071e3')
        secondary_color = mood_system.get('colors', {}).get('secondary', '#1d1d1f')
        accent_color = mood_system.get('colors', {}).get('accent', '#2997ff')
        bg_color = mood_system.get('colors', {}).get('background', '#000000')
        text_color = mood_system.get('colors', {}).get('text', '#f5f5f7')
        
        heading_font = mood_system.get('fonts', {}).get('heading', 'Inter, sans-serif')
        body_font = mood_system.get('fonts', {}).get('body', 'Inter, sans-serif')
        
        # Extract content from strategy
        pages = content_strategy.get('pages', {})
        home_page = pages.get('home', {})
        patterns_page = pages.get('behavioral_patterns', {})
        
        hero_headline = home_page.get('thesis', 'Portfolio')[:80]
        hero_intro = home_page.get('introduction', ['Professional Portfolio'])
        hero_subheadline = hero_intro[0][:120] if hero_intro else 'Professional Portfolio'
        
        # Get pattern count for nav
        patterns_count = len(patterns_page.get('patterns', [])) if patterns_page else 0
        
        return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_name} - Portfolio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/framer-motion@10/dist/framer-motion.js"></script>
    <style>
        * {{
            font-family: {body_font};
        }}
        body {{ 
            background: {bg_color}; 
            color: {text_color};
            margin: 0;
            padding: 0;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: {heading_font};
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .gradient-text {{
            background: linear-gradient(135deg, {primary_color}, {accent_color});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const {{ motion, AnimatePresence }} = window.Motion;
        const {{ useState, useEffect }} = React;
        
        // Embed actual content data
        const CONTENT_DATA = {json.dumps(content_strategy, indent=2)};
        
        function Navigation({{ currentRoute, setRoute }}) {{
            const navItems = [
                {{ id: 'home', label: 'Home' }},
                {{ id: 'patterns', label: 'Patterns', count: {patterns_count} }},
                {{ id: 'about', label: 'About' }}
            ];
            
            return (
                <nav className="fixed top-0 left-0 right-0 z-50 glass">
                    <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
                        <div className="text-xl font-bold">{user_name}</div>
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
                                    <h2 className="text-3xl font-bold mb-4" style={{{{ color: '{accent_color}' }}}}>{pattern.name}</h2>
                                    <p className="text-lg opacity-90 mb-4">{pattern.summary}</p>
                                    {{pattern.analysis && pattern.analysis.map((para, pIdx) => (
                                        <p key={{pIdx}} className="text-base opacity-80 mb-3 leading-relaxed">{para}</p>
                                    ))}}
                                </motion.div>
                            ))}}
                        </div>
                    </div>
                </motion.div>
            );
        }}
        
        function AboutPage() {{
            return (
                <motion.div
                    initial={{{{ opacity: 0 }}}}
                    animate={{{{ opacity: 1 }}}}
                    className="min-h-screen flex items-center justify-center px-8 pt-20"
                >
                    <div className="max-w-4xl text-center">
                        <h1 className="text-5xl font-bold mb-8 gradient-text">About</h1>
                        <p className="text-xl opacity-80">Get in touch to learn more.</p>
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


# ============================================================================
# LEGACY DESIGN AGENT (kept for reference)
# ============================================================================

def design_agent_legacy(mood_system: dict, content_data: dict, user_name: str) -> str:
    """
    Design Agent: Generates complete HTML/CSS code for the site.
    Input: Design system from Mood Agent + Content from Content Agent
    Output: Complete HTML string
    """
    
    system_prompt = """
You are an Expert Frontend Developer and Creative Technologist.
Your task is to generate a complete, modern, single-page HTML website with embedded CSS.
Requirements:
- Fully responsive design
- Modern CSS (flexbox, grid, animations)
- No JavaScript unless absolutely necessary
- Beautiful typography and spacing
- Smooth animations and transitions
- The design MUST reflect the mood/style provided
- All CSS should be in a <style> tag in the <head>
- Use semantic HTML5
- Include meta tags for SEO and social sharing

Generate ONLY the HTML code. No explanations. No markdown. Just raw HTML.
"""

    user_prompt = f"""
Generate a complete single-page HTML website for: {user_name}

DESIGN SYSTEM:
{json.dumps(mood_system, indent=2)}

CONTENT STRUCTURE:
{json.dumps(content_data, indent=2)}

The website should have these sections:
1. Hero (full-screen, bold, attention-grabbing)
2. About (personal story, 2-3 paragraphs)
3. Expertise/Skills (grid or list of capabilities)
4. Projects (showcase 2-3 key projects)
5. CTA/Contact (footer with call to action)

Design requirements:
- Use the color palette EXACTLY as provided
- Apply the fonts specified
- Reflect the layout_style in the structure (e.g., if "Brutalist", use bold borders and asymmetric layouts)
- Add smooth scroll behavior
- Include hover effects on interactive elements
- Make it visually stunning and unique

Generate the complete HTML now:
"""
    
    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        html_content = response.choices[0].message.content
        
        # Clean up markdown code blocks if present
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
            
        return html_content
    except Exception as e:
        print(f"Design Agent Error: {e}")
        # Fallback minimal HTML
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_name} - Portfolio</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: sans-serif; background: #f0f0f0; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>{user_name}</h1>
    <p>Site generation encountered an error. Please try again.</p>
</body>
</html>"""


# ============================================================================
# LEGACY CONTENT AGENT (kept for backward compatibility)
# ============================================================================

SYSTEM_PROMPT = """
You are a Professional Profiler and Behavioral Analyst.
Your task is to construct a 'Professional Fingerprint'—a structural analysis of the user's professional psyche.
You must NOT generate a CV, a Resume, or a standard Portfolio.
You must generate a "Thesis" on the professional, focusing on how they think, decide, and fail.

You must identify:
1. Behavioral Patterns: 5-7 recurring habits or themes.
2. Anti-Claims: 4-6 things the person is NOT good at or refuses to do (Boundaries).
3. Failure Map: 3 real or implied failures, analyzing the decision and the lesson.
4. Decision Log: 3 key decisions, showing options, trade-offs, and impact.
5. Proprietary Method: A unique 3-5 step method derived from their way of working.

Tone: Assertive, analytical, "Human First", no buzzwords.
"""

def _sanitize_json_output(content: str) -> dict:
    """Best-effort extractor to parse JSON from noisy LLM output."""
    try:
        # Try direct parse first
        return json.loads(content)
    except Exception:
        pass
    
    # Strip markdown code blocks
    cleaned = content
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # Strip known LM Studio/Chat markers and extract JSON block
    for marker in ["<|channel|>", "<|constrain|>", "<|message|>", "<|im_start|>", "<|im_end|>"]:
        cleaned = cleaned.replace(marker, "")
    
    # Find first '{' and last '}' to isolate JSON
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass
    
    # As last resort, raise to caller
    raise ValueError(f"Could not extract valid JSON from LLM output. First 200 chars: {content[:200]}")

def analyze_profile(context_text: str, user_answers: dict) -> dict:
    """
    Legacy Profile Analyzer: Generates the 'Professional Fingerprint' structure.
    Refactored to use LangChain and Pydantic for stability.
    """
    parser = PydanticOutputParser(pydantic_object=LegacyProfile)
    
    system_prompt = """
You are a Professional Profiler and Behavioral Analyst.
Your task is to construct a 'Professional Fingerprint'—a structural analysis of the user's professional psyche.
You must NOT generate a CV, a Resume, or a standard Portfolio.
You must generate a "Thesis" on the professional, focusing on how they think, decide, and fail.

You must identify:
1. Behavioral Patterns: 5-7 recurring habits or themes.
2. Anti-Claims: 4-6 things the person is NOT good at or refuses to do (Boundaries).
3. Failure Map: 3 real or implied failures, analyzing the decision and the lesson.
4. Decision Log: 3 key decisions, showing options, trade-offs, and impact.
5. Proprietary Method: A unique 3-5 step method derived from their way of working.

Tone: Assertive, analytical, "Human First", no buzzwords.

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "USER INTERVIEW ANSWERS:\n{answers}\n\nRAW DATA:\n{context}")
    ])
    
    # Use string parser first to sanitize output, then validate via Pydantic
    chain = prompt | llm | StrOutputParser()
    
    try:
        raw = chain.invoke({
            "answers": json.dumps(user_answers, indent=2),
            "context": context_text[:20000],
            "format_instructions": parser.get_format_instructions()
        })
        try:
            data = _sanitize_json_output(raw)
            validated = LegacyProfile.model_validate(data)
            return validated.model_dump()
        except Exception as inner:
            # Bubble into outer except to trigger safe fallback payload
            raise inner
    except Exception as e:
        print(f"Analyze Profile Error: {e}")
        return {
            "meta": {
                "name": "Unknown Analyst",
                "thesis": "Data insufficient for thesis generation.",
                "social": {}
            },
            "fingerprint": {
                "patterns": [{"name": "Error", "description": "LLM Connection Failed", "evidence": "N/A"}],
                "anti_claims": [],
                "failure_map": [],
                "decision_log": [],
                "method": {"name": "N/A", "steps": [], "when_works": "", "when_fails": ""},
                "working_with_me": []
            }
        }
