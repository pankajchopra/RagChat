import os
from typing import Dict, List
import httpx
import asyncio
import time



class OpenAIChatbotC:
    def __init__(self, api_key: str = None, model: str =None, base_url: str =None):
        """
        Initialize ChatbotOpenAI with OpenAI API credentials
        
        :param api_key: OpenAI API key
        :param model: OpenAI model to use (defaults to GPT-4)
        """
        print("Hello _init_")
        api_key = os.getenv("OPENAI_API_KEY")
        model: "gpt-4"
        base_url="https://api.openai.com/v1/chat/completions"
        self.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
        self.model = model if model else os.getenv("OPENAI_MODEL")
        self.base_url = base_url if base_url else os.getenv("OPENAI_API_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

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
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content'].strip()
            except httpx.RequestError as exc:
                raise Exception(f"HTTP Request Error: {exc}")
            except KeyError as exc:
                raise Exception(f"Response Parsing Error: {exc}")

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
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }

        with httpx.Client() as client:
            try:
                response = client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content'].strip()
            except httpx.RequestError as exc:
                raise Exception(f"HTTP Request Error: {exc}")
            except KeyError as exc:
                raise Exception(f"Response Parsing Error: {exc}")

    # Example usage


def main():
    try:
        # Replace with your actual OpenAI API key
        # api_key = os.getenv("OPENAI_API_KEY")

        client = OpenAIChatbotC()

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Explain quantum computing simply."}
        ]
        # Async method
        # response = await client.async_get_response(messages)
        # print("Async Response:", response)

        # Sync method (alternative)
        sync_response = client.sync_get_response(messages)
        print("Sync Response:", sync_response)

    except Exception as e:
        print(f"Error: {e}")


# Run async main
if __name__ == "__main__":
    for retry in range(5):
        try:
            main()
        except Exception as e:
            if retry < 5 - 1:
                wait_time = 2 ** retry  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise Exception("Max retries exceeded") from e
