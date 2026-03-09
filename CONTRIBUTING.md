# Contributing to Itero

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/hanschrome/itero.git
cd itero
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
```

Unit tests only:

```bash
pytest tests/ -v --ignore=tests/integration/
```

Integration tests only:

```bash
pytest tests/integration/ -v
```

## Code Style

- Follow the existing structure (domain, adapters, application layers)
- Add tests for new features
- Keep the hexagonal architecture: domain defines ports, adapters implement them

## Submitting Changes

1. Fork the repository
2. Create a branch (`git checkout -b feature/my-feature`)
3. Make your changes and ensure tests pass
4. Commit with clear messages
5. Open a Pull Request describing the change and why it's needed

## Questions?

Open an issue for bugs, features, or questions.
