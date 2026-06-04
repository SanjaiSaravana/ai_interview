import os
from groq import Groq

class InterviewAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def get_response(self, history, role):
        """
        Generates the next interview question based on chat history.
        """
        system_prompt = {
            "role": "system", 
            "content": (
                f"You are a senior HR Manager interviewing a candidate for a {role} position. "
                "Keep your responses concise (1-2 sentences). Ask only ONE question at a time. "
                "If the candidate gives a brief answer, ask a follow-up to dig deeper. "
                "Be professional, slightly challenging, but encouraging."
            )
        }
        
        # Ensure system prompt is always at the start
        messages = [system_prompt] + history

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return completion.choices[0].message.content