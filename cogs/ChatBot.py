import openai
import json
import os
from dotenv import load_dotenv

load_dotenv("..\.env")

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_response(user_message):
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=user_message,
        max_tokens=100,
        temperature=0.6,
        top_p=1.0,
        n=1,
        stop=None,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].text.strip()


print("ChatGPT: Hello! How can I assist you today?")
while True:
    user_input = input("User: ")
    if user_input.lower() == 'bye':
        print("ChatGPT: Goodbye!")
        break
    response = generate_response(user_input)
    print("ChatGPT:", response)
