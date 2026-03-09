"""Factory to create AgentExecutor from YAML config."""

from pathlib import Path

from itero.domain import AgentExecutor
from itero.adapters.agents import CustomCommandAgent


def create_agent(config: dict, cwd: Path) -> AgentExecutor:
    """Create an agent from workflow step config."""
    if "custom_command" in config:
        return CustomCommandAgent(
            command_template=config["custom_command"],
            cwd=cwd,
        )
    raise ValueError(f"Unknown agent config: {config}")
