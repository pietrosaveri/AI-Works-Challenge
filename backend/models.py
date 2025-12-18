"""
Pydantic models for the Professional Fingerprint application.
This module contains all data models used across the multi-agent system.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# === Content models ===
class Pattern(BaseModel):
    name: str
    summary: str
    analysis: List[str] = Field(default_factory=list)
    evidence_quotes: List[str] = Field(default_factory=list)


class AntiClaim(BaseModel):
    claim: str
    analysis: List[str] = Field(default_factory=list)
    quote: str = ""


class Failure(BaseModel):
    title: str
    analysis: List[str] = Field(default_factory=list)
    key_lesson: str = ""


class Decision(BaseModel):
    title: str
    analysis: List[str] = Field(default_factory=list)
    key_insight: str = ""


class MethodStep(BaseModel):
    step_number: int
    step_name: str
    description: List[str] = Field(default_factory=list)


class Method(BaseModel):
    page_title: str = Field(default="Proprietary Method")
    method_name: str = Field(default="Unique Approach")
    introduction: List[str] = Field(default_factory=list)
    steps: List["MethodStep"] = Field(default_factory=list)
    when_works: List[str] = Field(default_factory=list)
    when_fails: List[str] = Field(default_factory=list)
    conclusion: List[str] = Field(default_factory=list)


class Guideline(BaseModel):
    guideline: str
    explanation: List[str] = Field(default_factory=list)


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


# --- Icon and Orchestrator Models ---
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


class Workspace(BaseModel):
    design_dna: dict
    content_strategy: dict
    ux_plan: dict
    icon_plan: Optional[dict] = Field(default_factory=dict)
    react_code: Optional[str] = None
    version: int = 0
    action_log: List[str] = Field(default_factory=list)

    def bump(self, note: str) -> None:
        self.version += 1
        self.action_log.append(f"v{self.version}: {note}")


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


# --- Design DNA Model (Art Director Agent) ---
class DesignDNA(BaseModel):
    archetype: str = Field(description="Content archetype (e.g., manifesto, case_study, timeline_journey)")
    layout: str = Field(description="Layout pattern (e.g., bento_grid, asymmetric_scatter, stream_of_consciousness)")
    motion: str = Field(description="Motion style (e.g., parallax_scroll, brutal_static, liquid_fluid)")
    theme: str = Field(description="Visual theme (e.g., neo_brutalist, glassmorphism, minimal_zen)")
    color_palette: List[str] = Field(description="Array of 5 hex color codes [primary, secondary, accent, bg, text]")
    typography_pair: Dict[str, str] = Field(description="Font pairing with 'heading' and 'body' keys")
    reasoning: str = Field(description="Brief explanation of why this combination fits the user")


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
    explanation: str


class LegacyProfile(BaseModel):
    patterns: List[LegacyPattern]
    anti_claims: List[LegacyAntiClaim]
    failure_map: List[dict]
    decision_log: List[dict]
    proprietary_method: List[str]
