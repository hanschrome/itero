"""Pytest fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project with .itero directory."""
    itero_dir = tmp_path / ".itero"
    itero_dir.mkdir()
    return tmp_path


@pytest.fixture
def workflows_yml(tmp_project: Path) -> Path:
    """Create workflows.yml in project."""
    path = tmp_project / ".itero" / "workflows.yml"
    path.write_text("""
workflows:
  - name: test-workflow
    file: test-workflow.yml
    description: Test workflow
""")
    return path


@pytest.fixture
def test_workflow_yml(tmp_project: Path) -> Path:
    """Create a minimal test workflow."""
    path = tmp_project / ".itero" / "test-workflow.yml"
    path.write_text("""
name: Test Workflow
steps:
  - id: step1
    role: Test
    agent:
      custom_command: "echo 'Got: {prompt}'"
    prompt: "Hello {{input_file}}"
    goto: end
""")
    return path


@pytest.fixture
def input_file(tmp_project: Path) -> Path:
    """Create sample input file."""
    path = tmp_project / "instructions.md"
    path.write_text("# Instructions\nDo something.\n")
    return path
