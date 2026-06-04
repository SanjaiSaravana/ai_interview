import json
import os
from groq import Groq

class InterviewEvaluator:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate_report(self, transcript, role):
        """
        Analyzes the transcript and returns a JSON report.
        """
        prompt = (
            f"Review the following mock interview transcript for the role of {role}. "
            "Provide a detailed evaluation in strictly JSON format with the following keys: "
            "'technical_score' (1-10), 'soft_skills_score' (1-10), 'feedback' (overall summary), "
            "'areas_to_improve' (list of 3 specific points).\n\n"
            f"Transcript: {transcript}"
        )

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"} # Forces JSON output
            )
            return response.choices[0].message.content
        except Exception as e:
            return json.dumps({
                "technical_score": 0,
                "soft_skills_score": 0,
                "feedback": f"Error generating report: {str(e)}",
                "areas_to_improve": ["Connection lost during analysis"]
            })