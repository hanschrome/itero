"""Run context: execution state for a workflow run."""

from pathlib import Path


class ExecutionContext:
    """State passed between workflow steps (files, outputs, variables)."""

    def __init__(
        self,
        run_dir: Path,
        project_root: Path,
        input_file: Path,
        variables: dict[str, str] | None = None,
    ) -> None:
        self.run_dir = run_dir
        self.project_root = project_root
        self.input_file = input_file
        self.variables = variables or {}
        self.step_outputs: dict[str, str] = {}

    def add_step_output(self, step_id: str, output: str) -> None:
        self.step_outputs[step_id] = output
