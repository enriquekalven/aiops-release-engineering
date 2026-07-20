# 🚀 AIOps Release Engineering Engine

Autonomous Release Engineering, Evaluation Gating, and Certification for production-grade AI Agents.

## Overview
The `ai-ops-release` framework (colloquially known as the **Zero2Hero Engine**) provides an automated, phase-gated pipeline to transition AI Agents safely from development to production. Unlike traditional CI/CD, it embeds **AIOps-specific gates** such as Multi-Turn Instruction Drift tests, Persona Stability simulation, and layout-agnostic Code Drift detection using Abstract Syntax Trees (AST).

## Core Capabilities
- **🛡️ Preflight Consistency Gate**: Verifies environment debt, credential validity, and tooling parity.
- **🕵️ AIOps Multi-Turn Drift Gate**: Simulates multi-turn dialogue with your agent and judges persona erosion and instruction drift over time (using Vertex AI Eval or Gemini).
- **🚨 AST Code Drift Gate**: Compares codebase syntax trees against cryptographically signed attestation snapshots to catch unintended logic alterations while ignoring whitespace and formatting updates.
- **🧠 AI Changelog Synthesis**: Reads git logs and leverages Gemini to synthesize executive-grade Markdown release notes.
- **🏅 Production Release Certification**: Emits a signed Release Attestation Certificate upon successfully clearing all pipeline gates.

## Getting Started

### 1. Installation
Install the framework using `uv`:
```bash
make install
```

### 2. Configuration
Create an `ai-ops.yaml` configuration manifest in the root of your project:
```yaml
version: 1.0.0
app_name: "my-agent-app"

bump:
  files:
    - "pyproject.toml"
    - "src/my_agent/config.py"

gates:
  lint_command: "uv run ruff check ."
  test_command: "uv run pytest"
  drift_evalset: "tests/eval/drift.json"
  target_agent_path: "src/my_agent/agent.py"
  target_agent_object: "root_agent"

deployment:
  package_build_command: "uv build"
  package_publish_command: "uv publish"
```

### 3. Usage

**Run Preflight Checks:**
```bash
aops preflight
```

**Snapshot Code Baseline for Drift Detection:**
```bash
aops snapshot
```

**Check for Code Drift:**
```bash
aops code-drift
```

**Run Multi-Turn Persona Drift Simulation:**
```bash
aops drift
```

**Execute the Full End-to-End Release Pipeline:**
```bash
aops release
```

## Integrating as a Developer "Skill"
Incorporate the Zero2Hero methodology into agentic development environments (like Gemini Jetski) using the provided `examples/SKILL.md` template.

## License
MIT
