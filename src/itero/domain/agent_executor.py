"""Domain port: interface for executing agent prompts.

The domain defines what it needs; adapters provide the implementation.
"""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from itero.domain.run_context import ExecutionContext


@runtime_checkable
class AgentExecutor(Protocol):
    """Execute a prompt and return the agent's response.

    Implementations may call Claude, Cursor, gemini-cli, or any custom command.
    """

    def execute(self, prompt: str, context: "ExecutionContext") -> str:
        """Run the agent with the given prompt and context.

        Args:
            prompt: The prompt to send to the agent.
            context: Current execution state (files, previous outputs, etc.).

        Returns:
            The agent's response text.
        """
        ...
