"""Goal planner endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


def get_orchestrator():
    from . import get_orchestrator as shared_get
    return shared_get()


class GoalRequest(BaseModel):
    age: int
    risk_appetite: int
    time_horizon: int
    goals: str = "general wealth growth"


@router.post("/plan/")
async def generate_goal_plan(request: GoalRequest):
    """Generate investment plan from goals."""
    try:
        orchestrator = get_orchestrator()
        user_data = {
            "age": request.age,
            "risk_appetite": request.risk_appetite,
            "time_horizon": request.time_horizon,
            "goals": request.goals
        }
        result = orchestrator.run_goal_planner(user_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))