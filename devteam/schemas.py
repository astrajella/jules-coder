from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RefinedGoal(BaseModel):
    high_level_goal: str = Field(..., description="The refined, specific, and actionable high-level goal.")

class FileCreation(BaseModel):
    file_path: str = Field(..., description="The full path of the file to create.")
    code: str = Field(..., description="The complete source code for the file.")

class BuildPlan(BaseModel):
    plan_description: str = Field(..., description="A short, user-facing summary of the build plan.")
    files_to_create: List[FileCreation] = Field(..., description="A list of all files that need to be created to complete the goal.")

class CodeOutput(BaseModel):
    file: str = Field(..., description="The full path of the file that was modified or created.")
    content: str = Field(..., description="The new, complete source code for the file.")

class CriticVerdict(BaseModel):
    status: Literal["APPROVED", "REJECTED"] = Field(..., description="The verdict on the code proposal.")
    feedback: Optional[str] = Field(None, description="Detailed feedback if the code is rejected, explaining what needs to be fixed.")
