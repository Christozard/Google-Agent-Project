from src.agents.base_agent import BaseAgent

class ProductStrategist(BaseAgent):
    def __init__(self):
        super().__init__("Product Strategist", "Product Direction")

    def execute_task(self, task_description: str):
        self.log_activity(f"Strategizing: {task_description}")
        # Logic to update requirements.md and tasks.md
        self.write_memory("requirements.md", f"\n## New Requirement\n- {task_description}", append=True)
        self.write_memory("tasks.md", f"\n- [ ] {task_description}", append=True)
        return f"Product Strategist has added {task_description} to requirements and tasks."

class SystemArchitect(BaseAgent):
    def __init__(self):
        super().__init__("System Architect", "Technical Design")

    def execute_task(self, task_description: str):
        self.log_activity(f"Designing: {task_description}")
        # Logic to update architecture.md and decisions.md
        self.write_memory("architecture.md", f"\n## Design Detail\n- {task_description}", append=True)
        self.write_memory("decisions.md", f"\n## Decision: {task_description}\n- Rationale: Technical necessity", append=True)
        return f"System Architect has updated architecture and decisions for {task_description}."

class BuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__("Builder Agent", "Code Implementation")

    def execute_task(self, task_description: str):
        self.log_activity(f"Building: {task_description}")
        # Logic to simulate code writing and update progress.md
        self.write_memory("progress.md", f"\n- [x] Implemented: {task_description}", append=True)
        return f"Builder Agent has implemented {task_description}."

class QADebugAgent(BaseAgent):
    def __init__(self):
        super().__init__("QA & Debug Agent", "Quality Assurance")

    def execute_task(self, task_description: str):
        self.log_activity(f"Testing: {task_description}")
        # Logic to simulate testing and update known_issues.md
        self.write_memory("known_issues.md", f"\n- [ ] Bug found during {task_description}", append=True)
        return f"QA Agent has verified {task_description} and logged issues."

class DevOpsDemoAgent(BaseAgent):
    def __init__(self):
        super().__init__("DevOps & Demo Agent", "Deployment & Documentation")

    def execute_task(self, task_description: str):
        self.log_activity(f"Deploying/Documenting: {task_description}")
        # Logic to update README.md or deployment guides
        self.write_memory("README.md", f"\n## Update\n- {task_description}", append=True)
        return f"DevOps Agent has updated documentation for {task_description}."