"""Tests for condition evaluator."""

import pytest
from pathlib import Path

from itero.domain import Step, StepCondition, StepGoto, GotoRule
from itero.domain.ports import FileSystem
from itero.application.condition_evaluator import should_run_step, resolve_goto


class FakeFS:
    def __init__(self, existing: set[str]) -> None:
        self._existing = existing

    def exists(self, path: Path) -> bool:
        return path.name in self._existing or str(path) in self._existing


def test_should_run_step_no_when() -> None:
    step = Step(id="x", role="R", agent={}, prompt="")
    assert should_run_step(step, Path("/run"), FakeFS({"a"})) is True


def test_should_run_step_run_if_files_exist_all_present() -> None:
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        when=StepCondition(run_if_files_exist=["a.md", "b.md"]),
    )
    assert should_run_step(step, Path("/run"), FakeFS({"a.md", "b.md"})) is True


def test_should_run_step_run_if_files_exist_missing() -> None:
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        when=StepCondition(run_if_files_exist=["a.md"]),
    )
    assert should_run_step(step, Path("/run"), FakeFS(set())) is False


def test_should_run_step_run_if_files_not_exist() -> None:
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        when=StepCondition(run_if_files_not_exist=["done.flag"]),
    )
    assert should_run_step(step, Path("/run"), FakeFS(set())) is True
    assert should_run_step(step, Path("/run"), FakeFS({"done.flag"})) is False


def test_resolve_goto_simple_string() -> None:
    step = Step(id="x", role="R", agent={}, prompt="", goto="next_step")
    assert resolve_goto(step, Path("/run"), FakeFS(set())) == "next_step"


def test_resolve_goto_with_when_files_exist_matched() -> None:
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        goto=StepGoto(
            default="end",
            when_files_exist=[GotoRule(files=["report.md"], then="developer")],
        ),
    )
    assert resolve_goto(step, Path("/run"), FakeFS({"report.md"})) == "developer"


def test_resolve_goto_with_when_files_exist_not_matched() -> None:
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        goto=StepGoto(
            default="end",
            when_files_exist=[GotoRule(files=["report.md"], then="developer")],
        ),
    )
    assert resolve_goto(step, Path("/run"), FakeFS(set())) == "end"


def test_resolve_goto_none_defaults_end() -> None:
    step = Step(id="x", role="R", agent={}, prompt="", goto=None)
    assert resolve_goto(step, Path("/run"), FakeFS(set())) == "end"


def test_resolve_goto_when_files_exist_then_end() -> None:
    """GOTO rule with then: end (full-pipeline style)."""
    step = Step(
        id="x",
        role="R",
        agent={},
        prompt="",
        goto=StepGoto(
            default="developer",
            when_files_exist=[GotoRule(files=["end_report.md"], then="end")],
        ),
    )
    assert resolve_goto(step, Path("/run"), FakeFS({"end_report.md"})) == "end"
    assert resolve_goto(step, Path("/run"), FakeFS(set())) == "developer"
