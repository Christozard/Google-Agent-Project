import unittest
import os
from src.api.mcp_client import MoomooMCPClient
from src.agents.development.dev_agents import ProductStrategist, SystemArchitect

class TestPhase2Infrastructure(unittest.TestCase):
    def setUp(self):
        self.client = MoomooMCPClient()
        self.client.connect()
        self.strategist = ProductStrategist()
        self.architect = SystemArchitect()

    def test_mcp_connection_and_safety(self):
        """Verify MCP client connection and trade safety."""
        # Test connection
        self.assertTrue(self.client.connected)
        
        # Test safety: Trade should be rejected without approval
        order = {"code": "US.AAPL", "qty": 10, "price": 150.0, "side": "BUY"}
        result = self.client.execute_trade(order, user_approved=False)
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "User approval required")
        
        # Test safety: Trade should succeed with approval
        result = self.client.execute_trade(order, user_approved=True)
        self.assertEqual(result["status"], "success")

    def test_dev_agents_memory_updates(self):
        """Verify that development agents correctly update shared memory files."""
        # Test Product Strategist
        req_text = "Implement a Portfolio Health Dashboard"
        self.strategist.execute_task(req_text)
        
        with open("requirements.md", "r") as f:
            content = f.read()
            self.assertIn(req_text, content)
            
        with open("tasks.md", "r") as f:
            content = f.read()
            self.assertIn(req_text, content)

        # Test System Architect
        arch_text = "Use a Singleton pattern for the MCP Client"
        self.architect.execute_task(arch_text)
        
        with open("architecture.md", "r") as f:
            content = f.read()
            self.assertIn(arch_text, content)
            
        with open("decisions.md", "r") as f:
            content = f.read()
            self.assertIn(arch_text, content)

    def test_activity_logging(self):
        """Verify that agent activities are logged to progress.md."""
        self.strategist.execute_task("Test logging")
        with open("progress.md", "r") as f:
            content = f.read()
            self.assertIn("[Product Strategist] Strategizing: Test logging", content)

if __name__ == "__main__":
    unittest.main()