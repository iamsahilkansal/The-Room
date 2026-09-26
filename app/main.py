import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from google.genai import types
from agent import Agent
import re
import ollama

def sanitize_response(text: str) -> str:
    cleaned = re.sub(r'\*.*?\*', '', text)
    cleaned = re.sub(r' +', ' ', cleaned)
    return cleaned.strip()

def talk_to_agent(prompt, user_name="You"):
    formatted_prompt =(f"[{user_name}]: {prompt}")
    messages.append({"role": "user", "content": formatted_prompt})
    response = ollama.chat(model="mia-agent", messages=messages)
    response["message"]["content"] = sanitize_response(response["message"]["content"])
    agent_message = response["message"]  # This is a dict: {"role": "assistant", "content": "..."}
    agent_text = agent_message["content"] # This is the actual string response
    messages.append(agent_message)
    print(f"{agent_text}\n")

print("Ollama Chatbot Initialized! (Type 'exit' to quit)\n")
messages = []
while True:
    prompt = input("You: ")
    if prompt.lower() == "/exit":
        break

    if prompt.lower() == "/help":
        print("Commands:\n  /exit - Exit the chat\n  /reset - Reset the chat session\n  /help - Show this help message\n  /instructions - Show Mia's system instructions\n  /history - Show chat history\n")
        continue

    if prompt.lower() == "/instructions":
        print(f"System Instructions for Mia:\n{Agent['Mia']}\n")
        continue

    if prompt.lower() == '/history':
        print("Chat History:")
        for message in messages:
            print(f"{message['role'].capitalize()}: {message['content']}")
        print()
        continue

    talk_to_agent(prompt)