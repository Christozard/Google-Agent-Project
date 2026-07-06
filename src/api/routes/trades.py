"""Trade execution endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger("trades_route")


def get_orchestrator():
    from . import get_orchestrator as shared_get
    return shared_get()


class OrderRequest(BaseModel):
    code: str
    qty: int
    price: float
    trd_side: str = "BUY"
    user_approved: bool = False


class UnlockRequest(BaseModel):
    password: str


@router.post("/execute/")
async def execute_trade(request: OrderRequest):
    """Execute a trade order."""
    try:
        orchestrator = get_orchestrator()
        # REAL mode is enforced in MoomooMCPClient - no environment setting needed
        logger.info(f"Trades route: Executing trade, approved={request.user_approved}")
        order_details = {
            "code": request.code,
            "qty": request.qty,
            "price": request.price,
            "trd_side": request.trd_side
        }
        result = orchestrator.run_trade_execution(order_details, user_approved=request.user_approved)
        logger.info(f"Trades route: Trade result - status={result.get("status")}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview/")
async def preview_trade(request: OrderRequest):
    """Preview a trade (check max tradable without executing)."""
    try:
        orchestrator = get_orchestrator()
        # REAL mode is enforced - no environment setting needed
        result = orchestrator.mcp_client.get_max_tradable(
            code=request.code, price=request.price
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unlock/")
async def unlock_trade(request: UnlockRequest):
    """Unlock trade for REAL account."""
    try:
        orchestrator = get_orchestrator()
        result = orchestrator.mcp_client.unlock_trade(password=request.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))