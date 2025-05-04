from typing import List, Dict
import json

class CallQualityAnalyzer:
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance

    def analyze(self, conversation: List[Dict]) -> Dict[str, float]:
        if not conversation:
            return {
                "total_duration": 0.0,
                "overtalk_duration": 0.0,
                "silence_duration": 0.0,
                "speaking_duration": 0.0
            }

        conversation.sort(key=lambda x: x["stime"])

        total_duration = conversation[-1]["etime"] - conversation[0]["stime"]
        overtalk_duration = 0.0
        silence_duration = 0.0

        for i in range(1, len(conversation)):
            prev = conversation[i - 1]
            curr = conversation[i]

            prev_end = prev["etime"]
            curr_start = curr["stime"]

            if curr_start < prev_end - self.tolerance:
                overtalk_duration += prev_end - curr_start
            elif curr_start > prev_end + self.tolerance:
                silence_duration += curr_start - prev_end

        speaking_duration = total_duration - silence_duration

        return {
            "total_duration": round(total_duration, 3),
            "overtalk_duration": round(overtalk_duration, 3),
            "silence_duration": round(silence_duration, 3),
            "speaking_duration": round(speaking_duration, 3)
        }

