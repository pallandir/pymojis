.PHONY: install lint format-check typecheck test build twine-check ci clean data

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

# Regenerate the bundled emoji datasets from Chalda + vendored CLDR sources.
# CLDR sources at third_party/cldr/ are refreshed separately by the
# `refresh-dataset` GitHub workflow — this target never touches the network.
data:
	uv run python scripts/build_dataset.py

clean:
	rm -rf dist build *.egg-info
