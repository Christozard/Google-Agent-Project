"""Market research endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()


def get_orchestrator():
    from . import get_orchestrator as shared_get
    return shared_get()


class ResearchRequest(BaseModel):
    tickers: List[str]


@router.post("/")
async def research_securities(request: ResearchRequest):
    """Research multiple securities."""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.run_market_research(request.tickers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/committee/")
async def run_investment_committee(request: ResearchRequest):
    """Run investment committee analysis."""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.run_investment_committee(request.tickers)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))