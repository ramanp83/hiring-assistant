import openai
import os
from dotenv import load_dotenv
import time

load_dotenv()

openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
openai.api_key = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct")

def get_llm_response(user_input, context, retries=3, delay=1):
    """
    Get response from OpenRouter API with retry mechanism.
    """
    messages = [{"role": "system", "content": "You are a helpful AI hiring assistant."}]
    for msg in context:
        messages.append({"role": "user", "content": msg})
    messages.append({"role": "user", "content": user_input})

    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model=DEFAULT_MODEL,
                messages=messages,
                temperature=0.7
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
                continue
            return f"⚠️ Error calling OpenRouter API after {retries} attempts: {str(e)}"