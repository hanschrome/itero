"""Integration tests: full workflow execution with echo-based agents."""

import pytest
from pathlib import Path

from itero.adapters.fs import RealFileSystem
from itero.adapters.loaders import YamlWorkflowLoader
from itero.application.commands import RunWorkflowCommand
from itero.application.handlers import RunWorkflowHandler


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Project with .itero configured."""
    (tmp_path / ".itero").mkdir()
    return tmp_path


@pytest.fixture
def input_file(project_root: Path) -> Path:
    path = project_root / "instructions.md"
    path.write_text("# Task\nImplement feature X.\n")
    return path


# --- Use case 1: Load and run .examples workflows (simple-dev-tester, full-pipeline) ---


def test_integration_loads_and_runs_simple_dev_tester(
    project_root: Path, input_file: Path
) -> None:
    """Load actual .examples/simple-dev-tester.yml and run to completion."""
    examples_dir = Path(__file__).parent.parent.parent / ".examples"
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: simple-dev-tester
    file: simple-dev-tester.yml
    description: Dev + Tester
""")
    # Copy workflow from examples
    workflow_src = examples_dir / "simple-dev-tester.yml"
    (project_root / ".itero" / "simple-dev-tester.yml").write_text(
        workflow_src.read_text()
    )

    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    run_dir = project_root / "run"
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=run_dir,
    )

    result = handler.handle(
        RunWorkflowCommand(
            workflow_name="simple-dev-tester",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()
    assert result.parent == run_dir
    assert result.name  # UUID dir


def test_integration_loads_and_runs_full_pipeline(
    project_root: Path, input_file: Path
) -> None:
    """Load actual .examples/full-pipeline.yml and run to completion."""
    examples_dir = Path(__file__).parent.parent.parent / ".examples"
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: full-pipeline
    file: full-pipeline.yml
    description: Tech Lead, Dev, Tester, QA
""")
    (project_root / ".itero" / "full-pipeline.yml").write_text(
        (examples_dir / "full-pipeline.yml").read_text()
    )

    loader = YamlWorkflowLoader()
    fs = RealFileSystem()
    handler = RunWorkflowHandler(
        workflow_loader=loader,
        file_system=fs,
        run_base_dir=project_root / "run",
    )

    result = handler.handle(
        RunWorkflowCommand(
            workflow_name="full-pipeline",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()


# --- Use case 2: Linear flow (developer -> tester -> end) ---


def test_integration_linear_flow_both_steps_execute(
    project_root: Path, input_file: Path
) -> None:
    """Both steps run in sequence; workflow ends at 'end'."""
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: linear
    file: linear.yml
    description: Linear flow
""")
    (project_root / ".itero" / "linear.yml").write_text("""
name: Linear
steps:
  - id: step_a
    role: A
    agent:
      custom_command: "echo 'A: {prompt}'"
    prompt: "First"
    goto: step_b
  - id: step_b
    role: B
    agent:
      custom_command: "echo 'B: {prompt}'"
    prompt: "Second"
    goto: end
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
            workflow_name="linear",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()


# --- Use case 3: GOTO loop when file exists (tester creates report -> back to developer) ---


def test_integration_goto_loop_when_file_exists(
    project_root: Path, input_file: Path
) -> None:
    """Tester creates test_report001.md -> goto developer; second run deletes it -> end."""
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: goto-loop
    file: goto-loop.yml
    description: GOTO on file exists
""")
    # Tester: first run creates file (goto->developer), second run deletes it (goto->end)
    (project_root / ".itero" / "goto-loop.yml").write_text("""
name: GOTO Loop
steps:
  - id: developer
    role: Developer
    agent:
      custom_command: "echo 'Dev: {prompt}'"
    prompt: "Implement"
    goto: tester
  - id: tester
    role: Tester
    agent:
      custom_command: |
        echo "Tester: {prompt}"
        if [ -f {run_dir}/test_report001.md ]; then
          rm {run_dir}/test_report001.md
        else
          touch {run_dir}/test_report001.md
        fi
    prompt: "Run tests"
    goto:
      default: end
      when_files_exist:
        - files: [test_report001.md]
          then: developer
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
            workflow_name="goto-loop",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()
    # developer ran at least once, tester ran twice (create + delete), then end


# --- Use case 4: when condition skips step (run_if_files_exist not met) ---


def test_integration_when_condition_skips_step(
    project_root: Path, input_file: Path
) -> None:
    """Step with run_if_files_exist is skipped when file does not exist."""
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: when-skip
    file: when-skip.yml
    description: Skip when condition
""")
    (project_root / ".itero" / "when-skip.yml").write_text("""
name: When Skip
steps:
  - id: first
    role: First
    agent:
      custom_command: "echo 'First'"
    prompt: "Run"
    goto: conditional
  - id: conditional
    role: Conditional
    agent:
      custom_command: "echo 'Should not run'"
    prompt: "Skip me"
    when:
      run_if_files_exist: [missing_file.md]
    goto: end
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
            workflow_name="when-skip",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()
    # Conditional step should not have run (no missing_file.md), so we go to end via goto


# --- Use case 5: when condition runs step when file exists ---


def test_integration_when_condition_runs_step_when_file_exists(
    project_root: Path, input_file: Path
) -> None:
    """Step with run_if_files_exist runs when file is created by previous step."""
    (project_root / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: when-run
    file: when-run.yml
    description: Run when file exists
""")
    (project_root / ".itero" / "when-run.yml").write_text("""
name: When Run
steps:
  - id: creator
    role: Creator
    agent:
      custom_command: "echo 'Create' && touch {run_dir}/task001.md"
    prompt: "Create task"
    goto: consumer
  - id: consumer
    role: Consumer
    agent:
      custom_command: "echo 'Consumer ran: {prompt}'"
    prompt: "Process task"
    when:
      run_if_files_exist: [task001.md]
    goto: end
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
            workflow_name="when-run",
            input_file=input_file,
            project_root=project_root,
        )
    )

    assert result.exists()
    assert (result / "task001.md").exists()
    # Both creator and consumer should have run
