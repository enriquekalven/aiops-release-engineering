import asyncio
import os
from typing import Annotated, Optional
import typer
from rich.console import Console

from ai_ops_release.config import config
from ai_ops_release.evaluators.preflight import run_preflight as preflight_func
from ai_ops_release.evaluators.drift import run_drift_test as drift_func
from ai_ops_release.evaluators.code_drift import run_code_drift_check as code_drift_func, CodeDriftDetector
from ai_ops_release.engine import run_release as release_func, Zero2HeroEngine

app = typer.Typer(
    help="🚀 AIOps Release Engineering Engine: Autonomous release, gating, and certification for AI Agents.",
    no_args_is_help=True,
)

console = Console()


@app.command(name="preflight")
def preflight_cmd(
    path: Annotated[str, typer.Option("--path", "-p", help="Path to workspace")] = ".",
    registry: Annotated[str, typer.Option("--registry", "-r", help="PyPI Registry URL")] = "https://pypi.org/simple",
):
    """🛡️ Run preflight environment, credential, and tooling checks."""
    success = preflight_func(target_path=path, registry_url=registry)
    if not success:
        raise typer.Exit(code=1)


@app.command(name="drift")
def drift_cmd(
    agent_path: Annotated[str, typer.Option("--agent", "-a", help="Path to the agent.py file")] = None,
    agent_object: Annotated[str, typer.Option("--object", "-o", help="Name of the agent object in module")] = None,
    evalset: Annotated[str, typer.Option("--evalset", "-e", help="Path to drift evalset JSON file")] = None,
    app_name: Annotated[str, typer.Option("--app", help="ADK App Name")] = "app",
):
    """🕵️ Run AIOps Multi-Turn Persona & Instruction Drift Simulation."""
    # Pull defaults from config if not provided
    tgt_agent = agent_path or config.gates.target_agent_path
    tgt_obj = agent_object or config.gates.target_agent_object
    tgt_evalset = evalset or config.gates.drift_evalset
    tgt_app = app_name or config.gates.target_agent_app_name or "app"

    console.print(f"Loading Agent from: [cyan]{tgt_agent}:{tgt_obj}[/cyan]")
    console.print(f"Using Evalset: [cyan]{tgt_evalset}[/cyan]")

    success, score = asyncio.run(run_drift_test(
        agent_path=tgt_agent,
        agent_object=tgt_obj,
        evalset_path=tgt_evalset,
        app_name=tgt_app
    ))
    
    if not success:
        console.print(f"❌ [red]Drift Gate Failed with score: {score:.1f}/5.0[/red]")
        raise typer.Exit(code=1)
    console.print(f"✅ [green]Drift Gate Passed with score: {score:.1f}/5.0[/green]")


@app.command(name="snapshot")
def snapshot_cmd(
    path: Annotated[str, typer.Option("--path", "-p", help="Path to workspace")] = ".",
    attestation: Annotated[str, typer.Option("--attestation", help="Path to save attestation JSON")] = ".ai-ops/audit_attestation.json",
    files: Annotated[Optional[list[str]], typer.Argument(help="List of Python files or directories to snapshot")] = None,
):
    """📸 Snapshot structural AST hashes for code drift detection."""
    detector = CodeDriftDetector(workspace_path=path, attestation_file=attestation)
    
    target_files = files
    if not target_files:
        # Default to all .py files in src/ and the agent path
        target_files = []
        src_dir = os.path.join(path, "src")
        if os.path.exists(src_dir):
            for root, _, fs in os.walk(src_dir):
                for f in fs:
                    if f.endswith(".py"):
                        target_files.append(os.path.relpath(os.path.join(root, f), path))
        
        agent_path = config.gates.target_agent_path
        if agent_path and os.path.exists(os.path.join(path, agent_path)):
             target_files.append(agent_path)
             
    if not target_files:
        console.print("⚠️ [yellow]No Python files found to snapshot.[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"Snapshotted [cyan]{len(target_files)}[/cyan] files.")
    detector.save_attestation(target_files)


@app.command(name="code-drift")
def code_drift_cmd(
    path: Annotated[str, typer.Option("--path", "-p", help="Path to workspace")] = ".",
    attestation: Annotated[str, typer.Option("--attestation", help="Path to attestation JSON")] = ".ai-ops/audit_attestation.json",
):
    """🚨 Check for layout-agnostic structural code drift."""
    success = code_drift_func(workspace_path=path, attestation_file=attestation)
    if not success:
        raise typer.Exit(code=1)


@app.command(name="bump")
def bump_cmd(
    version: Annotated[str, typer.Argument(help="Target version to bump to (e.g. 1.0.1)")] = None,
    path: Annotated[str, typer.Option("--path", "-p", help="Path to workspace")] = ".",
):
    """🔄 Bump semantic version across pyproject.toml, package.json, and code."""
    engine = Zero2HeroEngine(workspace_path=path, target_version=version)
    success = engine.bump_version_strings(engine.target_version)
    if not success:
        raise typer.Exit(code=1)


@app.command(name="release")
def release_cmd(
    version: Annotated[Optional[str], typer.Option("--target-version", "-v", help="Force a specific version")] = None,
    path: Annotated[str, typer.Option("--path", "-p", help="Path to workspace")] = ".",
):
    """🚀 Run the Full Autonomous Release Pipeline (Prep, Gate, Certify, Deploy, Tag)."""
    success = asyncio.run(release_func(workspace_path=path, new_version=version))
    if not success:
        console.print("❌ [bold red]Release Pipeline Failed.[/bold red]")
        raise typer.Exit(code=1)
    console.print("✅ [bold green]Release Pipeline Completed Successfully.[/bold green]")


def main():
    app()


if __name__ == "__main__":
    main()
