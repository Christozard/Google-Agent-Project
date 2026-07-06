"""
API Integration Tests for Moomoo Investment Agent.
Tests FastAPI endpoints with mocked orchestrator.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIEndpoints:
    """Test all API endpoints."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mocked orchestrator."""
        mock = MagicMock()
        mock.mcp_client.connected = True
        mock.run_goal_planner.return_value = {
            "risk_profile": "Moderate",
            "risk_score": 5,
            "target_allocation": {"Tech": 0.6, "Finance": 0.4}
        }
        mock.run_portfolio_analysis.return_value = {
            "diversification_score": 0.8,
            "sector_allocation": {"Tech": 0.5},
            "total_positions": 5
        }
        mock.run_market_research.return_value = {
            "research_results": [{"code": "US.AAPL", "recommendation": "BUY"}],
            "status": "complete"
        }
        mock.execute_trade.return_value = {
            "status": "success",
            "order_id": "12345"
        }
        return mock
    
    @pytest.fixture
    def client(self, mock_orchestrator):
        """Create test client with mocked orchestrator."""
        with patch('src.api.routes.portfolio.get_orchestrator', return_value=mock_orchestrator):
            with patch('src.api.routes.research.get_orchestrator', return_value=mock_orchestrator):
                with patch('src.api.routes.trades.get_orchestrator', return_value=mock_orchestrator):
                    with patch('src.api.routes.goals.get_orchestrator', return_value=mock_orchestrator):
                        from src.api.server import app
                        yield TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_config_endpoint(self, client):
        """Test config endpoint."""
        response = client.get("/api/config")
        assert response.status_code == 200
    
    def test_goal_planner_endpoint(self, client, mock_orchestrator):
        """Test goal planner API."""
        response = client.post("/api/goals/plan/", json={
            "age": 30,
            "risk_appetite": 7,
            "time_horizon": 5
        })
        assert response.status_code == 200
        assert response.json()["risk_profile"] == "Moderate"
    
    def test_portfolio_health_endpoint(self, client, mock_orchestrator):
        """Test portfolio health API."""
        response = client.get("/api/portfolio/health/")
        assert response.status_code == 200
        assert "diversification_score" in response.json()
    
    def test_market_research_endpoint(self, client, mock_orchestrator):
        """Test market research API."""
        response = client.post("/api/research/", json={
            "tickers": ["US.AAPL", "US.MSFT"]
        })
        assert response.status_code == 200
        assert "research_results" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])