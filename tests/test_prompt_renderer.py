"""Tests for prompt renderer."""

import pytest
from pathlib import Path

from itero.domain.run_context import ExecutionContext
from itero.application.prompt_renderer import render_prompt


def test_render_input_file(tmp_path: Path) -> None:
    input_file = tmp_path / "todo.md"
    input_file.write_text("# Task")
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=input_file,
    )
    result = render_prompt("Read {{input_file}}", ctx)
    assert str(input_file) in result


def test_render_input_content(tmp_path: Path) -> None:
    input_file = tmp_path / "todo.md"
    input_file.write_text("# Task")
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=input_file,
    )
    result = render_prompt("Content: {{input_content}}", ctx)
    assert "# Task" in result


def test_render_run_dir(tmp_path: Path) -> None:
    run_dir = tmp_path / "run" / "abc"
    ctx = ExecutionContext(
        run_dir=run_dir,
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
    )
    result = render_prompt("Output to {{run_dir}}", ctx)
    assert str(run_dir) in result


def test_render_variables(tmp_path: Path) -> None:
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
        variables={"foo": "bar"},
    )
    result = render_prompt("Var: {{foo}}", ctx)
    assert "bar" in result


def test_render_uuid_double_brace(tmp_path: Path) -> None:
    """Support task_{{uuid}}.md double-brace placeholder."""
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
        variables={"uuid": "xyz-789"},
    )
    result = render_prompt("Read task_{{uuid}}.md", ctx)
    assert "task_xyz-789.md" in result
