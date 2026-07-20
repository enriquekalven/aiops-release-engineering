import os
import shutil
import subprocess
import urllib.request
from rich.console import Console
from rich.table import Table

console = Console()


class PreflightEngine:
    """
    Ensures the environment and dependencies are consistent before running release gates.
    """

    def __init__(self, target_path: str = "."):
        self.target_path = os.path.abspath(target_path)
        self.results = {}

    def check_registry_access(self, registry_url: str = "https://pypi.org/simple") -> tuple[bool, str]:
        """Verify if the environment can reach the package registry."""
        try:
            req = urllib.request.Request(registry_url)
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status == 200:
                    return True, f"Reachable: {registry_url}"
        except Exception as e:
            console.print(
                f"⚠️  [yellow]Registry check failed for {registry_url}: {str(e)}.[/yellow]"
            )
            # Failover check
            if registry_url != "https://pypi.org/simple":
                try:
                    with urllib.request.urlopen("https://pypi.org/simple", timeout=3) as response:
                        if response.status == 200:
                            return True, "Resilient Failover: Public PyPI mirrors active."
                except Exception:
                    pass
            return False, f"Registry unreachable: {str(e)}"
        return False, "Unknown registry status"

    def check_tooling(self, required_tools: list[str] = None) -> tuple[bool, str]:
        """Check for mandatory CLI tools."""
        if not required_tools:
            required_tools = ["python3", "git", "uv"]
        
        missing = []
        for tool in required_tools:
            if not shutil.which(tool):
                # Special check for pip/uv
                if tool == "uv" and (shutil.which("pip") or shutil.which("pip3")):
                    continue
                missing.append(tool)

        if missing:
            return False, f"Missing tools: {', '.join(missing)}"
        return True, "All base tools detected."

    def check_environment_consistency(self) -> tuple[bool, str]:
        """Check for common environment debt (missing .env file)."""
        env_files = [f for f in os.listdir(self.target_path) if f.startswith(".env")]
        if not env_files:
            return True, "No .env detected. Ensure environment variables are loaded."
        return True, f"Detected environment files: {', '.join(env_files)}"

    def check_api_keys(self, required_keys: list[str] = None) -> tuple[bool, str]:
        """Check for required API tokens in environment."""
        if not required_keys:
            required_keys = ["GEMINI_API_KEY", "GOOGLE_API_KEY"]
            
        found = []
        missing = []
        for key in required_keys:
            if os.getenv(key):
                found.append(key)
            else:
                missing.append(key)
                
        if missing and not any(k in found for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY"]):
            return False, f"Missing API Keys (At least one Google/Gemini key required for AI changelog/drift): {', '.join(missing)}"
        return True, f"Found API Keys: {', '.join(found)}"

    def run_all_checks(self, registry_url: str = "https://pypi.org/simple") -> bool:
        """Runs all preflight checks and renders a table."""
        console.print("📋 [bold cyan]Running Preflight Checks...[/bold cyan]")
        
        c1_ok, c1_msg = self.check_tooling()
        c2_ok, c2_msg = self.check_registry_access(registry_url)
        c3_ok, c3_msg = self.check_environment_consistency()
        c4_ok, c4_msg = self.check_api_keys()

        table = Table(title="🛡️ Preflight Status")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details", style="dim")

        def status_str(ok):
            return "[green]PASSED[/green]" if ok else "[red]FAILED[/red]"

        table.add_row("Base Tooling", status_str(c1_ok), c1_msg)
        table.add_row("Registry Access", status_str(c2_ok), c2_msg)
        table.add_row("Env Consistency", status_str(c3_ok), c3_msg)
        table.add_row("API Credentials", status_str(c4_ok), c4_msg)

        console.print(table)
        
        # We allow proceeding on env consistency warnings, but fail on tools or registry
        return c1_ok and c2_ok


def run_preflight(target_path: str = ".", registry_url: str = "https://pypi.org/simple") -> bool:
    engine = PreflightEngine(target_path)
    return engine.run_all_checks(registry_url)


if __name__ == "__main__":
    run_preflight()
