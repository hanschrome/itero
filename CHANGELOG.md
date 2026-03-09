# Changelog

All notable changes to Itero will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-03-09

### Added

- Initial release
- CLI commands: `itero run <workflow> <input_file>`, `itero list`
- YAML workflows with steps, conditions, and GOTO
- `workflows.yml` index to reference workflow definitions
- `when` conditions: `run_if_files_exist`, `run_if_files_not_exist`
- `goto` with `when_files_exist` (including `then: end`)
- `CustomCommandAgent` with `{prompt}` and `{run_dir}` placeholders
- Prompt variables: `{{input_file}}`, `{{run_dir}}`, `{{project_root}}`, `{{input_content}}`
- Run directory per execution (`run/<uuid>/`)
- Example workflows: simple-dev-tester, full-pipeline
- Unit and integration tests (39 tests)
- MIT License
