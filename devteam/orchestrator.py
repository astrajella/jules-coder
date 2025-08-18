from .agents import supervisor, planner, coder, critic
import yaml
from pathlib import Path
from .logger import logger
from . import rag
import asyncio

class Orchestrator:
    def __init__(self, session_id: str, voyage_api_key: str):
        self.session_id = session_id
        self.voyage_api_key = voyage_api_key
        self.file_system = {}
        self.history = rag.ConversationHistory(voyage_api_key)

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
        await self.history.add_entry("user", high_level_goal)
        await asyncio.sleep(20)

        # 1. Supervisor
        logger.info(f"[{self.session_id}] Calling Supervisor...")
        refined_goal = supervisor.run(
            high_level_goal,
            self.prompts["supervisor"]["system"],
            self.get_model("supervisor")
        )
        logger.info(f"[{self.session_id}] Refined goal: {refined_goal}")
        await self.history.add_entry("supervisor", f"Refined goal: {refined_goal}")
        await asyncio.sleep(20)

        # 2. Planner
        logger.info(f"[{self.session_id}] Calling Planner...")
        context = await self.history.get_relevant_context(refined_goal)
        planner_prompt = f"High-level goal: {refined_goal}\n\nRelevant context:\n{context}"
        plan = planner.run(
            planner_prompt,
            self.prompts["planner"]["system"],
            self.get_model("planner")
        )
        logger.info(f"[{self.session_id}] Plan: {plan}")
        await self.history.add_entry("planner", f"Created a plan: {plan}")
        await asyncio.sleep(20)

        # 3. Coder & Critic Loop
        for step in plan.get("plan", []):
            file_path = step.get("file")
            prompt = step.get("prompt")

            logger.info(f"[{self.session_id}] Executing step: {step}")
            current_content = self.file_system.get(file_path, "")

            context = await self.history.get_relevant_context(prompt)
            await asyncio.sleep(20)

            # Coder
            new_content = coder.run(
                prompt,
                self.prompts["coder"]["system"],
                self.get_model("coder"),
                file_path,
                current_content,
                context
            )

            # Critic
            logger.info(f"[{self.session_id}] Calling Critic...")
            critic_prompt = f"Original request: {prompt}\n\nProposed code:\n```\n{new_content}\n```"
            critic_response = critic.run(
                critic_prompt,
                self.prompts["critic"]["system"],
                self.get_model("critic")
            )

            if critic_response.get("status") == "APPROVED":
                logger.info(f"[{self.session_id}] Critic approved the code for {file_path}.")
                self.file_system[file_path] = new_content
                await self.history.add_entry("coder", f"Wrote code for {file_path}:\n{new_content}", is_code=True)
                await asyncio.sleep(20)
                await self.history.add_entry("critic", f"Approved code for {file_path}.")
                await asyncio.sleep(20)
            else:
                logger.warning(f"[{self.session_id}] Critic rejected the code for {file_path}.")
                await self.history.add_entry("critic", f"Rejected code for {file_path}. Feedback: {critic_response.get('feedback')}")
                await asyncio.sleep(20)

    def get_files(self):
        return self.file_system
