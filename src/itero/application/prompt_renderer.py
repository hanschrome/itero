"""Render prompts with variables from context."""

from pathlib import Path

from itero.domain.run_context import ExecutionContext


def render_prompt(template: str, context: ExecutionContext) -> str:
    """Replace {{variable}} placeholders with context values."""
    vars_map = {
        "input_file": str(context.input_file),
        "input_content": context.input_file.read_text()
        if context.input_file.exists()
        else "",
        "run_dir": str(context.run_dir),
        "project_root": str(context.project_root),
    }
    vars_map.update(context.variables)
    vars_map.update(
        {f"step_output_{k}": v for k, v in context.step_outputs.items()}
    )
    result = template
    for key, val in vars_map.items():
        result = result.replace(f"{{{{{key}}}}}", str(val))
    return result
