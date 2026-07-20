import os
import yaml
import tomllib
from ai_ops_release.config import config, AIOpsReleaseConfig
from ai_ops_release.engine import Zero2HeroEngine

def test_versions_are_in_sync():
    """Ensure version strings in python config, pyproject.toml, and ai-ops.yaml match."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # 1. Get Python Config Version
    py_version = config.version
    
    # 2. Get pyproject.toml version
    pyproject_path = os.path.join(root, "pyproject.toml")
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    pyproject_version = pyproject_data["project"]["version"]
    
    # 3. Get ai-ops.yaml version
    ai_ops_path = os.path.join(root, "ai-ops.yaml")
    with open(ai_ops_path, "r", encoding="utf-8") as f:
        ai_ops_data = yaml.safe_load(f)
    ai_ops_version = ai_ops_data["version"]
    
    print(f"\nVersions detected -> Config: {py_version}, pyproject: {pyproject_version}, ai-ops.yaml: {ai_ops_version}")
    
    assert py_version == pyproject_version
    assert py_version == ai_ops_version

def test_engine_bump_version_all_files(tmp_path):
    """Test that the engine bumps versions in all configured files correctly."""
    toml_content = '[project]\nversion = "1.0.0"'
    yaml_content = 'version: 1.0.0\napp_name: demo'
    py_content = 'version = "1.0.0"\nVERSION = "1.0.0"'
    
    (tmp_path / "pyproject.toml").write_text(toml_content)
    (tmp_path / "ai-ops.yaml").write_text(yaml_content)
    (tmp_path / "version.py").write_text(py_content)
    
    # Create engine pointing to tmp_path
    engine = Zero2HeroEngine(workspace_path=str(tmp_path), target_version="1.0.1")
    
    # Configure the files to bump
    engine.config.bump.files = ["pyproject.toml", "ai-ops.yaml", "version.py"]
    
    success = engine.bump_version_strings("1.0.1")
    assert success is True
    
    # Verify updates
    updated_toml = (tmp_path / "pyproject.toml").read_text()
    updated_yaml = (tmp_path / "ai-ops.yaml").read_text()
    updated_py = (tmp_path / "version.py").read_text()
    
    assert 'version = "1.0.1"' in updated_toml
    assert 'version: 1.0.1' in updated_yaml
    assert 'version = "1.0.1"' in updated_py
    assert 'VERSION = "1.0.1"' in updated_py
