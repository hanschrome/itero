"""Command: list available workflows."""

from pathlib import Path


class ListWorkflowsCommand:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
