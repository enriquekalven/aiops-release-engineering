# Layout-Agnostic AST Structural Hasher Optimization

An AlphaEvolve experiment to optimize a layout-agnostic Abstract Syntax Tree (AST) Structural Hasher for Python source code.

## Files

| File | Purpose |
|---|---|
| `initial_program.py` | Seed program with EVOLVE-BLOCK markers |
| `evaluator.py` | CLI-compatible evaluator for the `ae` CLI |
| `problem_description.md` | Detailed problem specification (used in LLM prompts) |
| `test_program.py` | Tests for the initial program |
| `test_evaluator.py` | Tests for the evaluator |
| `example_evaluation.json` | Sample evaluator output |
| `pyproject.toml` | Project configuration |

## Running Tests

```bash
uv sync
uv run pytest -v
```

## Metric

- **Name:** `accuracy_score`
- **Direction:** maximize
- **Evaluation strategy:** PARTIAL_CREDIT

## Launching

Use the `alpha-evolve-runner` skill or the `ae` CLI to launch this experiment.
```bash
ae experiment create --config .evolve/experiment_description.json
```
