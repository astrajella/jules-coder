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
