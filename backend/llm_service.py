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
    navigation_prompt: str = Field(default="Explore the sections above")

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

class IconSuggestion(BaseModel):
    location: str = Field(description="Where to place the icon (e.g., 'navigation', 'hero', 'pattern-card')")
    icon_name: str = Field(description="Icon name from the library")
    purpose: str = Field(description="Why this icon fits the content")

class IconStrategy(BaseModel):
    icon_library: str = Field(description="Icon library to use (lucide-react, heroicons, phosphor)")
    cdn_url: str = Field(description="CDN URL for the icon library")
    color_scheme: str = Field(description="How icons should be colored (accent, gradient, monochrome)")
    suggestions: List[IconSuggestion] = Field(description="Specific icon placements")
    usage_philosophy: str = Field(description="Overall approach to icon usage (minimal, decorative, functional)")

class OrchestratorReport(BaseModel):
    validations: Optional[List[str]] = Field(default_factory=list)
    needs_regeneration: Optional[bool] = False
    regeneration_instructions: Optional[str] = None
    design_directives: Optional[dict] = Field(default_factory=dict)
    content_adjustments: Optional[dict] = Field(default_factory=dict)
    summary: Optional[str] = ""

def icon_curator_agent(mood_system: dict, content_strategy: dict, ux_plan: dict, user_name: str) -> dict:
    """
    Icon Curator Agent: Selects appropriate icons to enhance visual design.
    Suggests tasteful icon placement without overwhelming the design.
    """
    parser = PydanticOutputParser(pydantic_object=IconStrategy)
    
    system_prompt = """
You are an Icon Curator and Visual Enhancement Specialist.
Your task is to select tasteful, meaningful icons that enhance the visual design.

PRINCIPLES:
1. LESS IS MORE - Icons should enhance, not clutter (3-8 icons total)
2. MEANINGFUL - Each icon must relate to its content
3. CONSISTENT - Use ONE icon library throughout
4. SUBTLE - Icons complement the design system, don't overpower it

ICON LIBRARIES (choose ONE):
- Lucide Icons: Modern, clean, minimal (RECOMMENDED for most designs)
- Heroicons: Apple-style, outlined (great for tech/minimal)
- Phosphor Icons: Playful, varied weights (good for creative)
- Feather Icons: Super minimal (good for brutalist/clean)

PLACEMENT STRATEGY:
- Navigation: Small icons next to menu items (optional, only if adds value)
- Section Headers: Decorative icons for major sections (Patterns, Failures, etc.)
- Feature Cards: Icons to represent each pattern/skill
- Hero: ONE subtle decorative icon (optional)
- Footer/About: Contact/social icons

ICON SELECTION RULES:
- Match content meaning (e.g., 🎯 for goals, 🧩 for patterns, ⚡ for decisions)
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
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        # Create simplified content structure for token efficiency
        pages = content_strategy.get('pages', {})
        content_structure = {
            'sections': list(pages.keys()),
            'pattern_count': len(pages.get('behavioral_patterns', {}).get('patterns', [])),
            'has_failures': bool(pages.get('failures_and_lessons')),
            'has_decisions': bool(pages.get('decision_architecture')),
            'style': mood_system.get('layout_style', 'Unknown')
        }
        
        raw = chain.invoke({
            "user_name": user_name,
            "mood_system": json.dumps(mood_system, indent=2),
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
        # Fallback with Lucide Icons
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
    NOW DETERMINISTIC - Uses hash-based selection for consistent, diverse results.
    This eliminates LLM unreliability while ensuring unique designs for each user.
    """
    import hashlib
    
    # Create a deterministic hash from user inputs
    vibe_string = f"{vibe_data.get('favorite_color', 'blue')}{vibe_data.get('animal', 'wolf')}{vibe_data.get('abstract_word', 'flow')}"
    vibe_hash = int(hashlib.md5(vibe_string.encode()).hexdigest(), 16)
    
    # Deterministic color palettes (12 distinct palettes)
    color_palettes = [
        {"primary": "#0071e3", "secondary": "#1d1d1f", "accent": "#2997ff", "background": "#000000", "text": "#f5f5f7"},  # Apple Blue
        {"primary": "#FF6B6B", "secondary": "#4ECDC4", "accent": "#FFE66D", "background": "#1A1A2E", "text": "#EAEAEA"},  # Vibrant
        {"primary": "#6C5CE7", "secondary": "#A29BFE", "accent": "#FD79A8", "background": "#2D3436", "text": "#DFE6E9"},  # Purple Dream
        {"primary": "#00B894", "secondary": "#00CEC9", "accent": "#FDCB6E", "background": "#0A0E27", "text": "#F8F9FA"},  # Ocean
        {"primary": "#E17055", "secondary": "#FDCB6E", "accent": "#74B9FF", "background": "#FAF3E0", "text": "#2D3436"},  # Warm Earth
        {"primary": "#FF3838", "secondary": "#FF6348", "accent": "#FFC048", "background": "#F5F5F5", "text": "#1E272E"},  # Bold Red
        {"primary": "#3742FA", "secondary": "#5352ED", "accent": "#FF6348", "background": "#FFFFFF", "text": "#2F3542"},  # Clean Blue
        {"primary": "#2ECC71", "secondary": "#27AE60", "accent": "#F39C12", "background": "#ECF0F1", "text": "#2C3E50"},  # Fresh Green
        {"primary": "#E91E63", "secondary": "#9C27B0", "accent": "#00BCD4", "background": "#1C1C1C", "text": "#FFFFFF"},  # Neon Pink
        {"primary": "#FF9500", "secondary": "#FF5722", "accent": "#4CAF50", "background": "#FAFAFA", "text": "#212121"},  # Orange Burst
        {"primary": "#607D8B", "secondary": "#455A64", "accent": "#FF5722", "background": "#ECEFF1", "text": "#263238"},  # Industrial
        {"primary": "#1DE9B6", "secondary": "#00E676", "accent": "#FFEA00", "background": "#121212", "text": "#E0E0E0"}   # Cyber Green
    ]
    
    # Deterministic font pairings (10 distinct pairings)
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
    
    # Deterministic layout styles
    layout_styles = [
        "Apple Minimalist",
        "Swiss Brutalist",
        "Editorial Magazine",
        "Tech Dashboard",
        "Creative Studio",
        "Luxury Fashion",
        "Cyberpunk",
        "Academic Clean",
        "Startup Modern",
        "Artistic Portfolio"
    ]
    
    # Select based on hash
    palette = color_palettes[vibe_hash % len(color_palettes)]
    fonts = font_pairings[vibe_hash % len(font_pairings)]
    layout_style = layout_styles[vibe_hash % len(layout_styles)]
    
    # Generate mood keywords based on inputs
    mood_keywords = [
        vibe_data.get('favorite_color', 'balanced').lower(),
        vibe_data.get('animal', 'adaptive').lower(),
        layout_style.split()[0].lower()
    ]
    
    print(f"[DETERMINISTIC] Selected palette #{vibe_hash % len(color_palettes)}, fonts #{vibe_hash % len(font_pairings)}, style: {layout_style}")
    print(f"[MOOD] Colors: {palette['primary']} (primary), {palette['accent']} (accent)")
    print(f"[MOOD] Fonts: {fonts['heading']} / {fonts['body']}")
    
    return {
        "colors": palette,
        "fonts": fonts,
        "layout_style": layout_style,
        "mood_keywords": mood_keywords,
        "reasoning": f"Deterministically selected based on user vibe inputs (hash: {vibe_hash % 1000})"
    }

def selenium_validator_agent(url: str, max_runtime_sec: int = 180) -> dict:
    """
    Fast, reliable Selenium validation that works with localhost.
    - Headless Chrome, aggressive performance flags
    - Short explicit waits, overall max runtime guard
    - Validates navigation and all links quickly (requests fallback)
    """
    import time
    from urllib.parse import urljoin, urlparse
    issues = []
    start = time.time()
    report = {"success": False, "validation_skipped": False, "issues": issues}
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        import requests

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--blink-settings=imagesEnabled=false")
        opts.add_argument("--disable-features=PaintHolding")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--hide-scrollbars")
        opts.page_load_strategy = "none"

        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(8)
        driver.set_script_timeout(6)
        wait = WebDriverWait(driver, 6)

        driver.get(url)
        # Wait for root to exist
        try:
            wait.until(EC.presence_of_element_located((By.ID, "root")))
        except Exception:
            issues.append("Root element not found")

        # Quick React render check
        try:
            wait.until(lambda d: d.execute_script("return !!document.getElementById('root') && document.getElementById('root').children.length > 0"))
        except Exception:
            issues.append("Root has no rendered children")

        # Collect links fast
        anchors = driver.find_elements(By.TAG_NAME, "a")
        base = url
        checked = 0
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Validator)"})

        def quick_check(href: str) -> None:
            nonlocal issues
            if time.time() - start > max_runtime_sec:
                return
            if not href:
                issues.append("Empty href found")
                return
            full = urljoin(base, href)
            parsed = urlparse(full)
            # Hash routes are internal; simulate
            if parsed.fragment:
                try:
                    driver.execute_script(f"window.location.hash='{parsed.fragment}'")
                    time.sleep(0.25)
                except Exception:
                    issues.append(f"Failed to navigate hash {parsed.fragment}")
                return
            # For localhost/http links, do a fast HEAD then GET fallback
            try:
                resp = session.head(full, timeout=2, allow_redirects=True)
                if resp.status_code >= 400:
                    resp = session.get(full, timeout=3, allow_redirects=True)
                if resp.status_code >= 400:
                    issues.append(f"Broken link {full} status {resp.status_code}")
            except Exception as e:
                issues.append(f"Error fetching {full}: {e}")

        for a in anchors:
            if time.time() - start > max_runtime_sec:
                break
            href = a.get_attribute("href") or a.get_attribute("data-href") or a.get_attribute("onclick")
            # Skip mailto/tel
            if href and (href.startswith("mailto:") or href.startswith("tel:")):
                continue
            quick_check(href)
            checked += 1
            if checked >= 50:
                break  # keep it fast

        # Basic console error check
        try:
            logs = driver.get_log("browser")
            for entry in logs:
                if "Error" in entry.get("message", ""):
                    issues.append("Console error: " + entry.get("message", ""))
        except Exception:
            pass

        driver.quit()
        report["success"] = len(issues) == 0
        report["issues"] = issues
        return report
    except Exception as e:
        report["validation_skipped"] = True
        issues.append(f"Selenium error: {e}")
        return report


def content_strategist_agent(context_text: str, user_answers: dict) -> dict:
    """
    Content Strategist Agent: The CENTRAL agent that decides what goes on the website.
    Now with retry logic for reliability.
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

EXAMPLE OUTPUT STRUCTURE (follow this EXACTLY):
{{
  "pages": {{
    "home": {{
      "thesis": "Your one-sentence thesis here",
      "introduction": ["Paragraph 1", "Paragraph 2"],
      "navigation_prompt": "Explore the sections above"
    }},
    "behavioral_patterns": {{
      "page_title": "Behavioral Patterns",
      "introduction": ["Intro paragraph"],
      "patterns": [
        {{
          "name": "Pattern Name",
          "summary": "Brief summary",
          "analysis": ["Para 1", "Para 2", "Para 3"],
          "evidence_quotes": ["Quote 1", "Quote 2"]
        }}
      ]
    }}
  }},
  "meta": {{
    "site_title": "User Name - Professional Fingerprint",
    "navigation_structure": ["Home", "Patterns", "Anti-Claims", "Failures", "Decisions", "Method", "About"]
  }}
}}

{format_instructions}
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "USER INTERVIEW ANSWERS:\n{answers}\n\nRAW DATA:\n{context}")
    ])
    
    # Use string parser first to sanitize output, then validate via Pydantic
    chain = prompt | llm | StrOutputParser()
    
    # Retry logic with increasing temperature
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Adjust temperature for retries
            temp = 0.3 + (attempt * 0.1)  # 0.3, 0.4, 0.5
            retry_llm = ChatOpenAI(
                base_url="http://localhost:1234/v1",
                api_key="lm-studio",
                model="local-model",
                temperature=temp,
                max_tokens=32000
            )
            retry_chain = prompt | retry_llm | StrOutputParser()
            
            raw = retry_chain.invoke({
                "answers": json.dumps(user_answers, indent=2),
                "context": context_text[:25000],
                "format_instructions": parser.get_format_instructions()
            })
            
            print(f"[DEBUG] Content Strategist attempt {attempt + 1}, raw output length: {len(raw)} characters")
            
            try:
                data = _sanitize_json_output(raw)
                
                # STRUCTURE VALIDATION & AUTO-CORRECTION
                # Ensure the data has the required top-level structure
                if not isinstance(data, dict):
                    raise ValueError("Parsed data is not a dictionary")
                
                # Fix missing 'pages' or 'meta' fields
                if 'pages' not in data and 'meta' not in data:
                    # LLM might have returned just the pages content directly
                    # Try to detect if this looks like pages content
                    if any(key in data for key in ['home', 'behavioral_patterns', 'anti_claims', 'failures_and_lessons', 'decision_architecture', 'proprietary_method', 'about']):
                        print("[FIX] Detected pages content at top level, wrapping in proper structure")
                        data = {
                            'pages': data,
                            'meta': {
                                'site_title': user_answers.get('who_are_you', 'Professional Fingerprint'),
                                'navigation_structure': ['Home', 'Patterns', 'Anti-Claims', 'Failures', 'Decisions', 'Method', 'About']
                            }
                        }
                    # Or it might be just the home page content
                    elif 'thesis' in data or 'introduction' in data:
                        print("[FIX] Detected home page content at top level, creating full structure")
                        data = {
                            'pages': {
                                'home': data,
                                'behavioral_patterns': {'page_title': 'Patterns', 'introduction': [], 'patterns': []},
                                'anti_claims': {'page_title': 'Boundaries', 'introduction': [], 'anti_claims': []},
                                'failures_and_lessons': {'page_title': 'Failures', 'introduction': [], 'failures': []},
                                'decision_architecture': {'page_title': 'Decisions', 'introduction': [], 'decisions': []},
                                'proprietary_method': {'page_title': 'Method', 'method_name': 'Approach', 'introduction': [], 'steps': [], 'when_works': [], 'when_fails': [], 'conclusion': []},
                                'about': {'page_title': 'About', 'introduction': [], 'guidelines': [], 'contact_prompt': 'Contact'}
                            },
                            'meta': {
                                'site_title': user_answers.get('who_are_you', 'Professional Fingerprint'),
                                'navigation_structure': ['Home', 'About']
                            }
                        }
                
                # Ensure 'pages' exists and has required structure
                if 'pages' not in data:
                    print("[FIX] Adding missing 'pages' field")
                    data['pages'] = {
                        'home': {'thesis': 'Analysis in progress', 'introduction': ['Generating content...'], 'navigation_prompt': 'Explore'}
                    }
                
                # Ensure 'meta' exists
                if 'meta' not in data:
                    print("[FIX] Adding missing 'meta' field")
                    data['meta'] = {
                        'site_title': user_answers.get('who_are_you', 'Professional Fingerprint'),
                        'navigation_structure': list(data.get('pages', {}).keys())
                    }
                
                # Ensure 'pages' has at least 'home'
                if 'home' not in data.get('pages', {}):
                    print("[FIX] Adding missing 'home' page")
                    data['pages']['home'] = {
                        'thesis': 'Analysis in progress',
                        'introduction': ['Generating content...'],
                        'navigation_prompt': 'Explore the sections'
                    }
                
                validated = ContentStrategy.model_validate(data)
                print(f"[SUCCESS] Content Strategist succeeded on attempt {attempt + 1}")
                return validated.model_dump()
            except Exception as inner:
                print(f"[WARN] Content Strategist validation failed on attempt {attempt + 1}: {inner}")
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying with temperature {temp + 0.1}...")
                    continue
                else:
                    raise inner
        except Exception as e:
            print(f"[ERROR] Content Strategist attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                # Final fallback
                print(f"[FALLBACK] Using minimal fallback after {max_retries} attempts")
                break
    
    # Minimal fallback to prevent crash
    return {
        "pages": {
            "home": {"thesis": "Analysis in progress. Please try again.", "introduction": ["Generating content..."], "navigation_prompt": "Explore"},
            "behavioral_patterns": {"page_title": "Patterns", "introduction": ["Analyzing patterns..."], "patterns": []},
            "anti_claims": {"page_title": "Boundaries", "introduction": ["Identifying boundaries..."], "anti_claims": []},
            "failures_and_lessons": {"page_title": "Failures", "introduction": ["Mapping failures..."], "failures": []},
            "decision_architecture": {"page_title": "Decisions", "introduction": ["Analyzing decisions..."], "decisions": []},
            "proprietary_method": {"page_title": "Method", "method_name": "Approach", "introduction": ["Defining method..."], "steps": [], "when_works": [], "when_fails": [], "conclusion": []},
            "about": {"page_title": "About", "introduction": ["Contact information..."], "guidelines": [], "contact_prompt": "Get in touch"}
        },
        "meta": {"site_title": "Professional Fingerprint", "navigation_structure": ["Home", "Patterns", "About"]}
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


def react_developer_agent(mood_system: dict, content_strategy: dict, ux_plan: dict, user_name: str, image_paths: list, orchestrator_feedback: str = None, icon_strategy: dict = None) -> str:
    """
    React Developer Agent: Writes a complete single-file React app for Professional Fingerprinting.
    Can receive feedback from Orchestrator for regeneration.
    Now includes icon integration based on Icon Curator suggestions.
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

ICON INTEGRATION (MANDATORY - IF ICON_STRATEGY PROVIDED):
- Icons MUST be visible in the generated site (not optional!)
- Add Lucide CDN to <head>: <script src="https://unpkg.com/lucide@latest"></script>
- Use data-lucide attributes for icons (NOT React components)
- Initialize icons after React renders: lucide.createIcons()

ICON USAGE EXAMPLES:
```jsx
// Navigation icons
<nav>
  <a href="#home"><i data-lucide="home" className="w-5 h-5"></i> Home</a>
  <a href="#about"><i data-lucide="user" className="w-5 h-5"></i> About</a>
</nav>

// Feature cards with icons
<div className="feature-card">
  <i data-lucide="zap" className="w-12 h-12 mb-4 text-accent"></i>
  <h3>Feature Title</h3>
  <p>Description</p>
</div>

// Initialize after render in useEffect
useEffect(() => {
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}, [currentPage]);
```

ICON PLACEMENT RULES:
- Use icons from the ICON_STRATEGY suggestions ONLY
- Place icons based on icon_strategy.usage_philosophy (minimal/decorative/functional)
- Color icons using the accent color from mood_system
- Size: w-5 h-5 for nav, w-8 h-8 for cards, w-12 h-12 for heroes
- MANDATORY: Call lucide.createIcons() in useEffect for every page change

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

CRITICAL STYLING RULES (PREVENT BLANK/INVISIBLE PAGES):
1. **Navigation visibility**: Glass nav MUST have solid dark background (rgba(0,0,0,0.8) or rgba(30,30,30,0.9)) with white text
2. **Text contrast**: NEVER use white text on white backgrounds or black on black
3. **Accent color usage**: Create .text-accent and .bg-accent classes in <style> using the MOOD_SYSTEM accent color
4. **Minimum viable styles**: Always include inline <style> tag with body, h1-h3, .glass, .nav-link, .text-accent, .bg-accent
5. **Test visibility**: Imagine opening in a browser - can you SEE the navigation? Can you SEE the headings?

STYLE TAG TEMPLATE (MANDATORY):
```html
<style>
  body {{font-family: 'PRIMARY_FONT', sans-serif; color: TEXT_COLOR; background: BG_COLOR;}}
  h1,h2,h3{{font-family:'HEADING_FONT',sans-serif; font-weight:700; letter-spacing: 0.02em;}}
  h1{{font-weight:800; font-size: 3.5rem;}}
  h2{{font-weight:700; font-size: 2.5rem;}}
  .glass {{backdrop-filter:blur(10px); background:rgba(20,20,20,0.85); box-shadow: 0 4px 6px rgba(0,0,0,0.1);}}
  .nav-link{{color:#FFFFFF; text-decoration:none;}}
  .text-accent{{color: ACCENT_COLOR;}}
  .bg-accent{{background-color: ACCENT_COLOR;}}
</style>
```
Replace PRIMARY_FONT, HEADING_FONT, TEXT_COLOR, BG_COLOR, ACCENT_COLOR with actual values from MOOD_SYSTEM.

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
<body>
  <div id="root"></div>
  
  <script type="text/babel">
  const {{ motion, AnimatePresence, useScroll, useTransform }} = window.Motion;
  const {{ useState, useEffect, useRef }} = React;

  // EMBED CONTENT DATA AS A CONSTANT (MANDATORY)
  const CONTENT_DATA = {{content_strategy_json_here}};

  // Your components here...
  
  // RENDER AT THE END
  ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
```

CRITICAL: <div id="root"></div> MUST come BEFORE the <script> tag!

JSX SYNTAX VALIDATION (CRITICAL - PREVENT BLANK PAGES):
1. **Self-closing tags**: ALL React components without children MUST use `/>` (e.g., `<Home />`, `<Patterns />`)
2. **Conditional rendering**: `{condition && <Component />}` - NEVER forget the closing `/>` 
3. **Check every component**: In the main render, verify EACH component line ends with `/>` or `></Component>`
4. **Common mistake**: `{page==='home'&&<Home key="home"}}` ❌ WRONG
5. **Correct syntax**: `{page==='home'&&<Home key="home"/>}` ✅ CORRECT

BEFORE SUBMITTING YOUR HTML, SCAN THESE LINES:
- Main App return statement with conditional rendering
- Every `<ComponentName key="..."/>` must have the closing `/>`
- Missing `/>` causes JavaScript parse error = BLANK PAGE

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
    
    # Build icon section with explicit usage instructions
    if icon_strategy and icon_strategy.get('suggestions'):
        icon_list = "\n".join([f"  - {icon.get('name')} ({icon.get('lucide_name')}): {icon.get('purpose')}" for icon in icon_strategy.get('suggestions', [])])
        # Extract color safely
        color_scheme = icon_strategy.get('color_scheme', {})
        icon_color = color_scheme.get('primary', '#2997ff') if isinstance(color_scheme, dict) else '#2997ff'
        
        icon_section = """

=== ICON STRATEGY (MUST IMPLEMENT) ===
Library: """ + icon_strategy.get('icon_library', 'lucide') + """
CDN: """ + icon_strategy.get('cdn_url', 'https://unpkg.com/lucide@latest') + """
Philosophy: """ + icon_strategy.get('usage_philosophy', 'minimal') + """

ICONS TO USE (EXACTLY THESE):
""" + icon_list + """

IMPLEMENTATION CHECKLIST:
✓ Add Lucide CDN to <head>
✓ Use <i data-lucide="icon-name" className="w-5 h-5"></i> for each icon
✓ Call lucide.createIcons() in useEffect after each page render
✓ Color icons using accent color (""" + icon_color + """)
✓ Place icons in navigation, feature cards, section headers (based on suggestions above)

EXAMPLE IMPLEMENTATION:
```jsx
// Navigation with icons
<nav className="fixed top-0 w-full backdrop-blur-md bg-black/70 z-50">
  <a href="#home"><i data-lucide="home" className="w-5 h-5 inline mr-2"></i>Home</a>
  <a href="#patterns"><i data-lucide="brain" className="w-5 h-5 inline mr-2"></i>Patterns</a>
</nav>

// Feature cards with icons
<div className="grid grid-cols-3 gap-6">
  <div className="card">
    <i data-lucide="target" className="w-12 h-12 text-accent mb-4"></i>
    <h3>Feature Title</h3>
  </div>
</div>

// Initialize icons
useEffect(() => {{
  if (typeof lucide !== 'undefined') {{
    lucide.createIcons();
  }}
}}, [currentPage]);
```
"""
    else:
        icon_section = ""
    
    # Escape curly braces to avoid LangChain template parsing conflicts
    system_prompt_escaped = system_prompt.replace("{", "{{").replace("}", "}}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_escaped),
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
{icons}

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
            "feedback": feedback_section,
            "icons": icon_section
        })
        
        print(f"[DEBUG] React Developer generated HTML: {len(html_content)} characters")
        
        # CRITICAL FIX: Ensure <div id="root"> comes BEFORE scripts
        # React cannot render if the root element doesn't exist yet
        if '<div id="root">' in html_content and '</script>' in html_content:
            # Find the position of root div and script tags
            root_pos = html_content.find('<div id="root">')
            last_script_pos = html_content.rfind('</script>')
            
            if root_pos > last_script_pos:
                print("[FIX] Moving <div id='root'> before React script")
                # Remove the root div from its current position
                root_div = '<div id="root"></div>'
                html_content = html_content.replace(root_div, '', 1)
                
                # Insert it right after <body> tag
                body_pos = html_content.find('<body')
                if body_pos != -1:
                    # Find the end of the <body> tag
                    body_end = html_content.find('>', body_pos) + 1
                    html_content = html_content[:body_end] + '\n' + root_div + '\n' + html_content[body_end:]
                    print("[FIX] Root div moved successfully")
        
        # ICON INJECTION: Add icons deterministically based on icon strategy
        if icon_strategy and icon_strategy.get('suggestions'):
            print(f"[ICON INJECTION] Adding {len(icon_strategy.get('suggestions', []))} icons to HTML")
            
            # Ensure lucide CDN is present
            if 'lucide' not in html_content:
                lucide_cdn = '<script src="https://unpkg.com/lucide@latest"></script>\n    '
                if '</head>' in html_content:
                    html_content = html_content.replace('</head>', f'{lucide_cdn}</head>')
            
            # Add icon initialization script before closing body tag
            icon_init_script = '''
<script>
  // Initialize Lucide icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
</script>
'''
            if '</body>' in html_content and 'lucide.createIcons' not in html_content:
                html_content = html_content.replace('</body>', f'{icon_init_script}</body>')
                print("[ICON INJECTION] Added Lucide initialization script")
        
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
        
        # CRITICAL: Validate React code structure
        if '<script type="text/babel">' in html_content:
            # Check if CONTENT_DATA is embedded
            if 'const CONTENT_DATA' not in html_content and 'CONTENT_DATA =' not in html_content:
                print("[ERROR] CONTENT_DATA not embedded in React code!")
                print("[FIX] This will cause empty pages - using fallback with content")
                # Don't use this broken code, use the fallback instead
                raise ValueError("Generated code missing CONTENT_DATA embedding")
            
            # Check if root element exists
            if '<div id="root"' not in html_content:
                print("[ERROR] Missing root div element!")
                raise ValueError("Generated code missing root element")
            
            # Check if ReactDOM.createRoot is present
            if 'createRoot' not in html_content and 'ReactDOM.render' not in html_content:
                print("[ERROR] Missing React rendering code!")
                raise ValueError("Generated code missing React render call")
            
            # FIX: Invisible content due to poor contrast or missing accent colors
            if '<style>' in html_content:
                style_start = html_content.find('<style>')
                style_end = html_content.find('</style>', style_start)
                if style_start != -1 and style_end != -1:
                    style_content = html_content[style_start:style_end + 8]
                    
                    # Check for invisible nav (white text on light glass)
                    if '.glass' in style_content and 'rgba(255,255,255' in style_content:
                        print("[FIX] Detected invisible glass nav (white on white) - darkening background")
                        # Replace transparent white glass with dark glass
                        style_content = style_content.replace('rgba(255,255,255,0.1)', 'rgba(20,20,20,0.85)')
                        style_content = style_content.replace('rgba(255,255,255,0.2)', 'rgba(20,20,20,0.85)')
                        style_content = style_content.replace('rgba(255,255,255,0.3)', 'rgba(20,20,20,0.85)')
                        html_content = html_content[:style_start] + style_content + html_content[style_end + 8:]
                    
                    # FIX: Ensure proper contrast between text and background
                    def get_luminance(hex_color):
                        """Calculate relative luminance for WCAG contrast"""
                        hex_color = hex_color.strip('#')
                        if len(hex_color) == 3:
                            hex_color = ''.join([c*2 for c in hex_color])
                        r, g, b = [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)]
                        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
                        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
                        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
                        return 0.2126*r + 0.7152*g + 0.0722*b
                    
                    def has_good_contrast(color1, color2, min_ratio=4.5):
                        """Check if two colors have sufficient contrast"""
                        try:
                            lum1 = get_luminance(color1)
                            lum2 = get_luminance(color2)
                            lighter = max(lum1, lum2)
                            darker = min(lum1, lum2)
                            ratio = (lighter + 0.05) / (darker + 0.05)
                            return ratio >= min_ratio
                        except:
                            return True  # If parsing fails, assume it's okay
                    
                    # Extract body background and text color from mood_system
                    bg_color = mood_system.get('colors', {}).get('background', '#FFFFFF')
                    text_color = mood_system.get('colors', {}).get('text', '#000000')
                    
                    # Check contrast and fix if needed
                    if not has_good_contrast(bg_color, text_color):
                        print(f"[FIX] Poor contrast detected: {text_color} on {bg_color}")
                        # Determine if background is light or dark
                        bg_lum = get_luminance(bg_color)
                        if bg_lum > 0.5:
                            # Light background - use dark text
                            text_color = '#1a1a1a'
                            print(f"[FIX] Using dark text {text_color} for light background")
                        else:
                            # Dark background - use light text
                            text_color = '#f5f5f5'
                            print(f"[FIX] Using light text {text_color} for dark background")
                        
                        # Update the style content
                        import re
                        # Fix body color
                        style_content = re.sub(r'(body\s*\{[^}]*color\s*:\s*)#[0-9a-fA-F]{3,6}', f'\\1{text_color}', style_content)
                        # Ensure h1,h2,h3 have explicit color
                        if 'h1,h2,h3' in style_content and 'color:' not in style_content[style_content.find('h1,h2,h3'):style_content.find('}', style_content.find('h1,h2,h3'))]:
                            style_content = style_content.replace('h1,h2,h3{', f'h1,h2,h3{{color:{text_color};')
                        elif 'h1,h2,h3' not in style_content:
                            # Add heading styles with proper color
                            style_content = style_content.replace('</style>', f'\n  h1,h2,h3{{color:{text_color};}}\n</style>')
                        
                        html_content = html_content[:style_start] + style_content + html_content[style_end + 8:]
                    
                    # Add missing accent color classes if not present
                    if '.text-accent' not in style_content or '.bg-accent' not in style_content:
                        print("[FIX] Adding missing accent color classes")
                        # Extract accent color from mood_system if available
                        accent_color = mood_system.get('colors', {}).get('accent', '#2997ff')
                        accent_styles = f"\n  .text-accent{{color:{accent_color};}}\n  .bg-accent{{background-color:{accent_color};}}\n"
                        html_content = html_content.replace('</style>', accent_styles + '</style>')
            
            # Check and FIX lucide-react usage issues (common mistake)
            if 'lucide' in html_content.lower():
                if '<LucideIcon' in html_content or 'LucideIcon' in html_content:
                    print("[WARNING] Code uses LucideIcon components with UMD lucide - this won't work!")
                    print("[INFO] Auto-fixing icon implementation to use data-lucide attributes")
                    
                    # Remove LucideIcon components and replace with data-lucide pattern
                    # This is a simple fix - just remove icons for now to prevent JS errors
                    # Better: regenerate with proper icon instructions
                    html_content = re.sub(r'<LucideIcon[^/>]*/?>', '', html_content)
                    html_content = re.sub(r'const\s+NAV_ICONS\s*=\s*\{[^}]*\};', '', html_content)
                    print("[INFO] Removed LucideIcon components to prevent runtime errors")
        
        print("[VALIDATION] HTML structure checks passed")
        
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
        
        # Fix Framer Motion access patterns and add safe fallback to avoid blank page
        html_content = html_content.replace("window['framer-motion']", "window.Motion")
        html_content = html_content.replace('window["framer-motion"]', "window.Motion")

        # Insert a defensive Motion fallback inside the Babel script to prevent runtime crashes
        if '<script type="text/babel">' in html_content:
            safe_motion = (
                "\n// Safe Framer Motion fallback to avoid blank page when CDN attaches differently\n"
                "const __Motion = (window.Motion || window['framer-motion'] || {});\n"
                "const motion = __Motion.motion || (({ children, ...props }) => React.createElement('div', props, children));\n"
                "const AnimatePresence = __Motion.AnimatePresence || (({ children }) => children);\n"
            )
            html_content = html_content.replace(
                '<script type="text/babel">',
                '<script type="text/babel">' + safe_motion
            )
        
        # CRITICAL: Fix malformed JavaScript object syntax
        # Replace ],[ with proper comma separation ], 
        # This catches errors like: prop1:[...]],[prop2:[...]]
        html_content = re.sub(r'\],\s*\[', '], ', html_content)
        
        # CRITICAL: Remove any duplicate motion declarations that would crash
        # The LLM sometimes generates "const {motion, AnimatePresence} = window.Motion;" 
        # which crashes when window.Motion is undefined. We already have a safe fallback above.
        # Remove these dangerous lines that try to destructure from window.Motion or window['framer-motion']
        html_content = re.sub(
            r'\n\s*const\s*\{\s*motion[^}]*\}\s*=\s*window\.Motion\s*;?\s*\n',
            '\n',
            html_content
        )
        html_content = re.sub(
            r'\n\s*const\s*\{\s*motion[^}]*\}\s*=\s*window\[.framer-motion.\]\s*;?\s*\n',
            '\n',
            html_content
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
    """Bulletproof JSON extractor with multiple fallback strategies."""
    import re
    
    # Strategy 1: Direct parse
    try:
        return json.loads(content)
    except Exception:
        pass
    
    # Strategy 2: Strip markdown code blocks
    cleaned = content
    if "```json" in cleaned:
        try:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except Exception:
            pass
    elif "```" in cleaned:
        try:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
            return json.loads(cleaned)
        except Exception:
            pass
    
    # Strategy 3: Remove ALL known LLM markers and control tokens
    markers_to_remove = [
        "<|channel|>", "<|constrain|>", "<|message|>", 
        "<|im_start|>", "<|im_end|>", "<|endoftext|>",
        "final", "JSON", "json", "```"
    ]
    cleaned = content
    for marker in markers_to_remove:
        cleaned = cleaned.replace(marker, "")
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Strategy 4: Find first '{' and last '}' - but validate it's complete JSON
    start = cleaned.find('{')
    if start != -1:
        # Count braces to find the matching closing brace
        brace_count = 0
        end = -1
        for i in range(start, len(cleaned)):
            if cleaned[i] == '{':
                brace_count += 1
            elif cleaned[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i
                    break
        
        if end != -1:
            candidate = cleaned[start:end+1]
            try:
                return json.loads(candidate)
            except Exception as e:
                print(f"[DEBUG] Brace-matching failed: {e}")
    
    # Strategy 5: Use regex to find JSON object pattern
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, cleaned, re.DOTALL)
    for match in matches:
        try:
            result = json.loads(match)
            # Validate it's not just an empty object
            if result and len(result) > 0:
                return result
        except Exception:
            continue
    
    # Strategy 6: Try to find and fix common JSON errors
    # Fix unescaped quotes, trailing commas, etc.
    try:
        # Find the JSON-like content
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start:end+1]
            
            # Fix common issues
            # Remove trailing commas before closing braces/brackets
            candidate = re.sub(r',\s*}', '}', candidate)
            candidate = re.sub(r',\s*]', ']', candidate)
            
            return json.loads(candidate)
    except Exception as e:
        print(f"[DEBUG] JSON repair failed: {e}")
    
    # Last resort: raise with detailed error
    print(f"[ERROR] All JSON extraction strategies failed")
    print(f"[ERROR] Content length: {len(content)}")
    print(f"[ERROR] First 500 chars: {content[:500]}")
    print(f"[ERROR] Last 200 chars: {content[-200:]}")
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
            
            # STRUCTURE VALIDATION & AUTO-CORRECTION for legacy profile
            if not isinstance(data, dict):
                raise ValueError("Parsed data is not a dictionary")
            
            # Fix missing 'meta' or 'fingerprint' fields
            if 'meta' not in data or 'fingerprint' not in data:
                # Check if data looks like it has the right content but wrong structure
                if 'name' in data and 'thesis' in data:
                    # It's just the meta content
                    print("[FIX] Legacy profile: detected meta content at top level")
                    meta_data = data
                    data = {
                        'meta': meta_data,
                        'fingerprint': {
                            'patterns': [],
                            'anti_claims': [],
                            'failure_map': [],
                            'decision_log': [],
                            'method': {'name': 'N/A', 'steps': [], 'when_works': '', 'when_fails': ''},
                            'working_with_me': []
                        }
                    }
            
            # Ensure required fields exist
            if 'meta' not in data:
                print("[FIX] Legacy profile: adding missing 'meta' field")
                data['meta'] = {
                    'name': user_answers.get('who_are_you', 'Unknown'),
                    'thesis': 'Analysis incomplete',
                    'social': {}
                }
            
            if 'fingerprint' not in data:
                print("[FIX] Legacy profile: adding missing 'fingerprint' field")
                data['fingerprint'] = {
                    'patterns': [],
                    'anti_claims': [],
                    'failure_map': [],
                    'decision_log': [],
                    'method': {'name': 'N/A', 'steps': [], 'when_works': '', 'when_fails': ''},
                    'working_with_me': []
                }
            
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
