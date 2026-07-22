"""Initial program for Layout-Agnostic AST Structural Hasher Optimization.

Optimize a layout-agnostic Abstract Syntax Tree (AST) Structural Hasher for Python code.
"""
import ast
import hashlib
from typing import Any, Mapping

# ORIGIN: src/ai_ops_release/evaluators/code_drift.py::ASTStructuralHasher (lines 15-55)
class ASTStructuralHasher(ast.NodeVisitor):
    def __init__(self):
        self.structural_tokens = []

# EVOLVE-BLOCK-START
    def visit(self, node: ast.AST):
        # Skip docstring expressions entirely
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Skip the literal string inside docstrings or inline strings
            return

        # Record the type of the node
        self.structural_tokens.append(type(node).__name__)

        # Extract specific structural properties for critical nodes
        if isinstance(node, ast.Name):
            self.structural_tokens.append(f"Name:{node.id}")
        elif isinstance(node, ast.Constant):
            self.structural_tokens.append(f"Const:{repr(node.value)}")
        elif isinstance(node, ast.arg):
            self.structural_tokens.append(f"Arg:{node.arg}")
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            self.structural_tokens.append(f"Func:{node.name}")
            for dec in node.decorator_list:
                self.visit(dec)
        elif isinstance(node, ast.ClassDef):
            self.structural_tokens.append(f"Class:{node.name}")

        # Recursively visit children
        super().generic_visit(node)
# EVOLVE-BLOCK-END


def compute_hash(code_str: str) -> str | None:
    try:
        tree = ast.parse(code_str)
        hasher = ASTStructuralHasher()
        hasher.visit(tree)
        structural_string = "".join(hasher.structural_tokens)
        return hashlib.sha256(structural_string.encode("utf-8")).hexdigest()
    except Exception:
        return None


# Standard Benchmark pairs for testing/evaluating
BENCHMARK_PAIRS = [
    # (code1, code2, should_be_same)
    # 1. Whitespace & Comment differences (should be SAME)
    (
        "def add(a, b):\n    # add two numbers\n    return a + b\n",
        "def add(a, b):\n\n    # different comment\n    return a + b\n",
        True,
    ),
    # 2. Docstring differences (should be SAME)
    (
        'def greet(name):\n    """Greet user."""\n    return f"Hello {name}"\n',
        'def greet(name):\n    """A completely different docstring."""\n    return f"Hello {name}"\n',
        True,
    ),
    # 3. Logic change (should be DIFFERENT)
    (
        "def add(a, b):\n    return a + b\n",
        "def add(a, b):\n    return a - b\n",
        False,
    ),
    # 4. Critical URL string change (should be DIFFERENT)
    (
        'URL = "https://api.v1.example.com"\ndef fetch(): pass\n',
        'URL = "https://api.v2.example.com"\ndef fetch(): pass\n',
        False,
    ),
    # 5. Config key change (should be DIFFERENT)
    (
        'CFG = {"timeout": 30}\n',
        'CFG = {"timeout": 60}\n',
        False,
    ),
    # 6. Variable rename in body (should be DIFFERENT)
    (
        "def calc(x):\n    y = x * 2\n    return y\n",
        "def calc(x):\n    z = x * 2\n    return z\n",
        False,
    ),
    # 7. Function signature change (should be DIFFERENT)
    (
        "def process(data):\n    pass\n",
        "def process(data, options=None):\n    pass\n",
        False,
    ),
    # 8. Identical code (should be SAME)
    (
        "x = [1, 2, 3]\nfor i in x:\n    print(i)\n",
        "x = [1, 2, 3]\nfor i in x:\n    print(i)\n",
        True,
    ),
]


def evaluate(eval_inputs: Mapping[str, Any] = None) -> dict[str, float]:
    """Score the solution against the benchmark dataset."""
    correct = 0
    total = len(BENCHMARK_PAIRS)
    
    for code1, code2, should_same in BENCHMARK_PAIRS:
        h1 = compute_hash(code1)
        h2 = compute_hash(code2)
        
        if h1 is None or h2 is None:
            continue
            
        is_same = (h1 == h2)
        if is_same == should_same:
            correct += 1
            
    score = correct / total if total > 0 else 0.0
    return {"accuracy_score": score}
