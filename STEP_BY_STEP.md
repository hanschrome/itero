# Step-by-Step: Your First Itero Workflow

This guide walks you through adding Itero to your project and creating a simple Developer → Tester loop. When tests fail, the Tester creates a report and the Developer fixes; when tests pass, the workflow ends.

---

## Part 1: Add Itero to Your Project

### Step 1. Clone Itero

From your project root:

```bash
git clone https://github.com/hanschrome/itero.git
```

Or as a submodule:

```bash
git submodule add https://github.com/hanschrome/itero.git
```

### Step 2. Install Itero

```bash
cd itero && pip install -e .
cd ..
```

Verify it works:

```bash
itero --help
```

### Step 3. Create the Workflows Directory

```bash
mkdir .itero
```

### Step 4. Add `.itero/run/` to Your `.gitignore`

Itero writes execution output to `.itero/run/<uuid>/`. You don't want to commit those:

```bash
echo ".itero/run/" >> .gitignore
```

---

## Part 2: Your First Workflow (Dev → Tester Loop)

### Step 5. Create the Workflow Index

Create `.itero/workflows.yml`:

```yaml
workflows:
  - name: dev-tester
    file: dev-tester.yml
    description: Developer and Tester loop until tests pass
```

### Step 6. Create the Workflow Definition

Create `.itero/dev-tester.yml`:

```yaml
name: Dev + Tester Loop
steps:
  - id: developer
    role: Developer
    agent:
      custom_command: "gemini -y -p '{prompt}'"
    prompt: |
      Implement the changes described in {{input_file}}.
      Read the file and follow the instructions.
    goto: tester

  - id: tester
    role: Tester
    agent:
      custom_command: "gemini -y -p '{prompt}'"
    prompt: |
      Run the project tests (e.g. pytest, npm test, or whatever this project uses).
      If tests FAIL, create a file called test_report.md in {{run_dir}} with the failure output.
      If tests PASS, do NOT create any file.
    goto:
      default: end
      when_files_exist:
        - files: [test_report.md]
          then: developer
```

**What this does:**
- **Developer** reads your input file and implements.
- **Tester** runs tests. If they fail → creates `test_report.md` in the run dir.
- **goto rules:** If `test_report.md` exists → loop back to Developer. Otherwise → end.

### Step 7. Create an Input File

Create `instructions.md` (or any file name) with your task:

```markdown
# Task
Add a new endpoint GET /health that returns {"status": "ok"}.
```

### Step 8. Run the Workflow

From your project root:

```bash
itero run dev-tester instructions.md
```

Itero will run Developer → Tester. If the Tester creates `test_report.md`, it loops back to Developer. When tests pass and no report exists, the workflow ends.

### Step 9. Check Your Workflows

```bash
itero list
```

You should see ✓ next to `dev-tester` if the YAML loads correctly.

---

## Part 3: Going Further

Once the basics work, here's what else you can do:

### Use Another Agent

Replace `gemini -y -p '{prompt}'` with any CLI that accepts a prompt:

| Agent     | Example `custom_command`                    |
|-----------|---------------------------------------------|
| Gemini    | `gemini -y -p '{prompt}'`                   |
| Claude    | `claude -p '{prompt}'` (or your CLI wrapper)|
| Cursor    | `agent -p --force '{prompt}'`               |
| Custom    | `python scripts/my_agent.py '{prompt}'`     |

Placeholders: `{prompt}` (the rendered prompt), `{run_dir}` (execution directory).

### Add Conditions to Steps

Run a step only when certain files exist:

```yaml
- id: fixer
  when:
    run_if_files_exist: [test_report.md]
  # ... rest of step
```

Or skip when a file exists:

```yaml
when:
  run_if_files_not_exist: [done.flag]
```

### End the Workflow from a Condition

Use `then: end` in `goto` when a file signals "no more work":

```yaml
goto:
  default: next_step
  when_files_exist:
    - files: [end_report.md]
      then: end
```

### Multi-Task Pipelines

See `.examples/full-pipeline.yml` for a full flow:
- Tech Lead defines ROADMAP, picks tasks
- Developer implements
- Tester runs tests (loop on failure)
- QA reviews (loop on changes)
- Tech Lead commits and picks next task

### Prompt Variables

Use these in your `prompt:` templates:

| Variable        | Description                      |
|----------------|----------------------------------|
| `{{input_file}}`   | Path to the input file       |
| `{{input_content}}` | Contents of the input file   |
| `{{run_dir}}`       | This run's output directory  |
| `{{project_root}}`  | Your project root path       |
| `{{run_id}}`        | UUID of this run             |

### Makefile Integration

Add to your `Makefile`:

```makefile
run-itero:
	itero run dev-tester instructions.md

list-itero:
	itero list
```

---

## Troubleshooting

- **"workflows.yml not found"** — Run from your project root (the directory that contains `.itero/`).
- **"Workflow 'x' not found"** — Check the `name` in `workflows.yml` matches what you pass to `itero run`.
- **Agent fails** — Ensure the agent CLI is installed and the `custom_command` string is correct. Test it manually: `gemini -y -p "hello"`.
