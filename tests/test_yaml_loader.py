"""Tests for YAML workflow loader."""

import pytest
from pathlib import Path

from itero.adapters.loaders import YamlWorkflowLoader


def test_load_index(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "workflows.yml").write_text("""
workflows:
  - name: w1
    file: w1.yml
    description: First
  - name: w2
    file: w2.yml
""")
    loader = YamlWorkflowLoader()
    refs = loader.load_index(tmp_project / ".itero" / "workflows.yml")
    assert len(refs) == 2
    assert refs[0].name == "w1"
    assert refs[0].file == "w1.yml"
    assert refs[0].description == "First"
    assert refs[1].name == "w2"
    assert refs[1].description == ""


def test_load_index_empty(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "workflows.yml").write_text("")
    loader = YamlWorkflowLoader()
    refs = loader.load_index(tmp_project / ".itero" / "workflows.yml")
    assert refs == []


def test_load_index_no_workflows_key(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "workflows.yml").write_text("foo: bar")
    loader = YamlWorkflowLoader()
    refs = loader.load_index(tmp_project / ".itero" / "workflows.yml")
    assert refs == []


def test_load_workflow(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "w.yml").write_text("""
name: My Workflow
steps:
  - id: a
    role: Dev
    agent:
      custom_command: "echo {prompt}"
    prompt: "Do it"
    goto: b
  - id: b
    role: Test
    agent:
      custom_command: "pytest"
    prompt: "Test"
""")
    loader = YamlWorkflowLoader()
    wf = loader.load_workflow(tmp_project / ".itero" / "w.yml")
    assert wf.name == "My Workflow"
    assert len(wf.steps) == 2
    assert wf.steps[0].id == "a"
    assert wf.steps[0].goto.default == "b"
    assert wf.steps[1].goto.default == "end"


def test_load_workflow_with_when_and_goto_rules(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "w.yml").write_text("""
name: Conditional
steps:
  - id: tester
    role: Tester
    agent:
      custom_command: "echo {prompt}"
    prompt: "Test"
    when:
      run_if_files_exist: [task001.md]
      run_if_files_not_exist: [done.flag]
    goto:
      default: end
      when_files_exist:
        - files: [test_report001.md]
          then: developer
  - id: developer
    role: Developer
    agent:
      custom_command: "echo {prompt}"
    prompt: "Fix"
""")
    loader = YamlWorkflowLoader()
    wf = loader.load_workflow(tmp_project / ".itero" / "w.yml")
    step = wf.steps[0]
    assert step.when is not None
    assert step.when.run_if_files_exist == ["task001.md"]
    assert step.when.run_if_files_not_exist == ["done.flag"]
    assert step.goto is not None
    assert len(step.goto.when_files_exist) == 1
    assert step.goto.when_files_exist[0].files == ["test_report001.md"]
    assert step.goto.when_files_exist[0].then == "developer"


def test_load_workflow_empty_raises(tmp_project: Path) -> None:
    (tmp_project / ".itero" / "w.yml").write_text("")
    loader = YamlWorkflowLoader()
    with pytest.raises(ValueError, match="Empty workflow"):
        loader.load_workflow(tmp_project / ".itero" / "w.yml")
