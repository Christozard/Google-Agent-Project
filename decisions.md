# Architectural & Design Decisions

## Phase 3 Decisions

### Decision 1: Centralized InvestmentOrchestrator
- **Status**: Implemented
- **Context**: All 7 features need to work together in a coordinated workflow.
- **Decision**: Created a single `InvestmentOrchestrator` class that wires all 16 agent instances together and exposes a unified API. This avoids circular dependencies between agents and provides a single entry point.
- **Alternative Considered**: Decentralized agent communication via message bus. Rejected due to added complexity for the current scope.

### Decision 2: SharedMemory with Disk Persistence
- **Status**: Implemented
- **Context**: Agents need to share state across invocations and persist decisions.
- **Decision**: `SharedMemory` class with in-memory cache + JSON file fallback using dot-separated keys mapped to directory structures (e.g., `portfolio.health.score` → `shared_memory/portfolio/health/score.json`).
- **Alternative Considered**: SQLite database. Rejected for simplicity of JSON-based debugging.

### Decision 3: User Approval Gate for Trades
- **Status**: Implemented
- **Context**: CRITICAL SAFETY - no real trades should execute without explicit human approval.
- **Decision**: `execute_trade_with_approval()` requires `user_approved=True` parameter. The orchestrator reinforces this with validation and correction loops before execution. Default is `False`.
- **Safety**: Even with `user_approved=True`, the system still validates orders against qty/price/buying power limits.

### Decision 4: Sells-Before-Buys Execution Order
- **Status**: Implemented
- **Context**: Rebalancing plans may contain both buy and sell actions.
- **Decision**: `ExecutorAgent` executes all SELL actions first to free up capital, then executes BUY actions. This prevents insufficient buying power during rebalancing.

### Decision 5: Simulated Moomoo MCP Data
- **Status**: Planned for upgrade
- **Context**: The Moomoo MCP server is not running, so real API calls fail.
- **Decision**: All MCP client methods return realistic simulated data (prices, positions, P/E ratios). The architecture is designed so switching to real data requires only replacing the simulated return values in `MoomooMCPClient` methods.
- **Future**: Connect to real Moomoo MCP server at `127.0.0.1:11111` when available.

### Decision 6: Validation-Correction-Execution Pipeline
- **Status**: Implemented
- **Context**: Orders may fail validation (wrong qty, insufficient funds, etc.).
- **Decision**: Three-step pipeline: (1) Validator checks rules, (2) CorrectionLoop tries to fix issues automatically (split, reduce, adjust), (3) Executor runs the approved plan. All steps are audited.

### Decision 7: Audit Logger with Daily Rotation
- **Status**: Implemented
- **Context**: Need compliance-grade logging for all agent activities.
- **Decision**: JSONL format with daily file rotation (`audit_YYYY-MM-DD.jsonl`). In-memory buffer of 1000 entries for quick queries. Supports filtering by agent, action, and severity level.
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity
## Decision: Test architecture decision
- Rationale: Technical necessity