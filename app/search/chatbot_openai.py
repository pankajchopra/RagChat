import os
import requests
import json
from app.database import load_env


class ChatbotOpenAI:
    def __init__(self, api_key, model="text-davinci-003"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

    def get_response(self, prompt, temperature=0.7, top_p=0.9, max_tokens=2048):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "prompt": prompt,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "model": self.model
        }

        response = requests.post(f"{self.base_url}/completions", headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            raise Exception(f"Error: {response.status_code}")

    def get_context(self, context):
        return {
            "system": context["system"],
            "persona": context["persona"],
            "history": context["history"]
        }

    def get_full_prompt(self, prompt, context):
        full_prompt = ""
        for interaction in context["history"]:
            full_prompt += f"User: {interaction['user']}\nAssistant: {interaction['assistant']}\n"
        full_prompt += f"User: {prompt}\nAssistant: "
        return full_prompt


# Example usage:
api_key = "YOUR_OPENAI_API_KEY"
chatbot = ChatbotOpenAI(api_key)

prompt = "How are you doing?"
context = {
    "system": "I am an AI assistant.",
    "persona": "I am a helpful and knowledgeable assistant.",
    "history": [
        {"user": "User: How are you doing?", "assistant": "Assistant: I am doing well, thank you for asking."},
        {"user": "User: What is your purpose?", "assistant": "Assistant: My purpose is to assist users with their queries."}
    ]
}

full_prompt = chatbot.get_full_prompt(prompt, context)
response = chatbot.get_response(full_prompt)

print(response)
