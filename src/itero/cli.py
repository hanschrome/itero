#!/usr/bin/env python3
"""Itero CLI: run agent workflows from your codebase."""

import sys
from pathlib import Path

import typer

from itero.adapters.fs import RealFileSystem
from itero.adapters.loaders import YamlWorkflowLoader
from itero.application.commands import ListWorkflowsCommand, RunWorkflowCommand
from itero.application.handlers import (
    ListWorkflowsHandler,
    RunWorkflowHandler,
)

app = typer.Typer(
    name="itero",
    help="Run AI agent workflows from your codebase.",
)


def _get_project_root() -> Path:
    """Project root = cwd (must contain .itero/)."""
    root = Path.cwd()
    if not (root / ".itero").exists():
        typer.echo(
            "Error: .itero/ not found. Run from your project root.",
            err=True,
        )
        raise typer.Exit(1)
    return root


def _get_run_dir(project_root: Path) -> Path:
    """Run directory for this itero installation (under .itero/ to avoid collisions)."""
    return project_root / ".itero" / "run"


@app.command("list")
def list_workflows(
    project_root: Path = typer.Option(
        None,
        "--project",
        "-p",
        path_type=Path,
        help="Project root (default: current directory)",
    ),
) -> None:
    """List workflows from .itero/workflows.yml and show load status."""
    root = project_root or Path.cwd()
    loader = YamlWorkflowLoader()
    handler = ListWorkflowsHandler(workflow_loader=loader)
    statuses = handler.handle(ListWorkflowsCommand(project_root=root))

    for s in statuses:
        icon = "✓" if s.ok else "✗"
        typer.echo(f"  {icon} {s.name}: {s.description or '(no description)'}")
        if not s.ok and s.error:
            typer.echo(f"      Error: {s.error}")


@app.command("run")
def run_workflow(
    workflow_name: str = typer.Argument(..., help="Workflow name from workflows.yml"),
    input_file: str = typer.Argument(..., help="Input file path (e.g. instructions.md)"),
    project_root: Path = typer.Option(
        None,
        "--project",
        "-p",
        path_type=Path,
        help="Project root (default: current directory)",
    ),
) -> None:
    """Run a workflow with the given input file."""
    root = project_root or _get_project_root()
    input_path = root / input_file if not Path(input_file).is_absolute() else Path(input_file)

    run_dir = _get_run_dir(root)
    loader = YamlWorkflowLoader()
    fs = RealFileSystem()

    def _on_step_complete(step_id: str, role: str, output: str) -> None:
        typer.echo(f"  ✓ {step_id} ({role}) completed")
        if output.strip():
            stripped = output.strip()
            preview = ("..." + stripped[-200:]) if len(stripped) > 200 else stripped
            for line in preview.split("\n"):
                typer.echo(f"    {line}")

    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=run_dir,
        on_step_complete=_on_step_complete,
    )

    try:
        result_dir = handler.handle(
            RunWorkflowCommand(
                workflow_name=workflow_name,
                input_file=input_path,
                project_root=root,
            )
        )
        typer.echo(f"Run completed. Output: {result_dir}")
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
