"""Evaluate step conditions based on file existence in run dir."""

from pathlib import Path

from itero.domain import Step, StepCondition
from itero.domain.ports import FileSystem


def should_run_step(step: Step, run_dir: Path, fs: FileSystem) -> bool:
    """Check if step should run based on when conditions."""
    if step.when is None:
        return True
    when = step.when
    for f in when.run_if_files_exist:
        if not fs.exists(run_dir / f):
            return False
    for f in when.run_if_files_not_exist:
        if fs.exists(run_dir / f):
            return False
    return True


def resolve_goto(
    step: Step, run_dir: Path, fs: FileSystem
) -> str:
    """Resolve next step id based on goto rules and file existence."""
    if step.goto is None:
        return "end"
    if isinstance(step.goto, str):
        return step.goto
    # StepGoto
    for rule in step.goto.when_files_exist:
        if all(fs.exists(run_dir / f) for f in rule.files):
            return rule.then
    return step.goto.default
