import os
import re
import time
from dotenv import load_dotenv
import ollama
from agent import Agent
import json
import re

def sanitize_response(text: str, agent_name: str) -> str:
    # 1. Take ONLY the first paragraph (drops hallucinated 2nd character lines)
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    first_p = paragraphs[0] if paragraphs else text.strip()
    
    # 2. Take only the first line if split by single newline
    first_line = first_p.split("\n")[0].strip()

    # 3. Strip text inside asterisks (*actions*)
    cleaned = re.sub(r'\*.*?\*', '', first_line)

    # 4. Strip any bracketed tags the model accidentally output
    cleaned = re.sub(r'^\s*\[[A-Za-z0-9_]+\]:\s*', '', cleaned)

    # 5. Collapse spaces
    cleaned = re.sub(r' +', ' ', cleaned).strip()

    # 6. Fallback if response came out empty (prevents blank outputs)
    if not cleaned:
        cleaned = "🤔" if agent_name == "Mia" else "😜"

    return f"[{agent_name}]: {cleaned}"

def talk_to_agent(agent_name: str, messages: list):
    model_map = {
        "Mia": "mia-agent",
        "Alex": "alex-agent"
    }
    
    model_name = model_map.get(agent_name)
    if not model_name:
        return

    # Create a clean copy of messages containing only standard Ollama keys
    api_messages = [{"role": m["role"], "content": m["content"]} for m in messages]

    try:
        response = ollama.chat(model=model_name, messages=api_messages)
        # print(response)
        raw_content = response["message"]["content"]
        
        # Sanitize output (strip asterisks/actions)
        clean_content = sanitize_response(raw_content, agent_name=agent_name)

        # Enforce prefix consistency if the model forgot it
        # expected_prefix = f"[{agent_name}]:"
        # if not clean_content.startswith(expected_prefix):
        #     clean_content = f"{expected_prefix} {clean_content}"

        # # Print message directly (prefix is already included)
        print(f"{clean_content}\n")

        # Save to chat history
        messages.append({"role": "assistant", "content": clean_content})

    except Exception as e:
        print(f"❌ Error communicating with {agent_name}: {e}\n")

def chat_orchestrator(messages: list):
    response = ollama.chat(
    model="orchestrator-agent",
    messages=messages,
    format="json"
)

    raw_content = response["message"]["content"]

    try:
        decision = json.loads(raw_content)
        responders = decision.get("responders", [])

    except json.JSONDecodeError:
        print("❌ Orchestrator returned invalid JSON:")
        print(raw_content)
        return
    print(f"Orchestrator decided to respond with: {responders}\n")
    for agent_name in responders:
        talk_to_agent(agent_name, messages)

def main():
    print("Ollama Chatbot Initialized! (Type '/exit' to quit)\n")
    messages = []
    name = input("Enter your name: ").strip() or "You"

    while True:
        prompt = input(f"[{name}]: ").strip()
        
        if not prompt:
            continue

        if prompt.lower() == "/exit":
            break

        if prompt.lower() == "/help":
            print("\nCommands:\n  /exit - Exit chat\n  /reset - Reset chat session\n  /help - Show help\n  /history - Show chat history\n")
            continue

        if prompt.lower() == "/reset":
            messages.clear()
            print(" Chat history cleared.\n")
            continue

        if prompt.lower() == '/history':
            print("\n--- Chat History ---")
            for msg in messages:
                print(f"{msg['speaker'].capitalize()}: {msg['content']}")
            print("--------------------\n")
            continue

        # Format user prompt with name tag for multi-agent awareness
        formatted_prompt = f"[{name}]: {prompt}"
        messages.append({"role": "user", "content": formatted_prompt})

        # Trigger sequential agent responses
        chat_orchestrator(messages)
        # talk_to_agent("Mia", messages)
        # talk_to_agent("Alex", messages)

if __name__ == "__main__":
    main()