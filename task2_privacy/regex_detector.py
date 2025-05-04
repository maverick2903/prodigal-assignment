import re
from typing import List, Dict, Union

class ComplianceRegexDetector:
    def __init__(self):
        self.sensitive_patterns = [
            # Balance and payment information
            r"balance\s+(?:is|of|shows|shows as|at|available)?\s+\$?[\d,]+\.?\d*",
            r"(?:you|your account|customer)\s+(?:currently )?(?:has|have|owe[sd]?|are carrying)\s+(?:a )?(?:balance|debt|amount)(?:\s+of)?\s+\$?[\d,]+\.?\d*",
            r"(?:account|current|available)\s+balance\s+(?:is|of|at|available)?\s+\$?[\d,]+\.?\d*",
            r"(?:minimum|past due|last|recent|next|monthly) (?:payment|bill|amount due)(?:\s+is)?\s+\$?[\d,]+\.?\d*",
            r"(?:total|outstanding|remaining) (?:balance|amount|debt)(?:\s+is)?\s+\$?[\d,]+\.?\d*",
            r"(?:paid|charged|deposited|withdrew|transferred)\s+\$?[\d,]+\.?\d*",
            r"transaction(?:\s+amount)?\s+(?:of|is|was)?\s+\$?[\d,]+\.?\d*",
            
            # Account numbers and identifiers
            r"account\s+(?:number|#)\s+(?:is|ends in|last digits|ending with)?\s+[\*x]?\d+",
            r"last\s+(?:\d+|four|five|six)\s+(?:digits|numbers)\s+(?:of|is|are)?\s+\d+",
            r"(?:your|the)\s+account\s+(?:number|ending|ends|last digits)\s+(?:with|in|is)?\s+\d+",
            r"card\s+(?:number|#)\s+(?:ending|ends|last digits)\s+(?:with|in)?\s+\d+",
            r"(?:credit|debit)\s+card\s+(?:ending|ends|last digits)\s+(?:with|in)?\s+\d+",
            r"routing\s+number\s+(?:is|of)?\s+\d+",
            
            # Loan and interest information
            r"interest\s+rate\s+(?:is|of|at)?\s+\d+\.?\d*\s*%",
            r"loan\s+(?:amount|balance|principal)\s+(?:is|of|remaining)?\s+\$?[\d,]+\.?\d*",
            r"(?:APR|annual percentage rate)\s+(?:is|of|at)?\s+\d+\.?\d*\s*%",
            
            # Date-related sensitive information
            r"expir(?:y|ation)\s+date\s+(?:is|of)?\s+\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}",
            r"due\s+date\s+(?:is|of|on)?\s+\d{1,2}[\/\-]\d{1,2}[\/\-]?\d{0,4}",
            
            # Personal identifiable information
            r"(?:your|the) (?:address|email|phone|contact number|zip code)\s+(?:is|shows as|listed as)?\s+\w+",
            r"(?:full|partial) (?:SSN|social security number)\s+(?:is|ending in)?\s+[\*x]?\d+"
        ]
        self.verification_patterns = [
            # DOB verification
            r"(?:can|could) (?:you|I) (?:please |kindly )?(?:verify|confirm|tell me|provide|share)(?:\s+your)?\s+(?:date of birth|DOB|birthday)",
            r"(?:what|when)(?:'s| is) your (?:date of birth|DOB|birthday)",
            r"(?:I need to|I'll need to|I have to|need to|must) (?:verify|confirm)(?:\s+your)?\s+(?:date of birth|DOB|birthday)",
            r"for verification(?:\s+purposes)?,? (?:what is|can you tell me)(?:\s+your)?\s+(?:date of birth|DOB|birthday)",
            
            # Address verification
            r"(?:can|could) (?:you|I) (?:please |kindly )?(?:verify|confirm|tell me|provide|share)(?:\s+your)?\s+(?:address|mailing address|home address|billing address|residential address)",
            r"(?:what|where)(?:'s| is) your (?:address|mailing address|home address|billing address|residential address)",
            r"(?:I need to|I'll need to|I have to|need to|must) (?:verify|confirm)(?:\s+your)?\s+(?:address|mailing address|home address|billing address|residential address)",
            r"for verification(?:\s+purposes)?,? (?:what is|can you tell me)(?:\s+your)?\s+(?:address|mailing address|home address|billing address|residential address)",
            
            # SSN verification
            r"(?:can|could) (?:you|I) (?:please |kindly )?(?:verify|confirm|tell me|provide|share)(?:\s+your)?\s+(?:social security number|SSN|last four of your social|last four digits of your SSN)",
            r"(?:what|what's) (?:is |are )?(?:your|the last|the) (?:social security number|SSN|last four of your social|last four digits of your SSN)",
            r"(?:I need to|I'll need to|I have to|need to|must) (?:verify|confirm)(?:\s+your)?\s+(?:social security number|SSN|last four of your social|last four digits of your SSN)",
            r"for verification(?:\s+purposes)?,? (?:what is|can you tell me)(?:\s+your)?\s+(?:social security number|SSN|last four of your social|last four digits of your SSN)",
            
            # General identity verification
            r"(?:I need to|I'll need to|I have to|need to|must) (?:verify|confirm|authenticate)(?:\s+your)?\s+(?:identity|ID|identification)",
            r"for (?:security|verification|authentication) (?:purposes|reasons|measures)",
            r"before (?:I|we) (?:can|could|proceed|continue|access|provide|share) (?:that|this|account|information|details)",
            r"(?:can|could) (?:you|I) (?:please |kindly )?(?:verify|confirm|authenticate)(?:\s+your)?\s+(?:identity|ID|identification)",
            
            # Security questions
            r"(?:security|verification) question",
            r"mother's maiden name",
            r"first pet'?s name",
            r"(?:childhood|high school|elementary school) (?:street|address|school)"
        ]
        
        self.sensitive_regexes = [re.compile(pat, re.IGNORECASE) for pat in self.sensitive_patterns]
        self.verification_regexes = [re.compile(pat, re.IGNORECASE) for pat in self.verification_patterns]

    def contains_sensitive_info(self, text: str) -> bool:
        return any(pat.search(text) for pat in self.sensitive_regexes)

    def contains_verification(self, text: str) -> bool:
        return any(pat.search(text) for pat in self.verification_regexes)

    def analyze_conversation(self, conversation: Union[List[Dict], Dict]) -> Dict[str, bool]:
        """
        Returns:
        {
            "privacy_violation": True/False
        }
        """

        verified = False
        violation_detected = False

        for con in conversation:
            speaker = con.get("speaker", "").lower()
            text = con.get("text", "")

            if "agent" not in speaker:
                continue

            # Check if identity verification occurs
            if self.contains_verification(text):
                verified = True
                continue

            # Check if sensitive info is shared without prior verification
            if self.contains_sensitive_info(text) and not verified:
                violation_detected = True
                break  # One violation is enough to flag

        return {"privacy_violation": violation_detected}
