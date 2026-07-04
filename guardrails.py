# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Security Guardrails Module for Scientific Publications Ingestion.
Ensures crawled titles and abstracts do not contain prompt injections,
jailbreaks, or instruction overrides.
"""
import re

# Suspect terms commonly found in jailbreaks and injection attempts
INJECTION_KEYWORDS = [
    r"\bignore\b.*\bprevious\b.*\binstructions\b",
    r"\bsystem\s+prompt\b",
    r"\bforget\b.*\b(past|previous)\b.*\b(instructions|directives)\b",
    r"\byou\s+are\s+now\b",
    r"\boverride\b.*\binstructions\b",
    r"\bdo\s+not\s+summarize\b",
    r"\bas\s+an\s+ai\b",
    r"\bassistant\b.*\bhelp\b",
    r"\bignore\b.*\babove\b",
    r"\bnew\s+role\b",
    r"\[system\]",
    r"\btranslate\b.*\bignore\b",
    r"\bprompt\s+injection\b"
]

def scan_text(text: str) -> tuple[bool, str, str]:
    """
    Scans a given text segment (abstract or title) for prompt injections.
    Returns: (is_flagged, reason, evidence)
    """
    if not text:
        return False, "", ""
        
    text_lower = text.lower()
    
    # 1. Keyword Scanning
    for pattern in INJECTION_KEYWORDS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            # Extract a snippet around the match
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            evidence = text[start:end].strip()
            return True, "Potential Prompt Injection Keyword Match", f"... {evidence} ..."
            
    # 2. Check for typical adversarial patterns (e.g. system commands, markdown code injection attempts)
    command_patterns = [
        r"user:\s*",
        r"assistant:\s*",
        r"system:\s*",
        r"human:\s*"
    ]
    for pat in command_patterns:
        match = re.search(pat, text_lower, re.IGNORECASE)
        if match:
            evidence = text[match.start():min(len(text), match.end() + 20)].strip()
            return True, "Suspicious Conversational Structure Injection", evidence
            
    return False, "", ""

def scan_paper(paper_data: dict) -> tuple[bool, str, str]:
    """
    Scans a dictionary of paper metadata (title, abstract) for security flags.
    Returns: (is_flagged, reason, evidence)
    """
    title = paper_data.get('title', '')
    abstract = paper_data.get('abstract', '')
    
    # Scan title
    flagged, reason, evidence = scan_text(title)
    if flagged:
        return True, f"Title Flagged: {reason}", evidence
        
    # Scan abstract
    flagged, reason, evidence = scan_text(abstract)
    if flagged:
        return True, f"Abstract Flagged: {reason}", evidence
        
    return False, "", ""
