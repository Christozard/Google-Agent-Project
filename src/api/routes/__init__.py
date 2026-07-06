"""API route routers package."""
# Shared orchestrator singleton - defined first
_orchestrator = None


import os

def get_orchestrator():
    """Get or create the shared InvestmentOrchestrator instance."""
    global _orchestrator
    from src.agents.runtime.investment_orchestrator import InvestmentOrchestrator
    
    # REAL mode is enforced in MoomooMCPClient - no environment check needed
    
    if _orchestrator is None:
        _orchestrator = InvestmentOrchestrator()

    return _orchestrator



def reset_orchestrator():
    """Reset the orchestrator (useful for testing)."""
    global _orchestrator
    if _orchestrator:
        _orchestrator.close()
    _orchestrator = None


# Import routers after singleton definition
from .goals import router as goals_router  # noqa: E402
from .portfolio import router as portfolio_router  # noqa: E402
from .research import router as research_router  # noqa: E402
from .trades import router as trades_router  # noqa: E402
