"""Market monitoring endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


def get_orchestrator():
    from . import get_orchestrator as shared_get
    return shared_get()


class TriggerRequest(BaseModel):
    code: str
    price: float
    condition: str = "BELOW_OR_EQUAL"


@router.post("/trigger/")
async def add_price_trigger(request: TriggerRequest):
    """Add a price trigger for monitoring."""
    try:
        orchestrator = get_orchestrator()
        orchestrator.market_monitoring.add_price_trigger(
            request.code, request.price, request.condition
        )
        return {"status": "success", "message": f"Added trigger for {request.code}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start/")
async def start_monitoring():
    """Start market monitoring."""
    try:
        orchestrator = get_orchestrator()
        orchestrator.market_monitoring.start_monitoring()
        return {"status": "started", "message": "Market monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/")
async def stop_monitoring():
    """Stop market monitoring."""
    try:
        orchestrator = get_orchestrator()
        orchestrator.market_monitoring.stop_monitoring()
        return {"status": "stopped", "message": "Market monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))