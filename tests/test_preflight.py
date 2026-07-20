from unittest.mock import patch, MagicMock
import os
import pytest
from ai_ops_release.evaluators.preflight import PreflightEngine, run_preflight

def test_preflight_registry_check():
    engine = PreflightEngine()
    success, detail = engine.check_registry_access("https://pypi.org/simple")
    assert success is True
    assert "Reachable" in detail

def test_preflight_tooling_check():
    engine = PreflightEngine()
    success, detail = engine.check_tooling()
    assert success is True
    assert "All base tools detected" in detail

def test_preflight_env_check(tmp_path):
    # Test with no .env
    engine = PreflightEngine(target_path=str(tmp_path))
    success, detail = engine.check_environment_consistency()
    assert success is True
    assert "No .env detected" in detail
    
    # Test with .env
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=test")
    success, detail = engine.check_environment_consistency()
    assert success is True
    assert "Detected environment files" in detail

@patch('shutil.which', return_value='/usr/bin/git')
@patch('urllib.request.urlopen')
def test_preflight_run_all(mock_urlopen, mock_which):
    # Mock reachable pypi
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response
    
    # Run all checks
    assert run_preflight() is True
