import os
import instructor
from openai import OpenAI
from ..schemas import CriticVerdict

# Configure the client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Apply the instructor patch
patched_client = instructor.patch(client)

def run(prompt: str, system_prompt: str, model: str) -> CriticVerdict:
    """
    Reviews code and provides a verdict using an LLM.
    Returns a validated CriticVerdict object.
    """
    return patched_client.chat.completions.create(
        model=model,
        response_model=CriticVerdict,
        max_retries=3,
        extra_body={"provider": {"require_parameters": True}},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
