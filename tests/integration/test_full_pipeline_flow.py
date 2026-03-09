"""Integration tests for full-pipeline style flow (ROADMAP, task_{uuid}, end_report)."""

import pytest
from pathlib import Path

from itero.adapters.fs import RealFileSystem
from itero.adapters.loaders import YamlWorkflowLoader
from itero.application.commands import RunWorkflowCommand
from itero.application.handlers import RunWorkflowHandler


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / ".itero").mkdir()
    return tmp_path


@pytest.fixture
def input_file(project_root: Path) -> Path:
    path = project_root / "instructions.md"
    path.write_text("# Task\nImplement feature X.\n")
    return path


def test_full_pipeline_style_roadmap_and_end_report(
    project_root: Path, input_file: Path
) -> None:
    """Simulate full-pipeline: ROADMAP.md -> pick creates end_report -> goto end."""
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: pipeline
    file: pipeline.yml
    description: Pipeline with ROADMAP and end_report
""")
    (project_root / ".itero" / "pipeline.yml").write_text("""
name: Pipeline
steps:
  - id: define
    role: Tech Lead
    agent:
      custom_command: "echo 'Define' && touch {run_dir}/ROADMAP.md"
    prompt: "Create ROADMAP"
    goto: pick
  - id: pick
    role: Tech Lead
    agent:
      custom_command: |
        echo "Pick"
        if [ -f {run_dir}/end_report.md ]; then
          rm {run_dir}/end_report.md
        else
          touch {run_dir}/end_report.md
        fi
    prompt: "Pick task"
    when:
      run_if_files_exist: [ROADMAP.md]
    goto:
      default: developer
      when_files_exist:
        - files: [end_report.md]
          then: end
  - id: developer
    role: Developer
    agent:
      custom_command: "echo 'Dev'"
    prompt: "Implement"
    when:
      run_if_files_exist: [ROADMAP.md]
    goto: pick
""")

    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=project_root / "run",
    )

    result = handler.handle(
        RunWorkflowCommand(
            workflow_name="pipeline",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()
    assert (result / "ROADMAP.md").exists()

