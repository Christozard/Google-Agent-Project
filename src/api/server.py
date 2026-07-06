"""
FastAPI backend for Moomoo Investment Agent.
Provides REST API endpoints for all 7 investment features.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# Load .env file at startup
load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

app = FastAPI(title="Moomoo Investment Agent API", description="REST API for AI-powered investment management", version="1.0.0")

# Include all common Vite ports
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from src.api.routes import portfolio, research, trades, goals, monitoring

app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(research.router, prefix="/api/research", tags=["research"])
app.include_router(trades.router, prefix="/api/trade", tags=["trades"])
app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "Moomoo Investment Agent API"}


@app.get("/api/config")
async def get_config():
    return {"trd_env": os.environ.get("MOOMOO_TRADING_ENV", "SIMULATE"), "security_firm": os.environ.get("MOOMOO_SECURITY_FIRM", "FUTUSG")}


class EnvRequest(BaseModel):
    trd_env: str


@app.post("/api/set-env")
async def set_env(request: EnvRequest):
    """Persist trading environment selection for session."""
    os.environ["MOOMOO_TRADING_ENV"] = request.trd_env
    return {"success": True, "trd_env": request.trd_env}


class ConnectRequest(BaseModel):
    trd_env: str = "SIMULATE"
    security_firm: str = "FUTUSG"
    host: str = "127.0.0.1"
    port: int = 11111


@app.post("/api/connect")
async def connect_to_opend(request: ConnectRequest):
    """Connect to Moomoo OpenD and set environment."""
    try:
        from src.api.routes import get_orchestrator
        orchestrator = get_orchestrator()
        orchestrator.mcp_client.set_environment(request.trd_env)
        connected = orchestrator.mcp_client.connect()
        if connected:
            return {"success": True, "message": f"Connected to OpenD in {request.trd_env} mode"}
        else:
            return {"success": False, "message": "Failed to connect - check OpenD is running on port 11111"}
    except Exception as e:
        return {"success": False, "message": str(e)}


class PasswordRequest(BaseModel):
    password: str


@app.post("/api/verify-password")
async def verify_password(request: PasswordRequest):
    """
    Verify trade password against .env configuration.
    If match, set _trade_unlocked flag for REAL trading.
    """
    expected_password = os.environ.get("MOOMOO_TRADE_PASSWORD", "")
    if not expected_password:
        return {"success": False, "message": "No password configured in .env"}
    
    if request.password == expected_password:
        # Set trade_unlocked on the orchestrator's MCP client
        try:
            from src.api.routes import get_orchestrator
            orchestrator = get_orchestrator()
            orchestrator.mcp_client._trade_unlocked = True
            return {"success": True, "message": "Password verified - REAL trading unlocked"}
        except Exception as e:
            return {"success": True, "message": "Password verified"}
    else:
        return {"success": False, "message": "Password mismatch"}
