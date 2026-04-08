# MatchLab Multi-Agent System

## Architecture

Two orchestrator agents coordinate four specialist subagents. Each specialist owns a coherent module of the codebase with scoped write permissions.

## Agent Map

| Agent | Type | Shortcut | Domain |
|-------|------|----------|--------|
| `testing` | Orchestrator | `Ctrl+Shift+T` | E2E test planning, execution, bug reporting |
| `development` | Orchestrator | `Ctrl+Shift+D` | Ticket implementation, CI, pull requests |
| `core-specialist` | Subagent | — | `apps/core/`, auth, registration, profiles |
| `matching-specialist` | Subagent | — | `apps/matching/`, solvers, scoring, export |
| `admin-ui-specialist` | Subagent | — | `apps/admin_views/`, templates, dashboards |
| `infra-specialist` | Subagent | — | `config/`, CI, Docker, scripts, fixtures |

## Workflows

### Testing Orchestrator

```mermaid
flowchart TD
    START_T([🧪 User describes feature to test]) --> A1[Phase 1: Analyze feature]
    A1 --> A2[Identify affected modules]
    A2 --> A3[Create test plan with milestones]
    A3 --> CP1{🛑 Checkpoint 1<br/>Human approves test plan}
    CP1 -->|Rejected| A1
    CP1 -->|Approved| B1

    B1[Phase 2: Prepare test data]
    B1 --> B2[/Delegate to infra-specialist<br/>Prepare fixtures & seed DB/]
    B2 --> B3[/Delegate to relevant specialists<br/>Verify model state/]
    B3 --> B4[Run loaddata & verify DB state]
    B4 --> CP2{🛑 Checkpoint 2<br/>Human confirms data ready}
    CP2 -->|Rejected| B1
    CP2 -->|Approved| C1

    C1[Phase 3: Execute tests]
    C1 --> C2[/Delegate to core-specialist<br/>Auth, profile, registration tests/]
    C1 --> C3[/Delegate to matching-specialist<br/>Solver, scoring, readiness tests/]
    C1 --> C4[/Delegate to admin-ui-specialist<br/>Dashboard, results, override tests/]
    C1 --> C5[/Delegate to infra-specialist<br/>CI, migration, fixture tests/]
    C2 & C3 & C4 & C5 --> C6[Collect all results & failures]

    C6 --> D1[Phase 4: Bug reporting]
    D1 --> D2[Create structured bug tickets]
    D2 --> D3[Generate summary report<br/>pass/fail counts by module]
    D3 --> CP3{🛑 Checkpoint 3<br/>Human reviews report<br/>& confirms filing issues}
    CP3 -->|Approved| END_T([✅ Testing complete])
    CP3 -->|Rejected| D1

    style CP1 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style CP2 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style CP3 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style B2 fill:#3498db,stroke:#2980b9,color:#fff
    style B3 fill:#3498db,stroke:#2980b9,color:#fff
    style C2 fill:#3498db,stroke:#2980b9,color:#fff
    style C3 fill:#3498db,stroke:#2980b9,color:#fff
    style C4 fill:#3498db,stroke:#2980b9,color:#fff
    style C5 fill:#3498db,stroke:#2980b9,color:#fff
```

### Development Orchestrator

```mermaid
flowchart TD
    START_D([🔧 User provides GitHub issue]) --> E1[Phase 1: Analyze ticket]
    E1 --> E2[Review 14-TECHNICAL-SPEC.md]
    E2 --> E3[Identify affected modules & specialists]
    E3 --> E4[Create implementation plan<br/>+ manual validation script]
    E4 --> CP4{🛑 Checkpoint 1<br/>Human reviews plan}
    CP4 -->|Rejected| E1
    CP4 -->|Approved| F1

    F1[Phase 2: Worktree setup]
    F1 --> F2[git worktree add -b feature-branch]
    F2 --> F3[/Delegate to specialists<br/>Implement changes in worktree/]
    F3 --> F4[Ensure migrations created]
    F4 --> F5[Present manual validation script]
    F5 --> CP5{🛑 Checkpoint 2<br/>Human runs manual validation}
    CP5 -->|Failed| F3
    CP5 -->|Passed| G1

    G1[Phase 3: CI green & PR]
    G1 --> G2[Run pytest apps/ locally]
    G2 --> G3{Tests pass?}
    G3 -->|No| G4[/Delegate fixes to<br/>responsible specialist/]
    G4 --> G2
    G3 -->|Yes| G5[Commit & push branch]
    G5 --> G6[gh pr create]
    G6 --> CP6{🛑 Checkpoint 3<br/>Human code review & merge}
    CP6 -->|Changes requested| F3
    CP6 -->|Merged| H1

    H1[Phase 4: Cleanup]
    H1 --> H2[git worktree remove]
    H2 --> H3[git pull origin main]
    H3 --> END_D([✅ Development complete])

    style CP4 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style CP5 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style CP6 fill:#ff6b6b,stroke:#c0392b,color:#fff
    style F3 fill:#3498db,stroke:#2980b9,color:#fff
    style G4 fill:#3498db,stroke:#2980b9,color:#fff
```

### System Overview

```mermaid
graph TB
    subgraph Orchestrators
        T[🧪 Testing Orchestrator<br/>Ctrl+Shift+T]
        D[🔧 Development Orchestrator<br/>Ctrl+Shift+D]
    end

    subgraph Specialists
        CS[Core Specialist<br/>apps/core/]
        MS[Matching Specialist<br/>apps/matching/]
        AS[Admin UI Specialist<br/>apps/admin_views/]
        IS[Infra Specialist<br/>config/, CI, Docker]
    end

    T -->|delegate| CS
    T -->|delegate| MS
    T -->|delegate| AS
    T -->|delegate| IS

    D -->|delegate| CS
    D -->|delegate| MS
    D -->|delegate| AS
    D -->|delegate| IS

    subgraph "Human Checkpoints 🛑"
        TC1[Test plan approval]
        TC2[Test data confirmation]
        TC3[Bug report review]
        DC1[Implementation plan review]
        DC2[Manual validation]
        DC3[PR code review & merge]
    end

    T -.->|requires| TC1
    T -.->|requires| TC2
    T -.->|requires| TC3
    D -.->|requires| DC1
    D -.->|requires| DC2
    D -.->|requires| DC3

    style T fill:#2ecc71,stroke:#27ae60,color:#fff
    style D fill:#e67e22,stroke:#d35400,color:#fff
    style CS fill:#9b59b6,stroke:#8e44ad,color:#fff
    style MS fill:#9b59b6,stroke:#8e44ad,color:#fff
    style AS fill:#9b59b6,stroke:#8e44ad,color:#fff
    style IS fill:#9b59b6,stroke:#8e44ad,color:#fff
```

## File Structure

```
.kiro/
├── agents/
│   ├── testing.json              # Testing orchestrator config
│   ├── development.json          # Development orchestrator config
│   ├── core-specialist.json      # Core & Auth subagent
│   ├── matching-specialist.json  # Matching Engine subagent
│   ├── admin-ui-specialist.json  # Admin UI subagent
│   └── infra-specialist.json     # Infrastructure subagent
├── prompts/
│   ├── testing-orchestrator.md   # Testing orchestrator system prompt
│   ├── development-orchestrator.md # Development orchestrator system prompt
│   ├── core-specialist.md        # Core specialist system prompt
│   ├── matching-specialist.md    # Matching specialist system prompt
│   ├── admin-ui-specialist.md    # Admin UI specialist system prompt
│   └── infra-specialist.md       # Infrastructure specialist system prompt
└── settings/
    └── cli.json                  # Workspace settings (delegate, thinking, todo, etc.)
```

## Usage

Switch to an orchestrator agent:
- `Ctrl+Shift+T` — Testing Orchestrator
- `Ctrl+Shift+D` — Development Orchestrator
- `/agent testing` — switch via command
- `/agent development` — switch via command

The orchestrators handle all delegation to specialists automatically. You only interact with the orchestrator.
