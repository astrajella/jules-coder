from .agents import supervisor, planner, coder, critic
import yaml
from pathlib import Path
from .logger import logger
from . import rag
from . import schemas
import asyncio

class Orchestrator:
    def __init__(self, session_id: str, voyage_api_key: str):
        self.session_id = session_id
        self.voyage_api_key = voyage_api_key
        self.file_system = {}
        self.history = rag.ConversationHistory(voyage_api_key)

        config_path = Path(__file__).resolve().parent.parent / "config"
        with open(config_path / "prompts.yaml", "r") as f:
            self.prompts = yaml.safe_load(f)
        with open(config_path / "models.yaml", "r") as f:
            self.models = yaml.safe_load(f)

    def get_model(self, role: str) -> str:
        return self.models["roles"].get(role, self.models["fallbacks"][role])

    async def run(self, high_level_goal: str):
        logger.info(f"[{self.session_id}] Starting build with Instructor for: {high_level_goal}")
        await self.history.add_entry("user", high_level_goal)
        await asyncio.sleep(20)

        # 1. Supervisor
        logger.info(f"[{self.session_id}] Calling Supervisor...")
        refined_goal_obj = supervisor.run(
            high_level_goal,
            self.prompts["supervisor"]["system"],
            self.get_model("supervisor")
        )
        refined_goal = refined_goal_obj.high_level_goal
        logger.info(f"[{self.session_id}] Refined goal: {refined_goal}")
        await self.history.add_entry("supervisor", f"Refined goal: {refined_goal}")
        await asyncio.sleep(20)

        # 2. Planner
        logger.info(f"[{self.session_id}] Calling Planner...")
        context = await self.history.get_relevant_context(refined_goal)
        planner_prompt = f"High-level goal: {refined_goal}\n\nRelevant context:\n{context}"
        build_plan = planner.run(
            planner_prompt,
            self.prompts["planner"]["system"],
            self.get_model("planner")
        )
        logger.info(f"[{self.session_id}] Plan: {build_plan.plan_description}")
        await self.history.add_entry("planner", f"Created a plan: {build_plan.model_dump_json(indent=2)}")
        await asyncio.sleep(20)

        # 3. Coder & Critic Loop
        for file_creation_instruction in build_plan.files_to_create:
            file_path = file_creation_instruction.file_path
            prompt = f"Create the file `{file_path}` with the following code."

            logger.info(f"[{self.session_id}] Executing instruction for: {file_path}")

            # Coder
            code_output = coder.run(
                prompt=prompt,
                system_prompt=self.prompts["coder"]["system"],
                model=self.get_model("coder"),
                file_path=file_path,
                current_content="", # Always creating new files in this simplified plan
                context=f"The overall plan is: {build_plan.plan_description}"
            )

            # Critic
            logger.info(f"[{self.session_id}] Calling Critic for {file_path}...")
            critic_prompt = f"Original request: {prompt}\n\nProposed code for {file_path}:\n```\n{code_output.content}\n```"
            verdict = critic.run(
                critic_prompt,
                self.prompts["critic"]["system"],
                self.get_model("critic")
            )

            if verdict.status == "APPROVED":
                logger.info(f"[{self.session_id}] Critic approved the code for {file_path}.")
                self.file_system[file_path] = code_output.content
                await self.history.add_entry("coder", f"Wrote code for {file_path}:\n{code_output.content}", is_code=True)
                await asyncio.sleep(20)
                await self.history.add_entry("critic", f"Approved code for {file_path}.")
                await asyncio.sleep(20)
            else:
                logger.warning(f"[{self.session_id}] Critic rejected code for {file_path}. Feedback: {verdict.feedback}")
                await self.history.add_entry("critic", f"Rejected code for {file_path}. Feedback: {verdict.feedback}")
                await asyncio.sleep(20)

    def get_files(self):
        return self.file_system
