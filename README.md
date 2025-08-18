# AI Coder Agent

This project is a full-stack application that uses a team of AI agents to generate code based on a high-level goal.

## Architecture

- **Frontend:** A simple HTML page with Tailwind CSS and vanilla JavaScript.
- **Backend:** A FastAPI server written in Python.
- **AI:** Uses OpenRouter to access various large language models.

## How to Run

1.  **Clone the repository.**

2.  **Set up the environment variables:**
    - Copy the `.env.example` file to a new file named `.env`.
    - Open `.env` and add your OpenRouter API key:
      ```
      OPENROUTER_API_KEY=your_key_here
      ```
    - You can get a free key from [OpenRouter.ai](https://openrouter.ai/).

3.  **Install the Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start the backend server:**
    ```bash
    python server.py
    ```
    The server will start on `http://localhost:8082`.

5.  **Open the frontend:**
    - Open the `devteam/web/ui/dist/index.html` file in your web browser.
    - Alternatively, you can navigate to `http://localhost:8082/ui` in your browser.

## How to Use

1.  Enter a high-level goal in the text area (e.g., "create a python script that prints hello world").
2.  Click the "Start Build" button.
3.  The application will start the build process. The UI will poll the backend for the generated files and display them when the build is complete.

## Project Structure

- `server.py`: The main FastAPI backend server.
- `requirements.txt`: Python dependencies.
- `.env.example`: Example environment file.
- `config/`: Contains the `models.yaml` and `prompts.yaml` configuration files.
- `devteam/`: The main application package.
  - `orchestrator.py`: The main orchestration logic.
  - `agents/`: Contains the individual AI agent logic.
  - `web/ui/dist/`: Contains the frontend HTML, CSS, and JavaScript files.
- `devteam.log`: The log file for the backend server.

## RAG Implementation

This application uses a Retrieval-Augmented Generation (RAG) system to provide context to the AI agents. This allows the agents to make more informed decisions and generate better code.

Here's how it works:

1.  **Conversation History:** As the agents work, every significant action (e.g., refining the goal, creating a plan, writing code, criticizing code) is stored in a `ConversationHistory` object.

2.  **Vector Embeddings:** Each entry in the history is sent to the Voyage AI API, which converts the text into a numerical vector embedding using the `voyage-3.5` model. These embeddings represent the semantic meaning of the text.

3.  **Contextual Retrieval:** Before an agent (like the Planner or Coder) is called, the Orchestrator formulates a query based on the current task. This query is also converted into a vector embedding.

4.  **Semantic Search:** The Orchestrator then performs a cosine similarity search between the query vector and all the vectors in the conversation history. This finds the historical entries that are most semantically similar to the current task.

5.  **Prompt Augmentation:** The top 3 most relevant historical entries are then formatted and inserted into the prompt that is sent to the agent. This provides the agent with the most relevant context, without overwhelming it with the entire conversation history.

This RAG system makes the AI agent team more efficient and effective, as it allows them to "remember" previous steps and build upon them.
