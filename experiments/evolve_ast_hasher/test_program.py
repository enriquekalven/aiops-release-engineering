"""Tests for initial_program.py."""
import pytest
from initial_program import compute_hash, evaluate, ASTStructuralHasher

def test_compute_hash_valid():
    code = "def foo(): pass"
    h = compute_hash(code)
    assert h is not None
    assert isinstance(h, str)
    assert len(h) == 64

def test_compute_hash_ignores_comments_and_docstrings():
    code1 = 'def foo():\n    """Docstring 1."""\n    # comment 1\n    return 42\n'
    code2 = 'def foo():\n    """Docstring 2."""\n    # comment 2\n    return 42\n'
    assert compute_hash(code1) == compute_hash(code2)

def test_evaluate_returns_accuracy():
    result = evaluate({})
    assert "accuracy_score" in result
    score = result["accuracy_score"]
    assert isinstance(score, (int, float))
    assert 0.0 <= score <= 1.0
