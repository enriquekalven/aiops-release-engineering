"""Tests for the evaluator."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import pytest

from evaluator import evaluate_program

INITIAL_CODE = open("initial_program.py").read()


def test_evaluate_program_returns_score_and_insights():
    """evaluate_program() returns a dict with score and insights."""
    result = evaluate_program(INITIAL_CODE)
    assert isinstance(result["score"], float)
    assert result["score"] >= 0.0
    assert isinstance(result["insights"], list)


def test_evaluate_program_returns_error_insights_on_failure():
    """evaluate_program() returns error insights for bad code."""
    result = evaluate_program("def !!! invalid python code")
    assert result["score"] is None
    labels = {i["label"] for i in result["insights"]}
    assert "error" in labels or "traceback" in labels


def test_evaluate_program_captures_stdout():
    """stdout from the program is captured as an insight."""
    code = 'print("hello stdout test")\ndef evaluate(ei=None):\n    return {"accuracy_score": 1.0}'
    result = evaluate_program(code)
    stdout_insights = [i for i in result["insights"] if i["label"] == "stdout"]
    assert len(stdout_insights) >= 1
    assert "hello stdout test" in stdout_insights[0]["text"]


def test_cli_main_writes_output_file():
    """main() writes a valid JSON output file when run via CLI."""
    tmpdir = tempfile.mkdtemp()
    try:
        shutil.copy("initial_program.py", os.path.join(tmpdir, "initial_program.py"))
        shutil.copy("evaluator.py", os.path.join(tmpdir, "evaluator.py"))
        output_file = os.path.join(tmpdir, "scores.json")

        cmd = [
            sys.executable,
            "evaluator.py",
            "--output-file",
            output_file,
            "--program-dir",
            tmpdir,
        ]

        result = subprocess.run(
            cmd,
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

        with open(output_file, "r") as f:
            data = json.load(f)

        assert isinstance(data["score"], (int, float))
        assert "insights" in data
    finally:
        shutil.rmtree(tmpdir)
