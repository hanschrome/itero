# Roadmap

Planned features and improvements for Itero.

## Planned

- **Prompt escaping** — Escape special characters in prompts before passing to shell so `$`, quotes, and similar do not break the command.
- **Agents** — Native adapters for Cursor, Claude, Gemini (API or CLI). Keep `custom_command` as fallback.
- **Dry run** — Simulate workflow execution without running agents. Show which steps would run and in what order.
- **Streaming** — Stream agent output to the terminal in real time instead of waiting until each step finishes.
- **Timeout** — Per-step and per-run timeout to avoid hung agents.
- **PyPI** — Publish to PyPI so users can `pip install itero` without cloning.
- **YAML validation** — Validate workflow schema before execution. Catch typos (e.g. `got` vs `goto`) early.
- **Linting** — Add ruff, black, and/or mypy for code quality.
- **CI (GitHub Actions)** — Run tests on push and pull requests.
- **Persist outputs** — Write each step’s output to files in the run directory for inspection and debugging.
- **Resume** — Resume a failed run from a specific step instead of starting over.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) if you want to help implement any of these.
