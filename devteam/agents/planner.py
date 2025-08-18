import json
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def run(goal: str, system_prompt: str, model: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": goal},
        ],
        response_format={"type": "json_object"},
        max_tokens=2048, # Planner might need more tokens
    )
    content = response.choices[0].message.content
    return json.loads(content)
