import os
import instructor
from openai import OpenAI
from ..schemas import CodeOutput

# Configure the client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Apply the instructor patch
patched_client = instructor.patch(client)

def run(prompt: str, system_prompt: str, model: str, file_path: str, current_content: str, context: str) -> CodeOutput:
    """
    Generates or modifies code using an LLM.
    Returns a validated CodeOutput object.
    """
    user_prompt = f"File: {file_path}\nRequest: {prompt}\n\nRelevant context:\n{context}\n"
    if current_content:
        user_prompt += f"\nHere is the current content of the file:\n```\n{current_content}\n```"

    return patched_client.chat.completions.create(
        model=model,
        response_model=CodeOutput,
        max_retries=3,
        extra_body={"provider": {"require_parameters": True}},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
