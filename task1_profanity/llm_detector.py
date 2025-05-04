import os
import json
from typing import Dict, Union, List
import google.generativeai as genai


class ProfanityLLMDetector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        genai.configure(api_key=self.api_key or os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def format_conversation(self, utterances: List[Dict]) -> str:
        formatted = []
        for utt in utterances:
            speaker = utt.get("speaker", "unknown")
            text = utt.get("text", "").strip().replace("\n", " ")
            formatted.append(f"{speaker}: {text}")
        return "\n".join(formatted)

    def analyze_conversation(self, conversation: Union[Dict, List[Dict]]) -> Dict[str, bool]:
        if isinstance(conversation, dict):
            utterances = list(conversation.values())[0] if len(conversation) == 1 else conversation.get("utterances", [])
        else:
            utterances = conversation

        input_text = self.format_conversation(utterances)

        prompt = (
            "You are a conversation compliance checker. "
            "Analyze the following dialogue between a debt collection agent and a borrower. "
            "Return a JSON object with two fields: "
            "`agent_profanity` and `borrower_profanity`, both set to true or false "
            "depending on whether profanity was used by that speaker.\n\n"
            f"Conversation:\n{input_text}\n\n"
            "Response format:\n"
            '{\n  "agent_profanity": true/false,\n  "borrower_profanity": true/false\n}'
        )

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip("```json").strip("```").strip()
            result = json.loads(json_text)
            # Sanitize result to be safe
            return {
                "agent_profanity": bool(result.get("agent_profanity", False)),
                "borrower_profanity": bool(result.get("borrower_profanity", False))
            }
        except Exception as e:
            print(f"[ERROR] Gemini LLM failed: {e}")
            return {
                "agent_profanity": False,
                "borrower_profanity": False
            }
