import os
from dotenv import load_dotenv
from litellm import completion
import json
import chainlit as cl


load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY is not set. Please ensure it is defined in your .env file.")


@cl.on_chat_start
async def start():
    cl.user_session.set("chat_history", [])
    await cl.Message(content="How can I help you today?").send()


@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()

    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        response =  completion(
            model="mistralai/devstral-small:free",
            api_key=openrouter_api_key,
            api_base="https://openrouter.ai/api/v1",
            messages=history,  
            stream=True  
        )

        full_response = ""
        async for chunk in response:
            token = chunk.choices[0].delta.get("content", "")
            full_response += token
            await msg.stream_token(token)

        await msg.update()

        history.append({"role": "assistant", "content": full_response})
        cl.user_session.set("chat_history", history)
        print(f"user: {message.content}")
        print(f"Assistant: {full_response}")

    except Exception as e:
        msg.content = f"Error: {str(e)}"
        await msg.update()
        print(f"Error: {str(e)}")


@cl.on_chat_end
async def end():
    history = cl.user_session.get("chat_history") or []
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    print("Chat history saved.")
