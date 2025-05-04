import re
from typing import List, Dict, Union

DEFAULT_PROFANITY_LIST = [
    r'\bass\b', r'\bshit\b', r'\bfuck\b', r'\bdamn\b', r'\bbitch\b',
    r'\bcrap\b', r'\bhell\b', r'\bmotherfucker\b', r'\bwtf\b', r'\bpiss\b',
    r'\bdick\b', r'\bcunt\b', r'\bbugger\b', r'\bbastard\b', r'\bslut\b'
]

OBFUSCATED_PROFANITY_PATTERNS = [
    r'f\*+', r's\*+', r'b\*+', r'a\*+', r'd\*+',
    r'f[^a-zA-Z]*u[^a-zA-Z]*c[^a-zA-Z]*k',
    r's[^a-zA-Z]*h[^a-zA-Z]*i[^a-zA-Z]*t',
]

CONTEXTUAL_PROFANITY_PATTERNS = [
    r'shut up', r'go to hell', r'screw you',
    r'get lost', r'idiot', r'stupid', r'dumb',
    r'shut the hell up', r'what the hell', r'what the heck'
]


class ProfanityRegexDetector:
    def __init__(
        self,
        profanity_patterns: List[str] = None,
        obfuscated_patterns: List[str] = None,
        contextual_patterns: List[str] = None
    ):
        self.profanity_patterns = profanity_patterns or DEFAULT_PROFANITY_LIST
        self.obfuscated_patterns = obfuscated_patterns or OBFUSCATED_PROFANITY_PATTERNS
        self.contextual_patterns = contextual_patterns or CONTEXTUAL_PROFANITY_PATTERNS

        self.compiled_profanity = [re.compile(pat, re.IGNORECASE) for pat in self.profanity_patterns]
        self.compiled_obfuscated = [re.compile(pat, re.IGNORECASE) for pat in self.obfuscated_patterns]
        self.compiled_contextual = [re.compile(r'\b' + re.escape(pat) + r'\b', re.IGNORECASE)
                                    for pat in self.contextual_patterns]

    def detect_profanity(self, text: str) -> bool:
        """
        Detects if the text contains profanity by checking:
        1. Direct profanity
        2. Obfuscated forms
        3. Contextually rude phrases
        """
        for pattern_group in [self.compiled_profanity, self.compiled_obfuscated, self.compiled_contextual]:
            if any(pattern.search(text) for pattern in pattern_group):
                return True
        return False

    def analyze_conversation(self, conversation: Union[List[Dict], Dict]) -> Dict[str, bool]:
        """
        Analyzes a single conversation JSON.
        Returns:
        {
            "agent_profanity": True/False,
            "borrower_profanity": True/False
        }
        """
        flags = {
            "agent_profanity": False,
            "borrower_profanity": False
        }

        # Support for single dict input (just in case)
        if isinstance(conversation, dict):
            conversation = [conversation]

        for con in conversation:
            speaker = con.get("speaker", "").lower()
            text = con.get("text", "")

            if self.detect_profanity(text):
                if "agent" in speaker:
                    flags["agent_profanity"] = True
                elif "borrower" in speaker:
                    flags["borrower_profanity"] = True

            if all(flags.values()):
                break

        return flags
