import json
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def run(prompt: str, system_prompt: str, model: str, file_path: str, current_content: str) -> str:

    user_prompt = f"File: {file_path}\nRequest: {prompt}\n"
    if current_content:
        user_prompt += f"\nHere is the current content of the file:\n```\n{current_content}\n```"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=4096, # Coder needs a lot of tokens
    )
    content = response.choices[0].message.content
    return json.loads(content).get("content", "")
