---
description: Fully automate the entire release cycle from code validation to global deployment with AI-augmented quality gates.
---

# 🚀 zero2hero: The Autonomous Release Engine (Generic Framework Edition)

This workflow automates the end-to-end productionization of your AI Agent. It ensures structural integrity, executes multi-turn evaluation drift testing, and orchestrates global deployments.

## Phase 1: Preparation & Intelligence Sync
1. **Semantic Version Sync**: 
   - Extract and increment the patch version (e.g. `1.0.0` -> `1.0.1`).
   - Synchronize across `pyproject.toml`, `package.json`, and source code.
2. **Upgrade Dependencies & Preflight**: 
   - Execute preflight checks for tooling, registries, and API keys.
3. **AI-Driven Changelog Generation**:
   - Leverage Gemini to read `git log` and append a high-fidelity Markdown delta to `CHANGELOG.md`.

## Phase 2: Structural Verification & AIOps Drift Gates
4. **Linting & Formatting**:
   - Run configured linters (e.g., Ruff).
5. **Code Drift Gate**:
   - Compare workspace AST hashes with the Attestation Snapshot to catch unintended logic changes.
6. **The AIOps Multi-Turn Drift Gate**:
   - Battle-test multi-turn persona stability and instruction retention with simulated user dialogue.
7. **Full Regression Suite**: 
   - Run `pytest` to ensure all unit tests pass.
8. **Release Certification**:
   - Generate a cryptographically signed Release Certificate upon passing all gates.

## Phase 3: Deployment & Publishing
9. **Frontend Build** (Optional): 
   - Execute configured frontend build scripts.
10. **Distribution Build**:
    - Build the Python distribution wheel (`uv build`).
11. **Git Release Management**:
    - Checkout a release branch, commit changes, and create a git tag (`v[VERSION]`).
12. **Publishing** (Optional):
    - Publish the package to PyPI and/or deploy the frontend.

## Usage
Run the pipeline using the `ai-ops` CLI:
```bash
ai-ops release
```
Or view individual gates:
```bash
ai-ops preflight
ai-ops code-drift
ai-ops drift --agent examples/sample_agent.py --object agent
```
