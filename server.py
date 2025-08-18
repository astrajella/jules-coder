import uvicorn
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from devteam.orchestrator import Orchestrator
from devteam.logger import logger

# --- Paths ---
APP_ROOT = Path(__file__).resolve().parent
UI_DIST = APP_ROOT / "devteam" / "web" / "ui" / "dist"

# --- FastAPI app ---
app = FastAPI(title="AI Coder")
app.mount("/ui", StaticFiles(directory=UI_DIST, html=True), name="ui")

# In-memory session store
sessions = {}

@app.post("/start")
async def start_build(request: dict = Body(...)):
    try:
        logger.info(f"Received build request: {request}")
        prompt = request.get("prompt")
        if not prompt:
            raise HTTPException(400, "prompt required")

        session_id = request.get("session", "default")

        # Create a new orchestrator for the session
        orch = Orchestrator(session_id)
        sessions[session_id] = orch

        # Start the build process in the background
        await orch.run(prompt)

        logger.info(f"Build process started for session: {session_id}")
        return {"session_id": session_id, "message": "Build started."}
    except Exception as e:
        logger.error(f"Error in start_build: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/files")
def list_files(session_id: str = "default"):
    orch = sessions.get(session_id)
    if not orch:
        raise HTTPException(404, "Session not found")
    return {"files": orch.get_files()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
