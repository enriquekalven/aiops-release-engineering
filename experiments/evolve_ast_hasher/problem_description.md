# Layout-Agnostic AST Structural Hasher Optimization

## Problem Statement

The goal of this experiment is to optimize a layout-agnostic Abstract Syntax Tree (AST) Structural Hasher for Python source code. In AIOps release engineering, drift detection must distinguish between benign formatting changes (whitespace, docstring edits, comments) and semantic/functional code changes (logic alterations, config updates, string constant changes).

The `ASTStructuralHasher` class visits AST nodes and accumulates structural tokens. Currently, the seed implementation skips ALL string constants, which makes it immune to docstring changes, but also blind to critical configuration updates (such as API URLs, timeout values, or config dictionary keys).

## Formal Specification

Given two Python code snippets $C_1$ and $C_2$:
- Compute structural hashes $H(C_1) = \text{SHA256}(\text{tokens}(C_1))$ and $H(C_2) = \text{SHA256}(\text{tokens}(C_2))$.
- If $C_1$ and $C_2$ differ ONLY in comments, whitespace, indentation, or docstrings, $H(C_1)$ MUST equal $H(C_2)$.
- If $C_1$ and $C_2$ differ in control flow, binary operators, variable names, function signatures, or critical string constants (URLs, paths, keys), $H(C_1)$ MUST NOT equal $H(C_2)$.

## Evaluation

- **Metric:** `accuracy_score` (maximize)
- **Strategy:** `PARTIAL_CREDIT`
- **Inputs:** `BENCHMARK_PAIRS` set of paired Python code snippets with ground-truth equivalence labels.

## Solution Guidance

1. Differentiate docstring string constants (e.g. `ast.Expr` containing an `ast.Constant` string, or `ast.get_docstring`) from critical value string constants (e.g. dictionary keys, function call arguments, variable assignments).
2. Ensure variable names (`ast.Name`), function names (`ast.FunctionDef`), and argument names (`ast.arg`) are included in structural tokens.
3. Keep the hasher deterministic and fast. Do not import external non-stdlib packages.
