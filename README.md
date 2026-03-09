# Itero: Agent Workflows

Run AI agent workflows directly in your codebase. Define workflows in YAML, execute them where your code lives.

## Why Itero?

Working with AI agents—Claude, Cursor, gemini-cli, and the like—often puts you in a tedious loop: you ask the agent to implement something, run tests yourself, see failures, paste the logs back, and repeat.

**Agent → You run tests → Agent → You run tests → …**

Itero breaks this cycle by letting you define workflows where different roles collaborate autonomously. The agents run the tests, review each other's work, and iterate until done—without you in the middle.

**Simple workflow example:**

- **Developer** — Implements code based on your task
- **Tester** — Runs tests and reports back to the Developer; if all pass, the workflow ends

**Complex workflow example:**

1. **Tech Lead** — Reads your instructions from `TODO.md` and defines the tasks to execute
2. **Tech Lead** — Picks the next task and creates `task{uuid}.md`
3. **Developer** — Implements the changes specified in `task{uuid}.md`
4. **Tester** — Removes `test_report.md`. Runs tests per your project's test instructions; if tests fail, creates `test_report.md`
5. **Developer** — If `test_report.md` exists: fixes issues and goes back to step 4
6. **QA** — Removes `qa.md`. Reviews against the original instructions; if changes are needed, creates `qa.md`
7. **Tech Lead** — If `qa.md` exists: updates `task{uuid}.md` with the new requirements and loops back to step 3
8. **Tech Lead** — Commits and pushes when done

## Overview

Itero is an open source tool that you clone into your project to run agent workflows. Create a `.itero/` directory, add your workflow definitions in YAML, and run them in context of your repository.

**New here?** Follow the **[Step-by-Step Guide](STEP_BY_STEP.md)** to add Itero and create your first Dev → Tester workflow with Gemini.

## Installation

Clone Itero into your project:

```bash
git clone https://github.com/hanschrome/itero.git
```

Or add it as a submodule:

```bash
git submodule add https://github.com/hanschrome/itero.git
```

Install Itero (from the itero directory):

```bash
cd itero && pip install -e .
```

## Quick Start

1. **Create the workflows directory** in your project root:

   ```bash
   mkdir .itero
   ```

2. **Create workflows index** (`.itero/workflows.yml`):

   ```yaml
   workflows:
     - name: dev-with-tests
       file: dev-with-tests.yml
       description: Developer + Tester loop
   ```

3. **Add a workflow** (e.g. `.itero/dev-with-tests.yml`):

   ```yaml
   name: Dev with Tests
   steps:
     - id: developer
       role: Developer
       agent:
         custom_command: "gemini -y -p '{prompt}'"
       prompt: "Implement {{input_file}}"
       goto: tester

     - id: tester
       role: Tester
       agent:
         custom_command: "pytest ."
       prompt: "Run tests. If fail, create test_report001.md in {{run_dir}}"
       goto:
         default: end
         when_files_exist:
           - files: [test_report001.md]
             then: developer
   ```

4. **Run from your project root**:

   ```bash
   itero run dev-with-tests instructions.md
   ```

5. **List workflows** (check which load correctly):

   ```bash
   itero list
   ```

## Project Structure

```
your-project/
├── .itero/               # Your workflows
│   ├── workflows.yml    # Index of workflows
│   ├── dev-with-tests.yml
│   └── ...
├── run/                  # Execution outputs (one UUID per run)
│   └── <uuid>/
│       ├── task001.md
│       └── ...
└── itero/                # Itero (cloned or submodule)
```

Add `run/` to your `.gitignore`.

## Makefile Integration

From your project root, add targets to run Itero:

```makefile
WORKFLOW ?= dev-with-tests
INPUT ?= instructions.md

# Run Itero workflow with default settings
run-itero:
	itero run $(WORKFLOW) $(INPUT)

# Run with local tests workflow (common use case)
run-itero-with-local-tests:
	itero run dev-with-tests $(INPUT)

# List available workflows
list-itero-workflows:
	itero list
```

Usage:

```bash
make run-itero-with-local-tests
# or with custom input
make run-itero WORKFLOW=full-pipeline INPUT=TODO.md
```

## Workflow YAML Reference

### workflows.yml (index)

```yaml
workflows:
  - name: workflow-id      # Used in: itero run workflow-id input.md
    file: workflow-file.yml
    description: Short description
```

### Workflow definition

Each step has:
- **id** — Unique identifier (used for `goto` targeting)
- **role** — Role name (for documentation)
- **agent** — Agent config (e.g. `custom_command: "cmd {prompt}"`). Placeholders: `{prompt}`, `{run_dir}`)
- **prompt** — Template with `{{input_file}}`, `{{run_dir}}`, `{{project_root}}`, `{{input_content}}`, `{{uuid}}` (single or double braces). `{{uuid}}` is refreshed when `tech_lead_pick` runs.
- **when** (optional) — Run only when:
  - `run_if_files_exist: [file1.md]` — All files must exist in run dir
  - `run_if_files_not_exist: [file1.md]` — None may exist
- **goto** (optional) — Next step. Simple: `goto: step_id`. Conditional:

  ```yaml
  goto:
    default: next_step   # or "end"
    when_files_exist:
      - files: [test_report.md]
        then: developer   # Loop back if report exists
      - files: [end_report.md]
        then: end         # End workflow when no more tasks
  ```

### Example workflows

See [.examples/](.examples/) for complete examples, or follow the [Step-by-Step Guide](STEP_BY_STEP.md) for a walkthrough:
- `workflows.yml` — Index
- `simple-dev-tester.yml` — Developer + Tester loop
- `full-pipeline.yml` — Tech Lead, Developer, Tester, QA
- `instructions.md` — Sample input file

## Running Tests

From the itero directory:

```bash
pip install -e ".[dev]"
```

**All tests** (unit + integration):

```bash
pytest tests/ -v
```

**Unit tests only:**

```bash
pytest tests/ -v --ignore=tests/integration/
```

**Integration tests only** (full workflows with echo-based agents, no real LLM):

```bash
pytest tests/integration/ -v
```

**With coverage:**

```bash
pytest tests/ -v --cov=itero --cov-report=term-missing
```

**Integration tests** (`tests/integration/`) cover:
- Loading and running `.examples` workflows (simple-dev-tester, full-pipeline)
- Linear flow (step A → step B → end)
- GOTO loop when file exists (tester creates report → back to developer)
- `when` conditions: skip step when `run_if_files_exist` is not met
- `when` conditions: run step when file created by previous step

## Known Limitations

- **Single agent type:** Only `custom_command` is supported. Use it to call any CLI (e.g. `gemini -y -p "{prompt}"`, `cursor agent -p "{prompt}"`). Native adapters for Cursor, Claude, or Gemini may come in future versions.
- **No parallel steps:** Steps run sequentially.
- **Max 100 steps per run:** Workflows hit a safety limit to prevent infinite loops.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.
