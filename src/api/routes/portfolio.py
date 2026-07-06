"""Portfolio health and rebalancing endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


def get_orchestrator():
    from . import get_orchestrator as shared_get
    return shared_get()


class RebalanceRequest(BaseModel):
    target_allocation: Dict[str, float]


@router.get("/health/")
async def get_portfolio_health():
    """Get portfolio health analysis."""
    try:
        orchestrator = get_orchestrator()
        health = orchestrator.run_portfolio_analyzer()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebalance/")
async def rebalance_portfolio(request: RebalanceRequest):
    """Generate portfolio rebalancing plan."""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.portfolio_rebalancer.rebalance_portfolio(
            request.target_allocation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
