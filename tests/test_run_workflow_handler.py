"""Tests for RunWorkflowHandler."""

import pytest
from pathlib import Path

from itero.adapters.fs import RealFileSystem
from itero.adapters.loaders import YamlWorkflowLoader
from itero.application.commands import RunWorkflowCommand
from itero.application.handlers import RunWorkflowHandler


def test_run_workflow_completes(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
    input_file: Path,
) -> None:
    run_dir = tmp_project / "run"
    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=run_dir,
    )
    result = handler.handle(
        RunWorkflowCommand(
            workflow_name="test-workflow",
            input_file=input_file,
            project_root=tmp_project,
        )
    )
    assert result.exists()
    assert result.parent == run_dir
    assert len(list(result.iterdir())) >= 0  # Run dir created


def test_run_workflow_workflow_not_found(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
    input_file: Path,
) -> None:
    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=tmp_project / "run",
    )
    with pytest.raises(ValueError, match="not found"):
        handler.handle(
            RunWorkflowCommand(
                workflow_name="nonexistent",
                input_file=input_file,
                project_root=tmp_project,
            )
        )


def test_run_workflow_input_not_found(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
) -> None:
    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=tmp_project / "run",
    )
    with pytest.raises(FileNotFoundError):
        handler.handle(
            RunWorkflowCommand(
                workflow_name="test-workflow",
                input_file=tmp_project / "missing.md",
                project_root=tmp_project,
            )
        )
