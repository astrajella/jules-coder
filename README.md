# AI Coder Agent

## Overview

The AI Coder Agent is a sophisticated, full-stack application designed to autonomously generate production-ready code from high-level user prompts. It leverages a multi-agent team, each with a specialized role, to interpret user requirements, create a development plan, write the code, and review it for quality.

This project's core is a **proactive, enforcement-based architecture** that uses the `instructor` library to ensure all AI-generated outputs conform to a strict, predefined data schema. This eliminates common failure points related to JSON parsing and makes the system significantly more robust, predictable, and maintainable.

## Key Features

-   **Multi-Agent System:** A team of specialized AI agents (Supervisor, Planner, Coder, Critic) collaborate to deliver high-quality code.
-   **Structured AI Outputs:** Powered by the `instructor` library, all agent responses are validated Pydantic data objects, not unpredictable JSON strings.
-   **Retrieval-Augmented Generation (RAG):** A `ConversationHistory` module provides relevant context to agents at each step, enabling them to make more informed decisions.
-   **Self-Correction:** Agents are configured to automatically retry and self-correct if their initial output fails validation.
-   **Configurable & Extensible:** Agent roles, AI models, and prompts are all configurable through simple YAML files, making the system easy to extend and adapt.

## How It Works

The application follows a structured, multi-step process to convert a user's goal into functional code:

1.  **Goal Refinement (Supervisor):** The user's initial prompt is sent to the **Supervisor** agent, which refines it into a clear, actionable goal. The response is guaranteed to be a `RefinedGoal` Pydantic object.

2.  **Planning (Planner):** The refined goal is passed to the **Planner** agent. The Planner creates a comprehensive `BuildPlan`, detailing every file that needs to be created, including its full path and source code. This structured plan is enforced by `instructor`.

3.  **Code Generation (Coder & Critic Loop):** The **Orchestrator** iterates through the `BuildPlan`. For each file:
    a.  The **Coder** agent receives the instruction and generates the code, returning a validated `CodeOutput` object.
    b.  The generated code is then passed to the **Critic** agent, which reviews it against the original request. The Critic returns a `CriticVerdict` object, either "APPROVED" or "REJECTED".
    c.  If approved, the file is saved to the in-memory file system. If rejected, the process logs the feedback (in a full implementation, this would trigger a debugging loop).

4.  **Contextual Awareness (RAG):** Throughout this process, each significant action and output is vectorized using Voyage AI's `voyage-3.5` model and stored in a `ConversationHistory` object. Before calling the Planner or Coder, the Orchestrator performs a semantic search to retrieve the most relevant historical context, which is then added to the agent's prompt.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    -   Copy `.env.example` to a new file named `.env`.
    -   Add your API keys to the `.env` file:
        ```env
        OPENROUTER_API_KEY="your_openrouter_key"
        VOYAGE_API_KEY="your_voyage_api_key"
        ```

## Running the Application

1.  **Start the Backend Server:**
    ```bash
    python server.py
    ```
    The server will start on `http://localhost:8082` by default.

2.  **Access the Frontend:**
    -   Open the `devteam/web/ui/dist/index.html` file directly in your browser.
    -   Alternatively, navigate to `http://localhost:8082/ui`.

## Usage

1.  Enter a high-level development goal in the text area. For example: *"Create a Python script that uses the requests library to fetch and print the title of the Google homepage."*
2.  Click the "Start Build" button.
3.  The application will begin the code generation process. The UI will poll the backend every few seconds to check for the completed files.
4.  Once the build is complete, the generated files will appear in the "Generated Code" section, with tabs to switch between them.

## Project Structure

```
.
├── config/
│   ├── models.yaml       # Configure AI models for each agent
│   └── prompts.yaml      # Configure system prompts for each agent
├── devteam/
│   ├── agents/           # Contains the logic for each individual agent
│   │   ├── coder.py
│   │   ├── critic.py
│   │   ├── planner.py
│   │   └── supervisor.py
│   ├── web/ui/dist/      # Frontend HTML, JS, and CSS files
│   ├── logger.py         # Application logger setup
│   ├── orchestrator.py   # Main orchestration logic
│   ├── rag.py            # RAG and conversation history module
│   └── schemas.py        # Pydantic schemas for structured outputs
├── .env                  # Local environment variables (API keys)
├── .env.example          # Example environment file
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── server.py             # Main FastAPI server
```
