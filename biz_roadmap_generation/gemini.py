# followed the Gemini API quickstart tutorial https://ai.google.dev/gemini-api/docs/quickstart?lang=python

import google.generativeai as genai
import os

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel(
    'gemini-1.5-flash',
    generation_config=genai.GenerationConfig(
        max_output_tokens=2000,
        temperature=0.1,        # use higher values for more creative responses, and lower values for more deterministic responses, 0<x<1
    ))

# response = model.generate_content("Write a story about a magic backpack.") # magic backpack story example
# response = model.generate_content("Give me python code to sort a list") # python code example

# chat session example
chat = model.start_chat(history=[])
response = chat.send_message("In one sentence, explain how a computer works to a young child.")
response = chat.send_message("Okay, how about a more detailed explanation to a high schooler?")

# generation_config
response = model.generate_content(
    'Give me a numbered list of cat facts.',
    # limit to 5 facts
    generation_config = genai.GenerationConfig(stop_sequences=['\n6'])
)

print(response.text)

print(chat.history)