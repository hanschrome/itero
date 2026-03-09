"""Command: run a workflow."""

from pathlib import Path


class RunWorkflowCommand:
    def __init__(
        self,
        workflow_name: str,
        input_file: Path,
        project_root: Path,
    ) -> None:
        self.workflow_name = workflow_name
        self.input_file = input_file
        self.project_root = project_root
