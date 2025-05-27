import os
from dotenv import load_dotenv, find_dotenv
from litellm import completion
import json
import chainlit as cl

load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL")

conversation = []

@cl.on_chat_start
async def start():
    await cl.Message(content="Hi! I am your chatbot. Ask me anything.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    user_message = message.content
    conversation.append({"role": "user", "content": user_message})

    full_response = ""
    bot_message = cl.Message(content="")

    
    async for chunk in completion(
        model=gemini_model,
        messages=[{"role": "user", "content": user_message}],
        api_key=gemini_api_key,
        stream=True
    ):
        delta = chunk.choices[0].delta.content or ""
        full_response += delta
        await bot_message.stream_token(delta)

    await bot_message.send()
    conversation.append({"role": "assistant", "content": full_response})

@cl.on_chat_end
def end():
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(conversation, f, indent=2, ensure_ascii=False)

