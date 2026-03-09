"""Tests for ListWorkflowsHandler."""

import pytest
from pathlib import Path

from itero.adapters.loaders import YamlWorkflowLoader
from itero.application.commands import ListWorkflowsCommand
from itero.application.handlers import ListWorkflowsHandler, WorkflowStatus


def test_list_workflows_ok(
    tmp_project: Path,
    workflows_yml: Path,
    test_workflow_yml: Path,
) -> None:
    loader = YamlWorkflowLoader()
    handler = ListWorkflowsHandler(workflow_loader=loader)
    statuses = handler.handle(ListWorkflowsCommand(project_root=tmp_project))
    assert len(statuses) == 1
    assert statuses[0].name == "test-workflow"
    assert statuses[0].ok is True


def test_list_workflows_file_not_found(
    tmp_project: Path,
    workflows_yml: Path,
) -> None:
    # workflows.yml references test-workflow.yml but we don't create it
    loader = YamlWorkflowLoader()
    handler = ListWorkflowsHandler(workflow_loader=loader)
    statuses = handler.handle(ListWorkflowsCommand(project_root=tmp_project))
    assert len(statuses) == 1
    assert statuses[0].ok is False
    assert "not found" in statuses[0].error or "File" in statuses[0].error


def test_list_workflows_missing_index(tmp_project: Path) -> None:
    # No workflows.yml
    loader = YamlWorkflowLoader()
    handler = ListWorkflowsHandler(workflow_loader=loader)
    statuses = handler.handle(ListWorkflowsCommand(project_root=tmp_project))
    assert len(statuses) == 1
    assert statuses[0].ok is False
    assert "workflows.yml" in statuses[0].error or "not found" in statuses[0].error
