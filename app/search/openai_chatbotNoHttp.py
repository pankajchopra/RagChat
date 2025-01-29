import os
from typing import Dict, List
import httpx
from openai import OpenAI
import time


class OpenAIChatbotNoHttp:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        """
        Initialize ChatbotOpenAI with OpenAI API credentials
        
        :param api_key: OpenAI API key
        :param model: OpenAI model to use (defaults to GPT-4)
        """
        print("Hello _init_")
        api_key = os.getenv("OPENAI_API_KEY")
        model: "gpt-4"
        base_url = "https://api.openai.com/v1/chat/completions"
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        self.model = model if model else os.getenv("OPENAI_MODEL")
        self.base_url = base_url if base_url else os.getenv("OPENAI_API_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        ## Set the API key and model name
        self.MODEL = "gpt-4o-mini"
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", api_key))

    async def async_get_response(self,
                                 messages: List[Dict[str, str]],
                                 temperature: float = 0.7,
                                 top_p: float = 0.9,
                                 max_tokens: int = 2048) -> str:
        """
        Asynchronous method to get response from OpenAI API

        :param messages: Conversation messages
        :param temperature: Response randomness
        :param top_p: Sampling threshold
        :param max_tokens: Maximum response tokens
        :return: API response text
        """

    def get_full_prompt(self, prompt, context):
        full_prompt = ""
        for interaction in context["history"]:
            full_prompt += f"User: {interaction['user']}\nAssistant: {interaction['assistant']}\n"
        full_prompt += f"User: {prompt}\nAssistant: "
        return full_prompt

    def sync_get_response(self,
                          messages: List[Dict[str, str]],
                          temperature: float = 0.7,
                          top_p: float = 0.9,
                          max_tokens: int = 1024) -> str:
        """
        Synchronous method to get response from OpenAI API

        :param messages: Conversation messages
        :param temperature: Response randomness
        :param top_p: Sampling threshold
        :param max_tokens: Maximum response tokens
        :return: API response text
        """
        self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )


def main():
    try:
        client = OpenAIChatbotNoHttp()
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain quantum computing simply."}
        ]
        # Sync method (alternative)
        sync_response = client.sync_get_response(messages)
        print("Sync Response:", sync_response)
    except Exception as e:
        print(f"Error: {e}")


# Run async main
if __name__ == "__main__":
   main()
