import os
import json
import pytest
from ai_ops_release.evaluators.drift import DriftEvaluator, DEFAULT_DRIFT_PROMPTS

def test_drift_load_prompts_file_not_found(tmp_path):
    prompts = DriftEvaluator.load_prompts(str(tmp_path / "missing.json"))
    assert prompts == DEFAULT_DRIFT_PROMPTS

def test_drift_load_prompts_list_of_strings(tmp_path):
    json_path = tmp_path / "prompts.json"
    data = ["Hello", "World"]
    json_path.write_text(json.dumps(data))
    
    prompts = DriftEvaluator.load_prompts(str(json_path))
    assert prompts == data

def test_drift_load_prompts_list_of_objects_with_prompt_key(tmp_path):
    json_path = tmp_path / "prompts.json"
    data = [{"prompt": "Hello"}, {"prompt": "World"}]
    json_path.write_text(json.dumps(data))
    
    prompts = DriftEvaluator.load_prompts(str(json_path))
    assert prompts == ["Hello", "World"]

def test_drift_load_prompts_full_evalset_schema(tmp_path):
    json_path = tmp_path / "evalset.json"
    data = [
        {
            "eval_id": "test_1",
            "conversation": [
                {
                    "user_content": {
                        "parts": [{"text": "Hello Evalset"}]
                    }
                }
            ]
        }
    ]
    json_path.write_text(json.dumps(data))
    
    prompts = DriftEvaluator.load_prompts(str(json_path))
    assert prompts == ["Hello Evalset"]

def test_drift_load_prompts_invalid_json(tmp_path):
    json_path = tmp_path / "invalid.json"
    json_path.write_text("not json")
    
    prompts = DriftEvaluator.load_prompts(str(json_path))
    assert prompts == DEFAULT_DRIFT_PROMPTS
