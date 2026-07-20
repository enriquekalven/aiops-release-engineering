import os
import pytest
from ai_ops_release.config import AIOpsReleaseConfig, config
from ai_ops_release.evaluators.preflight import PreflightEngine
from ai_ops_release.evaluators.code_drift import ASTStructuralHasher, CodeDriftDetector
from ai_ops_release.engine import Zero2HeroEngine

def test_config_defaults():
    assert config.version == "1.0.0"
    assert config.app_name == "ai-ops-agent"
    assert config.gates.lint_command == "uv run ruff check ."
    assert config.gates.test_command == "uv run pytest"

def test_ast_hasher_basic(tmp_path):
    py_code = """
def hello(name: str):
    # This is a comment
    print(f"Hello {name}")
"""
    py_file = tmp_path / "hello.py"
    py_file.write_text(py_code)
    
    detector = CodeDriftDetector(workspace_path=str(tmp_path), attestation_file=str(tmp_path / "attestation.json"))
    h1 = detector.compute_file_hash(str(py_file))
    
    # Change comment and whitespace
    py_code_updated = """
def hello(name: str):


    # A DIFFERENT COMMENT
    print(f"Hello {name}")

"""
    py_file.write_text(py_code_updated)
    h2 = detector.compute_file_hash(str(py_file))
    
    # AST hash should be identical!
    assert h1 == h2
    assert h1 is not None

def test_engine_init(tmp_path):
    # Write a dummy pyproject.toml for the engine to find
    toml_content = """
[project]
name = "demo"
version = "0.1.0"
"""
    (tmp_path / "pyproject.toml").write_text(toml_content)
    (tmp_path / "ai-ops.yaml").write_text("version: 0.1.0\napp_name: demo")
    
    engine = Zero2HeroEngine(workspace_path=str(tmp_path), target_version="0.1.1")
    assert engine.current_version == "0.1.0"
    assert engine.target_version == "0.1.1"
    
    # Verify version bumping regex
    engine.bump_version_strings("0.1.1")
    updated_toml = (tmp_path / "pyproject.toml").read_text()
    assert 'version = "0.1.1"' in updated_toml
