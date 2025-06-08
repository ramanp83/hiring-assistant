import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

def get_llm_response(user_input, context):
    messages = [{"role": "system", "content": "You are a helpful AI hiring assistant."}]
    for msg in context:
        messages.append({"role": "user", "content": msg})
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3-8b-instruct",  # You can replace with gemma or cinematika
            messages=messages,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Error calling OpenRouter API: {str(e)}"
