import os
import json
import pytest
from ai_ops_release.evaluators.code_drift import CodeDriftDetector, run_code_drift_check

def test_code_drift_detection_flow(tmp_path):
    workspace = tmp_path
    attestation_file = ".ai-ops/attestation.json"
    
    # 1. Create a sample code file
    code_path = workspace / "agent.py"
    initial_code = """
def process_data(data):
    # Initial implementation
    result = data * 2
    return result
"""
    code_path.write_text(initial_code)
    
    # 2. Snapshot
    detector = CodeDriftDetector(workspace_path=str(workspace), attestation_file=attestation_file)
    registry = detector.save_attestation(["agent.py"])
    
    assert "agent.py" in registry
    assert os.path.exists(workspace / attestation_file)
    
    # 3. Check drift (should be None)
    drifts = detector.detect_drift()
    assert len(drifts) == 0
    assert run_code_drift_check(str(workspace), attestation_file) is True
    
    # 4. Modify comment and formatting (should NOT drift)
    updated_code_formatting = """
def process_data(data):

    # NEW COMMENT
    
    result = data * 2

    return result

"""
    code_path.write_text(updated_code_formatting)
    drifts = detector.detect_drift()
    assert len(drifts) == 0
    assert run_code_drift_check(str(workspace), attestation_file) is True
    
    # 5. Modify LOGIC (SHOULD drift)
    updated_code_logic = """
def process_data(data):
    result = data * 3 # MODIFIED MULTIPLIER
    return result
"""
    code_path.write_text(updated_code_logic)
    drifts = detector.detect_drift()
    assert "agent.py" in drifts
    assert drifts["agent.py"] == "drifted"
    assert run_code_drift_check(str(workspace), attestation_file) is False
    
    # 6. Delete file (SHOULD drift as missing)
    os.remove(code_path)
    drifts = detector.detect_drift()
    assert "agent.py" in drifts
    assert drifts["agent.py"] == "missing"
    assert run_code_drift_check(str(workspace), attestation_file) is False
