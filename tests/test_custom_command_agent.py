"""Tests for CustomCommandAgent."""

import pytest
from pathlib import Path

from itero.adapters.agents import CustomCommandAgent
from itero.domain.run_context import ExecutionContext


def test_execute_echo(tmp_path: Path) -> None:
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
    )
    agent = CustomCommandAgent(
        command_template="echo 'Output: {prompt}'",
        cwd=tmp_path,
    )
    result = agent.execute("hello world", ctx)
    assert "Output: hello world" in result or "hello world" in result


def test_execute_sets_cwd(tmp_path: Path) -> None:
    """Agent runs in project root (cwd)."""
    ctx = ExecutionContext(
        run_dir=tmp_path / "run",
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
    )
    agent = CustomCommandAgent(
        command_template="pwd",
        cwd=tmp_path,
    )
    result = agent.execute("", ctx)
    assert str(tmp_path) in result or tmp_path.name in result


def test_execute_run_dir_placeholder(tmp_path: Path) -> None:
    """Agent can use {run_dir} placeholder to write to run directory."""
    run_dir = tmp_path / "run" / "abc123"
    run_dir.mkdir(parents=True)
    ctx = ExecutionContext(
        run_dir=run_dir,
        project_root=tmp_path,
        input_file=tmp_path / "x.md",
    )
    agent = CustomCommandAgent(
        command_template="echo ok > {run_dir}/output.txt",
        cwd=tmp_path,
    )
    agent.execute("", ctx)
    assert (run_dir / "output.txt").read_text().strip() == "ok"
