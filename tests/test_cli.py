import os
from typer.testing import CliRunner
import pytest
from ai_ops_release.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "🚀 AIOps Release Engineering Engine" in result.stdout

def test_cli_preflight():
    result = runner.invoke(app, ["preflight"])
    # May return exit code 0 or 1 depending on environment, but should execute
    assert "Running Preflight Checks" in result.stdout

def test_cli_snapshot_and_code_drift(tmp_path):
    workspace = tmp_path
    attestation = ".ai-ops/attestation.json"
    
    code_path = workspace / "agent.py"
    code_path.write_text("a = 1")
    
    # Run snapshot
    result_snap = runner.invoke(app, ["snapshot", "--path", str(workspace), "--attestation", attestation, "agent.py"])
    assert result_snap.exit_code == 0
    assert "Audit Attestation Saved" in result_snap.stdout
    assert os.path.exists(workspace / attestation)
    
    # Run check
    result_check = runner.invoke(app, ["code-drift", "--path", str(workspace), "--attestation", attestation])
    assert result_check.exit_code == 0
    assert "No code drift detected" in result_check.stdout
    
    # Modify and check
    code_path.write_text("a = 2")
    result_check_fail = runner.invoke(app, ["code-drift", "--path", str(workspace), "--attestation", attestation])
    assert result_check_fail.exit_code == 1
    assert "Code Drift Detected" in result_check_fail.stdout

def test_cli_bump_dry_run(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.0"')
    (tmp_path / "ai-ops.yaml").write_text("version: 1.0.0\nbump:\n  files:\n    - pyproject.toml")
    
    result = runner.invoke(app, ["bump", "1.0.1", "--path", str(workspace := tmp_path)])
    assert result.exit_code == 0
    assert "Bumping semantic version" in result.stdout
    
    updated_toml = (tmp_path / "pyproject.toml").read_text()
    assert 'version = "1.0.1"' in updated_toml
