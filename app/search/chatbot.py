import os
import requests
import json
from app.database import load_env


class Chatbot:
    def __init__(self, model_name=None, llama_end_point=None, groq_api_key=None):
        if model_name is None or llama_end_point is None or groq_api_key is None:
            load_env()
        # self.llm = LLM(model_path=model_path)
        self.groq_api_key = groq_api_key if groq_api_key is not None else os.environ.get('LLAMA_API_KEY')
        self.model_name = model_name if model_name is not None else os.environ.get('LLAMA_MODEL_NAME')
        self.end_point = llama_end_point if llama_end_point is not None else os.environ.get('LLAMA_END_POINT')
        if self.end_point is None:
            self.end_point = "https://api.groq.com/openai/v1/chat/completions"
        self.conversation_history = []
        self.system_context = ""
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.groq_api_key}"  # Replace with your API key if required
        }

    def set_system_context(self, context):
        """Sets the system context for the chatbot."""
        self.system_context = context

    def chat(self, user_input, revisedQuery: bool = False):
        if (revisedQuery):
            _user_input = f"Please provide 3 revised versions of this query: {user_input} in the JSON version mentioned above"
            """Handles user input, generates a groq_llama_response, and updates chat history."""
            # Initialize the conversation history
        else:
            _user_input = user_input

        if isinstance(_user_input, list):
            for i in range(len(_user_input)):
                query = _user_input[i]
                self.call_llm(query)
        else:
            self.call_llm(_user_input)

        return self.conversation_history

    def call_llm(self, _user_input):
        self.conversation_history = [
            {
                "role": "system",
                "content": self.system_context
            }
        ]
        # Add user input to the conversation history
        user_message = {
            "role": "user",
            "content": _user_input
        }
        self.conversation_history.append(user_message)
        # Construct the payload to send to the API
        payload = {
            "model": self.model_name,
            "messages": self.conversation_history
        }
        try:
            # Send the HTTP request to LLAMA 3.3
            groq_llama_response = requests.post(self.end_point, headers=self.headers, data=json.dumps(payload))
            # Process the groq_llama_response
            if groq_llama_response.status_code == 200:
                assistant_response = groq_llama_response.json()
                assistant_message = {
                    "role": "assistant",
                    "content": assistant_response.get("choices", [{}])[0].get("message", "No content in groq_llama_response")
                }

                # Add assistant's groq_llama_response to the conversation history
                self.conversation_history.append(assistant_message)

                # Output the assistant's groq_llama_response
                # print("Assistant:", json.dump(self.conversation_history["content"], indent=4))
            else:
                print(f"Error: {groq_llama_response.status_code} - {groq_llama_response.text}")
                groq_llama_response.raise_for_status()  # Raise an exception for bad status codes

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Groq: {e}")


if __name__ == "__main__":
    # Path to your llama-3.3-70b-versatile model
    # model_path = "path/to/your/llama-3.3-70b-versatile/model"

    chatbot = Chatbot(model_name=None, groq_api_key=None, llama_end_point=None)

    # Set system context (optional)
    context = '''You are a helpful financial assistant. Money managers, investment consultants, and financial planners are regulated in the United States as “investment advisers” under the U.S. Investment Advisers Act of 1940 (“Advisers Act” or “Act”) or similar state statutes. This outline describes the regulation of investment advisers by the U.S. Securities and Exchange Commission (“SEC”).
                Provide revised versions of queries and make it relevant so that it can search in the Financial Advisor regulation of SEC. here is the query to fix 
                "in JSON format with the following structure: '{"revisedQuery": ["revised query 1", "revised query 2"]}'''
    chatbot.set_system_context(context)

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        final_user_input = f"Please provide 3 revised versions of this query: {user_input}"
        chatbot.chat(final_user_input)
        print("Assistant:", json.dumps(chatbot.conversation_history, indent=4))
