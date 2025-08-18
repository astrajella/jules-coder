import voyageai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class ConversationHistory:
    def __init__(self, voyage_api_key: str):
        self.client = voyageai.AsyncClient(api_key=voyage_api_key)
        self.history = []
        self.embeddings = []

    async def add_entry(self, role: str, content: str, is_code: bool = False):
        """Adds a new entry to the conversation history."""
        self.history.append({"role": role, "content": content})

        # We use different input types for code and natural language text.
        input_type = "code" if is_code else "document"

        response = await self.client.embed([content], model="voyage-3.5", input_type=input_type)
        self.embeddings.append(response.embeddings[0])

    async def get_relevant_context(self, query: str, k: int = 3) -> str:
        """
        Gets the most relevant context from the history for a given query.
        """
        if not self.history:
            return "No history yet."

        query_embedding_response = await self.client.embed([query], model="voyage-3.5", input_type="query")
        query_embedding = query_embedding_response.embeddings[0]

        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        context = "Relevant previous steps:\n"
        for i in top_k_indices:
            entry = self.history[i]
            context += f"- {entry['role']}: {entry['content']}\n"

        return context
