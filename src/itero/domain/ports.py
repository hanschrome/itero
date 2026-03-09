"""Domain ports: interfaces the domain needs from the outside."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from itero.domain.workflow import Workflow, WorkflowRef


@runtime_checkable
class FileSystem(Protocol):
    """File system operations (for testing and sandboxing)."""

    def exists(self, path: Path) -> bool:
        """Check if file/dir exists."""
        ...

    def read_text(self, path: Path) -> str:
        """Read file contents."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write file contents."""
        ...


@runtime_checkable
class WorkflowLoader(Protocol):
    """Load workflow index and definitions."""

    def load_index(self, path: Path) -> list[WorkflowRef]:
        """Load workflows.yml and return list of workflow refs."""
        ...

    def load_workflow(self, path: Path) -> Workflow:
        """Load a single workflow definition from YAML."""
        ...
