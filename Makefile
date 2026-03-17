# Dev helper to work on typing stuff
# Continuously run mypy on the codebase

.PHONY: mypy-watch
mypy-watch:
	watch -n 2 uv run mypy

.PHONY: lint
lint:
	uv run pre-commit run --all-files
