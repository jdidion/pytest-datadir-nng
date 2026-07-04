# AGENTS.md

Maintenance notes for `pytest-datadir-nng`, a pytest plugin providing the
`datadir` and `datadir_copy` fixtures.

## Layout
- `pytest_datadir_nng/__init__.py` - the plugin (registered as a `pytest11`
  entry point in `pyproject.toml`); exposes the `datadir` and `datadir_copy`
  fixtures.
- `tests/` - test suite plus the `tests/data/` resource tree used by the
  fixture-resolution tests.

## Build / test / release (uv)
- Trunk branch is `main`.
- Sync the dev environment: `uv sync`
- Run the tests: `uv run pytest`
- Run with coverage: `uv run pytest --cov --cov-report term-missing`
- Lint: `uv run ruff check .`
- Build sdist + wheel: `uv build`

## Versioning
Version is derived from git tags by `setuptools-scm` (`dynamic = ["version"]`).
To cut a release, create an annotated tag like `v1.2.0` on `main`; the build
picks it up automatically. When no tag is reachable the build falls back to the
`fallback_version` declared in `[tool.setuptools_scm]`.

Release is a human-only step (tag, build, publish). Do not push tags or publish
automatically.
