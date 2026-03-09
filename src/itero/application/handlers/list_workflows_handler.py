"""Handler: list available workflows and their status."""

from dataclasses import dataclass
from pathlib import Path

from itero.application.commands.list_workflows import ListWorkflowsCommand
from itero.domain.ports import WorkflowLoader


@dataclass
class WorkflowStatus:
    name: str
    description: str
    ok: bool
    error: str | None = None


class ListWorkflowsHandler:
    def __init__(
        self,
        workflow_loader: WorkflowLoader,
    ) -> None:
        self._loader = workflow_loader

    def handle(self, command: ListWorkflowsCommand) -> list[WorkflowStatus]:
        """List workflows and validate each can be loaded."""
        itero_dir = command.project_root / ".itero"
        index_path = itero_dir / "workflows.yml"

        if not index_path.exists():
            return [
                WorkflowStatus(
                    name="(none)",
                    description="",
                    ok=False,
                    error="workflows.yml not found",
                )
            ]

        try:
            refs = self._loader.load_index(index_path)
        except Exception as e:
            return [
                WorkflowStatus(
                    name="(parse error)",
                    description="",
                    ok=False,
                    error=str(e),
                )
            ]

        statuses = []
        for ref in refs:
            workflow_path = itero_dir / ref.file
            if not workflow_path.exists():
                statuses.append(
                    WorkflowStatus(
                        name=ref.name,
                        description=ref.description,
                        ok=False,
                        error=f"File not found: {ref.file}",
                    )
                )
                continue
            try:
                self._loader.load_workflow(workflow_path)
                statuses.append(
                    WorkflowStatus(
                        name=ref.name,
                        description=ref.description,
                        ok=True,
                    )
                )
            except Exception as e:
                statuses.append(
                    WorkflowStatus(
                        name=ref.name,
                        description=ref.description,
                        ok=False,
                        error=str(e),
                    )
                )
        return statuses
