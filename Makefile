.PHONY: install lint format-check typecheck test build twine-check ci clean

install:
	uv sync --extra dev --frozen

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy src

test:
	uv run pytest

build:
	rm -rf dist
	uv build --package pymojis
	uv build --package pymojis-fulldata

twine-check:
	uv run twine check dist/*

ci: lint format-check typecheck test build twine-check

clean:
	rm -rf dist build *.egg-info
