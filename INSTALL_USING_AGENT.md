# Install Itero Using an AI Agent

Instructions for AI agents (Gemini, Claude, Cursor, Aider, etc.) to install Itero in a user's codebase.

## Prerequisites

- Python 3.11+
- User runs commands from their **project root** (the directory containing their code)

## Step 1. Clone Itero

From the project root:

```bash
git clone https://github.com/hanschrome/itero.git
```

Or as a submodule:

```bash
git submodule add https://github.com/hanschrome/itero.git
```

## Step 2. Install Itero

```bash
cd itero && pip install -e . && cd ..
```

## Step 3. Create `.itero/` Directory

```bash
mkdir -p .itero
```

## Step 4. Add Workflow Files

Create `.itero/workflows.yml`:

```yaml
workflows:
  - name: simple-dev-tester
    file: simple-dev-tester.yml
    description: Developer + Tester loop (simplest example)

  - name: full-pipeline
    file: full-pipeline.yml
    description: Tech Lead, Developer, Tester, QA with loops
```

Create `.itero/simple-dev-tester.yml` (echo-based for dry run / testing):

```yaml
name: Simple Dev + Tester
steps:
  - id: developer
    role: Developer
    agent:
      custom_command: "echo 'Developer: {prompt}'"
    prompt: |
      Implement the changes described in {{input_file}}.
      Read {{input_content}} for instructions.
    goto: tester

  - id: tester
    role: Tester
    agent:
      custom_command: "echo 'Tester: {prompt}'"
    prompt: |
      Delete test_report.md if exists in {{run_dir}}. Run the project tests. If they fail, create test_report.md
      in the run directory ({{run_dir}}) with the failure details.
      If all pass, do not create any report file.
    goto:
      default: end
      when_files_exist:
        - files: [test_report.md]
          then: developer
```

Copy `full-pipeline.yml` from the examples (or create a minimal version). The full example is at `itero/.examples/full-pipeline.yml`.

## Step 5. Create Sample Input File

Create `instructions.md` in the project root:

```markdown
# Instructions
Add a new feature: [describe the task].
```

## Step 6. Add to `.gitignore`

```bash
echo ".itero/run/" >> .gitignore
```

## Step 7. Add Makefile Targets

Append to the project's `Makefile` (create one if it doesn't exist):

```makefile
# Itero
WORKFLOW ?= simple-dev-tester
INPUT ?= instructions.md

run-itero:
	itero run $(WORKFLOW) $(INPUT)

run-itero-dry-run:
	itero run simple-dev-tester instructions.md

list-itero-workflows:
	itero list
```

## Step 8. Dry Run Test

Run a dry run using the echo-based workflow (no real LLM, just validates setup):

```bash
itero run simple-dev-tester instructions.md
```

Expected output: Steps complete with echo output, then "Run completed. Output: .itero/run/<uuid>".

## Step 9. Verify Workflows

```bash
itero list
```

Expected: Both workflows show ✓.

## Switching to a Real Agent

Edit `.itero/simple-dev-tester.yml` (and other workflows) and replace the `custom_command` echo with a real agent:

```yaml
# Instead of:
custom_command: "echo 'Developer: {prompt}'"

# Use (example with Gemini):
custom_command: "gemini -y -p '{prompt}'"
```

## Examples Reference

- `itero/.examples/workflows.yml` — Index format
- `itero/.examples/simple-dev-tester.yml` — Dev + Tester loop
- `itero/.examples/full-pipeline.yml` — Full pipeline (Tech Lead, Dev, Tester, QA)
- `itero/STEP_BY_STEP.md` — Human-friendly walkthrough
