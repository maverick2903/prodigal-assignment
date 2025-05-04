import os
import json
from typing import Dict, Union, List
import google.generativeai as genai

# Set up Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not set in environment.")

genai.configure(api_key=API_KEY)

class ComplianceLLMDetector:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def format_conversation(self, utterances: List[Dict]) -> str:
        formatted = []
        for utt in utterances:
            speaker = utt.get("speaker", "unknown")
            text = utt.get("text", "").strip().replace("\n", " ")
            formatted.append(f"{speaker}: {text}")
        return "\n".join(formatted)

    def analyze_conversation(self, conversation: Union[Dict, List[Dict]]) -> Dict[str, bool]:
        input_text = self.format_conversation(conversation)

        prompt = (
            "You are a compliance analyst. Review this debt collection call transcript.\n"
            "Check if the AGENT shared any sensitive information (such as account balance or account number) "
            "BEFORE verifying the identity of the borrower using personal information (such as date of birth, address, or SSN).\n\n"
            "Return your response as a JSON object with:\n"
            "`privacy_violation`: true if such a violation exists, false otherwise.\n\n"
            f"Conversation:\n{input_text}\n\n"
            "Response format:\n"
            '{\n  "privacy_violation": true/false\n}'
        )

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip("```json").strip("```").strip()
            result = json.loads(json_text)
            return {
                "privacy_violation": bool(result.get("privacy_violation", False))
            }
        except Exception as e:
            print(f"[ERROR] Gemini LLM failed: {e}")
            return {
                "privacy_violation": False
            }
