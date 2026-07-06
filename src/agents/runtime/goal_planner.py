from typing import Dict, Any, List, Optional
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoalPlanner")

class GoalPlanner:
    """
    Runtime agent that decomposes high-level investment goals into 
    structured objectives and actionable tasks using real LLM-driven logic.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize the GoalPlanner.
        Args:
            llm_client: An optional LLM client for generating dynamic plans.
        """
        self.llm_client = llm_client

    def _generate_llm_prompt(self, user_data: Dict[str, Any]) -> str:
        """
        Constructs a detailed prompt for the LLM to decompose the user's goal.
        """
        age = user_data.get("age", "unknown")
        time_horizon = user_data.get("time_horizon", "unknown")
        risk_appetite = user_data.get("risk_appetite", "unknown")
        goals = user_data.get("goals", "general wealth growth")
        
        prompt = f"""As an expert financial advisor AI, decompose the following user investment goal into specific, measurable, achievable, relevant, and time-bound (SMART) objectives. Also, infer a risk profile (Conservative, Moderate, Aggressive) and suggest a target asset allocation based on the user's data. Avoid placeholders and provide real, actionable advice. 

User Data:
- Age: {age}
- Time Horizon: {time_horizon} years
- Risk Appetite (1-10, 10 being highest): {risk_appetite}
- Goals: {goals}

Provide the output in a JSON-like structure with keys: 'risk_profile', 'risk_score', 'target_allocation', 'expected_return', and 'objectives' (a list of SMART objectives)."
"""
        return prompt

    def decompose_goal(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decomposes a user's high-level goal into structured objectives using LLM (if available) 
        or a robust rule-based system.
        
        Args:
            user_data: Dictionary containing 'age', 'time_horizon', 'risk_appetite', 'goals'
        """
        logger.info("Decomposing investment goals...")
        
        if self.llm_client:
            # In a real scenario, this would call the LLM API
            prompt = self._generate_llm_prompt(user_data)
            logger.info("Calling LLM for goal decomposition...")
            # Simulate LLM response for now, to be replaced with actual LLM call
            llm_response_text = self._simulate_llm_response(user_data)
            # Parse LLM response into the expected dictionary format
            return json.loads(llm_response_text) # Assumes LLM returns valid JSON
        else:
            # Robust rule-based system as a fallback/initial implementation
            risk_appetite = user_data.get("risk_appetite", 5)
            age = user_data.get("age", 30)
            horizon = user_data.get("time_horizon", 10)
            goals_text = user_data.get("goals", "General wealth growth")

            # Weighted scoring for risk profile
            risk_score = (risk_appetite * 0.5) + (horizon * 0.3) - (age * 0.2)
            risk_score = max(1, min(10, round(risk_score)))
            
            if risk_score <= 4:
                profile = "Conservative"
                allocation = {"Bonds": 70, "Equities": 20, "Cash": 10}
                target_return = "3-5%"
            elif risk_score <= 7:
                profile = "Moderate"
                allocation = {"Bonds": 40, "Equities": 50, "Cash": 10}
                target_return = "6-8%"
            else:
                profile = "Aggressive"
                allocation = {"Bonds": 10, "Equities": 80, "Cash": 10}
                target_return = "10%+"

            objectives = [
                f"Establish a {profile} risk profile (score: {risk_score}) suitable for {age} years old with a {horizon} year horizon.",
                f"Target an annual return of {target_return} while managing risk.",
                f"Optimize asset allocation according to {allocation} to achieve diversification.",
                f"Address specific goal: {goals_text}."
            ]

            return {
                "risk_profile": profile,
                "risk_score": risk_score,
                "target_allocation": allocation,
                "expected_return": target_return,
                "objectives": objectives,
                "decomposition_status": "Complete (Rule-based)"
            }

    def _simulate_llm_response(self, user_data: Dict[str, Any]) -> str:
        """
        Simulates an LLM response for goal decomposition.
        This would be replaced by an actual LLM API call.
        """
        risk_appetite = user_data.get("risk_appetite", 5)
        age = user_data.get("age", 30)
        horizon = user_data.get("time_horizon", 10)
        goals_text = user_data.get("goals", "General wealth growth")

        risk_score = (risk_appetite * 0.5) + (horizon * 0.3) - (age * 0.2)
        risk_score = max(1, min(10, round(risk_score)))

        if risk_score <= 4:
            profile = "Conservative"
            allocation = {"Bonds": 70, "Equities": 20, "Cash": 10}
            target_return = "3-5%"
        elif risk_score <= 7:
            profile = "Moderate"
            allocation = {"Bonds": 40, "Equities": 50, "Cash": 10}
            target_return = "6-8%"
        else:
            profile = "Aggressive"
            allocation = {"Bonds": 10, "Equities": 80, "Cash": 10}
            target_return = "10%+"

        objectives = [
            f"Establish a {profile} risk profile (score: {risk_score}) suitable for {age} years old with a {horizon} year horizon.",
            f"Target an annual return of {target_return} while managing risk.",
            f"Optimize asset allocation according to {allocation} to achieve diversification.",
            f"Address specific goal: {goals_text}."
        ]

        return json.dumps({
            "risk_profile": profile,
            "risk_score": risk_score,
            "target_allocation": allocation,
            "expected_return": target_return,
            "objectives": objectives,
            "decomposition_status": "Complete (Simulated LLM)"
        }, indent=4)

if __name__ == "__main__":
    import json # Import json for standalone test
    planner = GoalPlanner()
    test_user = {"age": 30, "time_horizon": 20, "risk_appetite": 8, "goals": "Buy a house in 5 years"}
    print(f"Decomposed Goals: {planner.decompose_goal(test_user)}")
