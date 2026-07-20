# Installation & Setup
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv is not installed. Installing uv..."; curl -LsSf https://astral.sh/uv/0.8.13/install.sh | sh; source $HOME/.local/bin/env; }
	uv sync

# Testing & Verification
test:
	uv sync
	uv run pytest

lint:
	uv sync
	uv run ruff check .

# Examples & Testing the Engine on the Sample Agent
preflight:
	uv run ai-ops preflight

drift:
	uv run ai-ops drift --agent examples/sample_agent.py --object agent --evalset examples/drift_evalset.json

snapshot:
	uv run ai-ops snapshot examples/sample_agent.py

code-drift:
	uv run ai-ops code-drift

release-demo:
	uv run ai-ops release --target-version 1.0.0-demo

# Build and Publish
build:
	rm -rf dist/ build/
	uv build

.PHONY: install test lint preflight drift snapshot code-drift release-demo build
