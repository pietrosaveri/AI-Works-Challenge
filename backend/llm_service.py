"""
Professional Fingerprint LLM Service
Main entry point that re-exports all components for backward compatibility.

This file maintains backward compatibility by re-exporting all functions and classes
from the refactored modules (models, llm_config, agents, utils).
"""

# Re-export LLM configuration
from .llm_config import (
    LLM_PROVIDER,
    GEMINI_MODEL,
    GOOGLE_API_KEY,
    LOCAL_LLM_BASE_URL,
    LOCAL_LLM_MODEL,
    get_llm_with_temp,
    get_llm_for_code_generation,
    llm
)

# Re-export all models
from .models import (
    # Content models
    Pattern,
    AntiClaim,
    Failure,
    Decision,
    MethodStep,
    Method,
    Guideline,
    AboutPage,
    HomePage,
    PatternsPage,
    AntiClaimsPage,
    FailuresPage,
    DecisionsPage,
    Pages,
    Meta,
    ContentStrategy,
    
    # Icon and Orchestrator models
    IconSuggestion,
    IconStrategy,
    OrchestratorReport,
    Workspace,
    
    # Mood Agent models
    Colors,
    Fonts,
    MoodSystem,
    
    # Design DNA model
    DesignDNA,
    
    # UX Architect models
    Navigation,
    PageLayout,
    TypographySystem,
    AnimationStrategy,
    UXPlan,
    
    # Legacy models
    LegacyPattern,
    LegacyAntiClaim,
    LegacyProfile
)

# Re-export utility functions
from .utils import (
    validate_workspace,
    apply_react_patches,
    _sanitize_json_output
)

# Re-export all agent functions
from .agents import (
    icon_curator_agent,
    orchestrator_agent,
    art_director_agent,
    mood_agent,
    content_strategist_agent,
    ux_architect_agent,
    react_developer_agent
)

# Legacy functions (analyze_profile, selenium_validator_agent) 
# were removed during refactoring - they should be replaced with content_strategist_agent
# If needed, add them back here or create a legacy.py module

# For backward compatibility with code that imports these directly
__all__ = [
    # Config
    'LLM_PROVIDER', 'GEMINI_MODEL', 'GOOGLE_API_KEY', 'LOCAL_LLM_BASE_URL', 'LOCAL_LLM_MODEL',
    'get_llm_with_temp', 'get_llm_for_code_generation', 'llm',
    # Models
    'Pattern', 'AntiClaim', 'Failure', 'Decision', 'MethodStep', 'Method', 'Guideline',
    'AboutPage', 'HomePage', 'PatternsPage', 'AntiClaimsPage', 'FailuresPage', 'DecisionsPage',
    'Pages', 'Meta', 'ContentStrategy', 'IconSuggestion', 'IconStrategy', 'OrchestratorReport',
    'Workspace', 'Colors', 'Fonts', 'MoodSystem', 'DesignDNA', 'Navigation', 'PageLayout',
    'TypographySystem', 'AnimationStrategy', 'UXPlan', 'LegacyPattern', 'LegacyAntiClaim', 'LegacyProfile',
    # Utils
    'validate_workspace', 'apply_react_patches', '_sanitize_json_output',
    # Agents
    'icon_curator_agent', 'orchestrator_agent', 'art_director_agent', 'mood_agent',
    'content_strategist_agent', 'ux_architect_agent', 'react_developer_agent',
]

