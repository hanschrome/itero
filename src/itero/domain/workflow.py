"""Domain models for workflows and steps."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepCondition:
    """Condition for when a step should run or where to go next."""

    run_if_files_exist: list[str] = field(default_factory=list)
    run_if_files_not_exist: list[str] = field(default_factory=list)


@dataclass
class GotoRule:
    """Rule for branching to another step based on file existence."""

    files: list[str]
    then: str  # step id


@dataclass
class StepGoto:
    """Where to go after a step completes."""

    default: str  # step id or "end"
    when_files_exist: list[GotoRule] = field(default_factory=list)


@dataclass
class Step:
    """A single workflow step."""

    id: str
    role: str
    agent: dict[str, Any]
    prompt: str
    when: StepCondition | None = None
    goto: StepGoto | str | None = None  # str = simple next step id


@dataclass
class Workflow:
    """Workflow definition with named steps."""

    name: str
    steps: list[Step]
    steps_by_id: dict[str, Step] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        self.steps_by_id = {s.id: s for s in self.steps}


@dataclass
class WorkflowRef:
    """Reference from workflows.yml index."""

    name: str
    file: str
    description: str
