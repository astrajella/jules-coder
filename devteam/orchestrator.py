from .agents import supervisor, planner, coder
import yaml
from pathlib import Path
from .logger import logger

class Orchestrator:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.file_system = {}

        # Load prompts
        config_path = Path(__file__).resolve().parent.parent / "config"
        with open(config_path / "prompts.yaml", "r") as f:
            self.prompts = yaml.safe_load(f)
        with open(config_path / "models.yaml", "r") as f:
            self.models = yaml.safe_load(f)

    def get_model(self, role: str) -> str:
        return self.models["roles"].get(role, self.models["fallbacks"][role])

    async def run(self, high_level_goal: str):
        logger.info(f"[{self.session_id}] Starting build for: {high_level_goal}")

        # 1. Supervisor
        logger.info(f"[{self.session_id}] Calling Supervisor...")
        refined_goal = supervisor.run(
            high_level_goal,
            self.prompts["supervisor"]["system"],
            self.get_model("supervisor")
        )
        logger.info(f"[{self.session_id}] Refined goal: {refined_goal}")

        # 2. Planner
        logger.info(f"[{self.session_id}] Calling Planner...")
        plan = planner.run(
            refined_goal,
            self.prompts["planner"]["system"],
            self.get_model("planner")
        )
        logger.info(f"[{self.session_id}] Plan: {plan}")

        # 3. Coder
        for step in plan.get("plan", []):
            file_path = step.get("file")
            prompt = step.get("prompt")

            logger.info(f"[{self.session_id}] Executing step: {step}")
            current_content = self.file_system.get(file_path, "")

            new_content = coder.run(
                prompt,
                self.prompts["coder"]["system"],
                self.get_model("coder"),
                file_path,
                current_content
            )

            self.file_system[file_path] = new_content
            logger.info(f"[{self.session_id}] Updated {file_path}")

    def get_files(self):
        return self.file_system
