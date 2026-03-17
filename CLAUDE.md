# Cadurso — Project Instructions

## Quick Reference

```bash
uv run pytest          # Run tests
make lint              # Run pre-commit (ruff check + ruff format + hooks)
uv run mypy            # Static type checking
```

## Architecture

- `cadurso/` — the library (zero runtime dependencies)
- `tests/` — test suites organized as "universes" (Akira, Brazil, Inception) plus top-level unit tests

### Test Universes

Each universe folder (`tests/akira/`, `tests/brazil/`, `tests/inception/`) is a self-contained authorization system set in a film's world. They follow the same pattern:

- `conftest.py` — actors, resources, permissions (Enums), rules, and a frozen `Cadurso` fixture
- `test_*.py` — plain test functions (never classes) exercising the authorization system
- `README.md` — short description of the universe and entry points

Universe-independent tests (e.g., unit tests for `AuthorizationDecision`, `Veto` edge cases) go in top-level `tests/test_*.py` files. If a test creates its own mini `Cadurso` instead of using a universe fixture, it doesn't belong in a universe folder.

## Code Style

- **Tests are plain functions**, not classes. Follow the Akira/Brazil/Inception pattern.
- **Use Enums for roles/permissions/actions**, not magic strings.
- **Descriptive variable names** for query results: `can_cobb_navigate_limbo`, not `result` or `fluent` or `decision`. Name after what it means, not how it was obtained.
- **No unnecessary comments or docstrings.** Don't add them to code you didn't write. Don't add "this is control flow, not an error"-style commentary.
- Ruff enforces formatting (88 char line length, `preview = true` for string wrapping). Don't fight the formatter — run `make lint` and accept its output.

## CI

The `lints_and_checks` workflow runs `make lint` (which uses `uv run pre-commit run --all-files`) to ensure the same ruff version is used locally and in CI. Always run `make lint` before pushing.
