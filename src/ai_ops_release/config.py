import os
import yaml
from pydantic import BaseModel, Field
from typing import List, Optional

class BumpConfig(BaseModel):
    files: List[str] = Field(default_factory=lambda: ["pyproject.toml", "package.json", "src/version.py"])

class GateConfig(BaseModel):
    lint_command: Optional[str] = "uv run ruff check ."
    test_command: Optional[str] = "uv run pytest"
    drift_evalset: Optional[str] = "tests/eval/evalsets/drift.json"
    target_agent_path: Optional[str] = "my_super_agent/agent.py"
    target_agent_object: Optional[str] = "root_agent"
    target_agent_app_name: Optional[str] = "app"

class DeploymentConfig(BaseModel):
    frontend_build_command: Optional[str] = "npm run build"
    frontend_deploy_command: Optional[str] = "firebase deploy --only hosting"
    package_build_command: Optional[str] = "uv build"
    package_publish_command: Optional[str] = "uv publish"

class AIOpsReleaseConfig(BaseModel):
    version: str = "1.0.0"
    app_name: str = "agent-ops-release"
    bump: BumpConfig = Field(default_factory=BumpConfig)
    gates: GateConfig = Field(default_factory=GateConfig)
    deployment: DeploymentConfig = Field(default_factory=DeploymentConfig)
    doc_sync_script: Optional[str] = "scripts/sync_docs.py"

    @classmethod
    def load(cls, workspace_path: str = ".") -> 'AIOpsReleaseConfig':
        config_path = os.path.join(workspace_path, "ai-ops.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
                return cls.model_validate(data)
        return cls()

config = AIOpsReleaseConfig.load()
