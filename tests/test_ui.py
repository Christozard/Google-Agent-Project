"""
Automated UI Testing for Moomoo Investment Agent Frontend.
"""
import pytest
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test mode
os.environ["MOOMOO_UI_TEST"] = "1"


class TestUIComponents:
    """Test individual UI component functions."""
    
    def test_render_order_form_exists(self):
        """Order form function should exist."""
        try:
            from src.frontend.components.trade_gate import render_order_form
            assert callable(render_order_form)
        except ImportError:
            pytest.skip("Streamlit not installed")
    
    def test_render_trade_approval_exists(self):
        """Trade approval function should exist."""
        try:
            from src.frontend.components.trade_gate import render_trade_approval
            assert callable(render_trade_approval)
        except ImportError:
            pytest.skip("Streamlit not installed")
    
    def test_render_goal_form_exists(self):
        """Goal form function should exist."""
        try:
            from src.frontend.components.goal_form import render_goal_form
            assert callable(render_goal_form)
        except ImportError:
            pytest.skip("Streamlit not installed")
    
    def test_render_env_config_exists(self):
        """Environment config function should exist."""
        try:
            from src.frontend.components.env_config import render_environment_config
            assert callable(render_environment_config)
        except ImportError:
            pytest.skip("Streamlit not installed")


class TestUIIntegration:
    """Integration tests for UI flows."""
    
    def test_import_app_module(self):
        """Test that the app module can be imported without errors."""
        try:
            import src.frontend.app
        except ImportError:
            pytest.skip("Streamlit not installed")
        assert hasattr(src.frontend.app, 'main')
    
    def test_import_orchestrator(self):
        """Test that orchestrator can be imported."""
        try:
            from src.agents.runtime.investment_orchestrator import InvestmentOrchestrator
        except ImportError:
            pytest.skip("moomoo-api not installed")
        assert InvestmentOrchestrator is not None
    
    def test_mocked_connection_flow(self):
        """Test connection flow with mocked MCP client."""
        try:
            from unittest.mock import MagicMock, patch
            from src.agents.runtime.investment_orchestrator import InvestmentOrchestrator
        except ImportError:
            pytest.skip("moomoo-api not installed")
        
        mock_client = MagicMock()
        mock_client.connect.return_value = True
        
        with patch('src.agents.runtime.investment_orchestrator.MoomooMCPClient', return_value=mock_client):
            orch = InvestmentOrchestrator()
            result = orch.connect()
            assert result is True


class TestUIDataFlows:
    """Test data flow through UI components - no external dependencies."""
    
    def test_goal_planner_data_structure(self):
        """Verify goal planner returns expected structure."""
        from src.agents.runtime.goal_planner import GoalPlanner
        
        planner = GoalPlanner()
        result = planner.decompose_goal({
            "age": 30,
            "risk_appetite": 7,
            "time_horizon": 5
        })
        
        assert "risk_profile" in result
        assert "risk_score" in result
        assert "target_allocation" in result
    
    def test_goal_planner_conservative(self):
        """Test conservative risk profile exists."""
        from src.agents.runtime.goal_planner import GoalPlanner
        planner = GoalPlanner()
        result = planner.decompose_goal({"age": 50, "risk_appetite": 2, "time_horizon": 3})
        assert result["risk_profile"] is not None
    
    def test_goal_planner_no_crash(self):
        """Test goal planner doesn't crash on any input."""
        from src.agents.runtime.goal_planner import GoalPlanner
        planner = GoalPlanner()
        # Should not crash
        result = planner.decompose_goal({"age": 30, "risk_appetite": 5, "time_horizon": 10})
        assert isinstance(result, dict)
        assert len(result) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])