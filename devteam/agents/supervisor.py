import json
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def run(high_level_goal: str, system_prompt: str, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": high_level_goal},
        ],
        response_format={"type": "json_object"},
        max_tokens=1024,
    )
    content = response.choices[0].message.content
    return json.loads(content).get("high_level_goal", high_level_goal)
