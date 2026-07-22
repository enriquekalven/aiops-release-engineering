"""CLI-compatible evaluator script for AlphaEvolve.

Usage:
    python evaluator.py --output-file /path/to/scores.json --program-dir /path/to/program
"""
import argparse
import contextlib
import io
import json
import math
import os
import signal
import sys
import traceback
from typing import Any, Dict, List


def _failure(msg: str, insights: List[Dict[str, str]] = None) -> Dict[str, Any]:
    if insights is None:
        insights = []
    insights.append({"label": "error", "text": msg})
    return {"score": None, "insights": insights}


def evaluate_program(
    code: str, timeout_seconds: int = 30
) -> Dict[str, Any]:
    """Execute candidate code and return evaluation results.

    Args:
        code: Python source code of candidate initial_program.py.
        timeout_seconds: Max execution time before signal alarm.

    Returns:
        Dict with "score" (float or None) and "insights" list.
    """
    insights: List[Dict[str, str]] = []
    stdout_io = io.StringIO()
    stderr_io = io.StringIO()

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Evaluation timed out after {timeout_seconds} seconds")

    has_alarm = hasattr(signal, "SIGALRM") and hasattr(signal, "alarm")
    if has_alarm:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

    raw_score = None
    try:
        namespace: Dict[str, Any] = {}
        with contextlib.redirect_stdout(stdout_io), contextlib.redirect_stderr(stderr_io):
            exec(code, namespace)

            if "evaluate" in namespace:
                eval_func = namespace["evaluate"]
                eval_result = eval_func()
            elif "solve" in namespace:
                solve_func = namespace["solve"]
                solve_result = solve_func()
                eval_result = {"accuracy_score": float(solve_result)}
            else:
                return _failure("Candidate code defines neither 'evaluate' nor 'solve' function", insights)

            if isinstance(eval_result, dict):
                raw_score = eval_result.get("accuracy_score")
            elif isinstance(eval_result, (int, float)):
                raw_score = eval_result
            else:
                return _failure(f"Invalid evaluation return type: {type(eval_result)}", insights)

    except TimeoutError as te:
        return _failure(str(te), insights)
    except Exception as e:
        insights.append({"label": "traceback", "text": traceback.format_exc()})
        return _failure(f"Evaluation exception: {e}", insights)
    finally:
        if has_alarm:
            signal.alarm(0)

        stdout_val = stdout_io.getvalue()
        if stdout_val:
            insights.append({"label": "stdout", "text": stdout_val})
        stderr_val = stderr_io.getvalue()
        if stderr_val:
            insights.append({"label": "stderr", "text": stderr_val})

    if raw_score is None:
        return _failure("Evaluation function returned None for accuracy_score", insights)

    try:
        score_val = float(raw_score)
    except (ValueError, TypeError):
        return _failure(f"Score cannot be converted to float: {raw_score}", insights)

    if math.isnan(score_val) or math.isinf(score_val):
        return _failure(f"Non-finite score encountered: {score_val}", insights)

    return {"score": score_val, "insights": insights}


def main():
    parser = argparse.ArgumentParser(description="AlphaEvolve Evaluator CLI")
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to write evaluation results JSON",
    )
    parser.add_argument(
        "--program-dir",
        required=True,
        help="Directory containing initial_program.py and context files",
    )

    args = parser.parse_args()

    program_dir = os.path.abspath(args.program_dir)
    if program_dir not in sys.path:
        sys.path.insert(0, program_dir)

    program_file = os.path.join(program_dir, "initial_program.py")
    if not os.path.exists(program_file):
        result = _failure(f"Program file not found: {program_file}")
    else:
        try:
            with open(program_file, "r", encoding="utf-8") as f:
                code = f.read()
            result = evaluate_program(code)
        except Exception as e:
            result = _failure(f"Failed to read or evaluate initial_program.py: {e}")

    output_dir = os.path.dirname(args.output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
