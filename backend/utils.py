"""
Utility functions for the Professional Fingerprint application.
Contains validation, patching, and JSON sanitization functions.
"""
import re
import json
from typing import List, Dict
from .models import Workspace


def validate_workspace(ws: Workspace) -> List[dict]:
    """Check for consistency issues across agents."""
    issues = []
    
    # Content vs UX
    pages = ws.content_strategy.get("pages", {})
    nav = ws.ux_plan.get("navigation", {}).get("structure", [])
    page_keys = list(pages.keys()) if pages else []
    if nav:
        missing = [p for p in page_keys if p not in nav]
        extra = [n for n in nav if n not in page_keys]
        if missing:
            issues.append({"owner": "ux", "issue": f"Missing in nav: {missing}"})
        if extra:
            issues.append({"owner": "content", "issue": f"Nav has extra: {extra}"})

    # Icon strategy presence
    if ws.icon_plan is None or not ws.icon_plan.get("icon_library"):
        issues.append({"owner": "icons", "issue": "Icon strategy missing"})

    # React code embedding/content
    if not ws.react_code:
        issues.append({"owner": "react", "issue": "React code missing"})
    else:
        code = ws.react_code
        if "const CONTENT" not in code or "CONTENT" not in code:
            issues.append({"owner": "react", "issue": "CONTENT_DATA not embedded"})
        if "const UX" not in code:
            issues.append({"owner": "react", "issue": "UX_PLAN not embedded"})
        cdn_required = ["react@18/umd/react.production.min.js", "react-dom@18/umd/react-dom.production.min.js", "@babel/standalone/babel.min.js"]
        for cdn in cdn_required:
            if cdn not in code:
                issues.append({"owner": "react", "issue": f"Missing CDN: {cdn}"})

    return issues


def apply_react_patches(original: str, patch_obj: dict) -> str:
    """Apply simple replacements or full override to React HTML code."""
    if not patch_obj:
        return original
        
    if "full_override" in patch_obj and patch_obj["full_override"]:
        return patch_obj["full_override"]
        
    code = original
    if "replacements" in patch_obj:
        for rep in patch_obj["replacements"]:
            if "find" in rep and "replace" in rep:
                code = code.replace(rep["find"], rep["replace"], 1)
                
    return code


def _sanitize_json_output(content: str) -> dict:
    """Bulletproof JSON extractor with multiple fallback strategies."""
    if not content:
        raise ValueError("Empty content provided to JSON sanitizer")
    
    # Pre-clean: strip common JSON comments and artifacts
    cleaned = content
    # Remove ```json fences
    if "```json" in cleaned:
        start = cleaned.find("```json") + 7
        end = cleaned.find("```", start)
        if end != -1:
            cleaned = cleaned[start:end].strip()
    elif "```" in cleaned:
        start = cleaned.find("```") + 3
        end = cleaned.find("```", start)
        if end != -1:
            cleaned = cleaned[start:end].strip()
    
    # Strip // line comments (handling inline comments safely)
    import re as _re
    # Remove // comments that are not part of a URL (lookbehind for :)
    cleaned = _re.sub(r"(?<!:)//.*", "", cleaned)
    # Strip /* block */ comments
    cleaned = _re.sub(r"/\*.*?\*/", "", cleaned, flags=_re.DOTALL)
    # Remove trailing commas before } or ]
    cleaned = _re.sub(r",\s*}\s*", "}", cleaned)
    cleaned = _re.sub(r",\s*]\s*", "]", cleaned)

    # Strategy 1: Direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    
    # Strategy 3: Remove ALL known LLM markers and control tokens
    markers_to_remove = [
        "<|channel|>", "<|constrain|>", "<|message|>", 
        "<|im_start|>", "<|im_end|>", "<|endoftext|>",
        "final", "JSON", "json", "```"
    ]
    # Continue cleaning
    for marker in markers_to_remove:
        cleaned = cleaned.replace(marker, "")
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Strategy 4: Find first '{' and last '}' - but validate it's complete JSON
    start = cleaned.find('{')
    if start != -1:
        end = cleaned.rfind('}')
        if end != -1:
            json_candidate = cleaned[start:end+1]
            try:
                # Validate that braces are balanced
                open_count = json_candidate.count('{')
                close_count = json_candidate.count('}')
                if open_count == close_count:
                    parsed = json.loads(json_candidate)
                    return parsed
            except Exception:
                pass
    
    # Strategy 5: Use regex to find JSON object pattern
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, cleaned, re.DOTALL)
    for match in matches:
        try:
            parsed = json.loads(match)
            if parsed:  # Non-empty dict
                return parsed
        except Exception:
            continue
    
    # Strategy 6: Try to fix common JSON errors
    # Fix unescaped quotes, trailing commas, etc.
    try:
        # Remove trailing commas before closing braces/brackets
        fixed = re.sub(r',\s*}', '}', cleaned)
        fixed = re.sub(r',\s*]', ']', fixed)
        parsed = json.loads(fixed)
        return parsed
    except Exception as e:
        pass
    
    # Last resort: raise with detailed error
    print(f"[ERROR] All JSON extraction strategies failed")
    print(f"[ERROR] Content length: {len(content)}")
    print(f"[ERROR] First 500 chars: {content[:500]}")
    print(f"[ERROR] Last 200 chars: {content[-200:]}")
    raise ValueError(f"Could not extract valid JSON from LLM output. First 200 chars: {content[:200]}")
