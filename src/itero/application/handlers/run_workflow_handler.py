"""Handler: run a workflow."""

import uuid
from collections.abc import Callable
from pathlib import Path

from itero.application.agent_factory import create_agent
from itero.application.condition_evaluator import (
    resolve_goto,
    should_run_step,
)
from itero.application.commands.run_workflow import RunWorkflowCommand
from itero.application.prompt_renderer import render_prompt
from itero.domain import Workflow
from itero.domain.ports import FileSystem, WorkflowLoader
from itero.domain.run_context import ExecutionContext


class RunWorkflowHandler:
    def __init__(
        self,
        workflow_loader: WorkflowLoader,
        file_system: FileSystem,
        run_base_dir: Path,
        on_step_complete: Callable[[str, str, str], None] | None = None,
    ) -> None:
        self._loader = workflow_loader
        self._fs = file_system
        self._run_base = run_base_dir
        self._on_step_complete = on_step_complete

    def handle(self, command: RunWorkflowCommand) -> Path:
        """Execute workflow, return run directory path."""
        itero_dir = command.project_root / ".itero"
        index_path = itero_dir / "workflows.yml"
        if not self._fs.exists(index_path):
            raise FileNotFoundError(
                f"workflows.yml not found at {itero_dir}"
            )

        refs = self._loader.load_index(index_path)
        ref = next((r for r in refs if r.name == command.workflow_name), None)
        if not ref:
            raise ValueError(
                f"Workflow '{command.workflow_name}' not found in workflows.yml"
            )

        workflow_path = itero_dir / ref.file
        if not self._fs.exists(workflow_path):
            raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

        if not self._fs.exists(command.input_file):
            raise FileNotFoundError(
                f"Input file not found: {command.input_file}"
            )

        workflow = self._loader.load_workflow(workflow_path)
        run_id = str(uuid.uuid4())
        run_dir = self._run_base / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        context = ExecutionContext(
            run_dir=run_dir,
            project_root=command.project_root,
            input_file=command.input_file,
            variables={"run_id": run_id},
        )

        self._execute_workflow(workflow, context)
        return run_dir

    def _execute_workflow(
        self, workflow: Workflow, context: ExecutionContext
    ) -> None:
        visited: set[str] = set()
        max_steps = 100
        step_count = 0
        current_id = workflow.steps[0].id if workflow.steps else None

        while current_id and current_id != "end" and step_count < max_steps:
            step_count += 1
            if current_id not in workflow.steps_by_id:
                raise ValueError(f"Unknown step id: {current_id}")

            step = workflow.steps_by_id[current_id]

            if not should_run_step(step, context.run_dir, self._fs):
                current_id = resolve_goto(step, context.run_dir, self._fs)
                continue

            agent = create_agent(step.agent, context.project_root)
            prompt = render_prompt(step.prompt, context)
            output = agent.execute(prompt, context)
            context.add_step_output(step.id, output)

            if self._on_step_complete:
                self._on_step_complete(step.id, step.role, output)

            current_id = resolve_goto(step, context.run_dir, self._fs)
