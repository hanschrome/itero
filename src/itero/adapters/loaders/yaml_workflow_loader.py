"""Adapter: loads workflows from YAML files."""

from pathlib import Path

import yaml

from itero.domain import (
    GotoRule,
    Step,
    StepCondition,
    StepGoto,
    Workflow,
    WorkflowRef,
)


class YamlWorkflowLoader:
    """Load workflow index and definitions from YAML."""

    def load_index(self, path: Path) -> list[WorkflowRef]:
        data = yaml.safe_load(path.read_text())
        if not data or "workflows" not in data:
            return []
        refs = []
        for w in data["workflows"]:
            refs.append(
                WorkflowRef(
                    name=w["name"],
                    file=w["file"],
                    description=w.get("description", ""),
                )
            )
        return refs

    def load_workflow(self, path: Path) -> Workflow:
        data = yaml.safe_load(path.read_text())
        if not data:
            raise ValueError(f"Empty workflow file: {path}")
        name = data.get("name", path.stem)
        raw_steps = data.get("steps", [])
        steps = []
        for i, s in enumerate(raw_steps):
            default_next = (
                raw_steps[i + 1]["id"] if i + 1 < len(raw_steps) else "end"
            )
            step = self._parse_step(s, default_next)
            steps.append(step)
        return Workflow(name=name, steps=steps)

    def _parse_step(self, s: dict, default_next: str = "end") -> Step:
        step_id = s["id"]
        role = s.get("role", "")
        agent = s.get("agent", {})
        prompt = s.get("prompt", "")

        when = None
        if "when" in s:
            w = s["when"]
            when = StepCondition(
                run_if_files_exist=w.get("run_if_files_exist", []),
                run_if_files_not_exist=w.get("run_if_files_not_exist", []),
            )

        goto = StepGoto(default=default_next, when_files_exist=[])
        if "goto" in s:
            g = s["goto"]
            if isinstance(g, str):
                goto = StepGoto(default=g, when_files_exist=[])
            else:
                rules = []
                for rule in g.get("when_files_exist", []):
                    rules.append(
                        GotoRule(files=rule["files"], then=rule["then"])
                    )
                goto = StepGoto(
                    default=g.get("default", default_next),
                    when_files_exist=rules,
                )

        return Step(
            id=step_id,
            role=role,
            agent=agent,
            prompt=prompt,
            when=when,
            goto=goto,
        )
