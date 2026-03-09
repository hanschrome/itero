"""Adapter: executes a custom shell command as the agent.

Implements the domain's AgentExecutor interface.
"""

import subprocess
from pathlib import Path

from itero.domain import AgentExecutor
from itero.domain.run_context import ExecutionContext


class CustomCommandAgent(AgentExecutor):
    """Runs a user-defined command. Placeholders: {prompt}, {run_dir}.

    Example YAML config:
        agent:
          custom_command: "gemini -y -p {prompt}"
        # Or to write to run dir:
        agent:
          custom_command: "echo {prompt} > {run_dir}/output.md"
    """

    def __init__(self, command_template: str, cwd: Path | None = None):
        self._command = command_template
        self._cwd = cwd or Path.cwd()

    def execute(self, prompt: str, context: ExecutionContext) -> str:
        cmd = self._command.format(
            prompt=prompt,
            run_dir=str(context.run_dir),
        )
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=self._cwd,
            capture_output=True,
            text=True,
        )
        result.check_returncode()
        return result.stdout
