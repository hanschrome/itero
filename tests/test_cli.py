"""Tests for CLI."""

import pytest
from pathlib import Path
from typer.testing import CliRunner

from itero.cli import app

runner = CliRunner()


def test_list_from_project_with_workflows(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
) -> None:
    result = runner.invoke(app, ["list"], env={"PYTHONPATH": "src"})
    # Run from cwd - we need to chdir to tmp_project
    result = runner.invoke(
        app,
        ["list", "--project", str(tmp_project)],
    )
    assert result.exit_code == 0
    assert "test-workflow" in result.stdout
    assert "✓" in result.stdout


def test_list_missing_index(tmp_project: Path) -> None:
    # tmp_project has .itero but no workflows.yml
    result = runner.invoke(app, ["list", "--project", str(tmp_project)])
    assert result.exit_code == 0
    assert "workflows.yml" in result.stdout or "none" in result.stdout.lower()


def test_run_workflow(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
    input_file: Path,
) -> None:
    result = runner.invoke(
        app,
        [
            "run",
            "test-workflow",
            str(input_file),
            "--project",
            str(tmp_project),
        ],
    )
    assert result.exit_code == 0
    assert "Run completed" in result.stdout or "Output:" in result.stdout
