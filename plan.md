# Agentic Investment Copilot - Hackathon Implementation Plan

This document outlines the step-by-step execution roadmap to build the Agentic Investment Copilot using the **Google Agent Development Kit (ADK)** and the **Moomoo API MCP**: https://github.com/Litash/moomoo-api-mcp.

---

## Phase 1: Environment & SDK Setup

Goal: Install `uv`, configure the Python virtual environment, install the Google ADK, and verify CLI/SDK availability.

1. **Install uv Package Manager**:
   ```bash
   # For macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Initialize Python Environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```
3. **Install Dependencies**:
   Install core packages specified in `requirements.txt`:
   ```bash
   uv pip install -r requirements.txt
   ```
4. **Verify Installations**:
   ```bash
   uv --version
   python3 -c "import google.adk; print(google.adk.__version__)"
   ```

---

## Phase 2: Create Development Agents & Shared Project Memory

Goal: Initialize and configure the specialized **Development Agents** that will autonomously coordinate, design, and write the project's source code, using a structured **Shared Project Memory** to maintain alignment. Make use of the google agents skills found here: https://github.com/addyosmani/agent-skills

*Note: These development agents are used to construct the project. The key runtime project agents and features (e.g., Investment Committee, Portfolio Analyzer) are separate from these development agents.*

### 1. Development Agents

#### A. Product Strategist
*   **Responsibilities**: Owns product direction; converts vague user requests into structured objectives.
*   **Tasks**: Clarify user goals, create MVP scope, generate user stories, prevent scope creep, prioritize features, and define acceptance criteria.
*   **Deliverables**: `requirements.md`, user stories, feature backlog.

#### B. System Architect
*   **Responsibilities**: Designs the technical solution.
*   **Tasks**: Define the tech stack, folder structure, API design, database schema, agent architecture, and MCP integration strategy.
*   **Deliverables**: `architecture.md`, system diagrams, implementation plan.

#### C. Builder Agent
*   **Responsibilities**: Writes production-ready code.
*   **Tasks**: Implement features, build React components, integrate MCP, implement APIs, refactor, and keep commits modular.
*   **Deliverables**: Working code, clean architecture.

#### D. QA & Debug Agent
*   **Responsibilities**: Maintains software quality.
*   **Tasks**: Review code, identify bugs, write tests, check edge cases, verify acceptance criteria, and suggest improvements.
*   **Deliverables**: Bug reports, test suite, validation results.

#### E. DevOps & Demo Agent
*   **Responsibilities**: Prepares the project for judging.
*   **Tasks**: Setup Docker, configure local setup, deploy, write README, draft demo scripts, document architecture, and troubleshoot setup.
*   **Deliverables**: `README.md`, demo guide, deployment instructions.

### 2. Shared Project Memory
All development agents reference and update these files in the workspace root to stay aligned and prevent drift:
*   `project.md` - Overall project context and current state.
*   `requirements.md` - Product requirements and features backlog.
*   `architecture.md` - Folder structures, system diagrams, and schemas.
*   `tasks.md` - Detailed TODO lists and assignments.
*   `progress.md` - Status of completed and pending deliverables.
*   `decisions.md` - Log of architectural and design decisions.
*   `known_issues.md` - Outstanding bugs, limitations, and workarounds.

---

## Phase 3: Core Project Features (Separate Runtime Agents)

Goal: Implement the backend agent logic and tool integrations for the application's runtime features.

### Feature 1 — Goal Planner
*   Infers risk tolerance from user inputs and generates investment objectives.

### Feature 2 — Portfolio Health Analyzer (Moomoo MCP)
*   Computes diversification score, sector allocation, and concentration risk using Moomoo MCP.

### Feature 3 — Market Research Agent
*   Compares candidate securities, pulls metrics (valuation, momentum, earnings), and ranks recommendations.

### Feature 4 — Portfolio Rebalancer
*   Generates buy/sell allocations and rebalancing rationale based on targets.

### Feature 5 — Trade Execution Agent (Moomoo MCP)
*   **CRITICAL SAFETY**: Checks buying power and builds orders, but halts for explicit user approval before execution.

### Feature 6 — Market Monitoring
*   Performs autonomous background monitoring for price and portfolio triggers.

### Feature 7 — Investment Committee (Collaborative Multi-Agent)
*   **Bull Analyst**: Arguments supporting candidate investments.
*   **Bear Analyst**: Arguments against candidate investments.
*   **Risk Manager**: Evaluates downside risk and portfolio impact.
*   **Decision Agent**: Collates arguments, computes confidence, and produces final recommendation.

---

## Phase 4: Frontend Development (Next.js)

Goal: Build a polished web application layout.

*   **Stack**: Next.js, React, Tailwind CSS, shadcn/ui, Framer Motion, Recharts.
*   **UI Screens**:
    *   **Chat Workspace**: Fluid interface for communicating with the Planner.
    *   **Agent Activity Feed**: Dynamic visual log showing development and runtime agent progress.
    *   **Portfolio Dashboard**: Value tracker, holdings, and sector allocation charts.
    *   **Research Workspace**: Analysis views containing bull/bear cases and confidence metrics.
    *   **Trade Approval Panel**: Prominent safety prompt for manual execution.
    *   **Explainability Panel**: Breakdown of the "why" behind each recommendation.

---

## Phase 5: Verification & Safety Compliance

*   Verify all order execution pathways prompt for explicit human confirmation.
*   Verify development agents successfully update Shared Project Memory files.
