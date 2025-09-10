# Repository Guidelines

## Project Structure & Module Organization
- Source: `src/` (core modules like `amazon_dash.py`, `action.py`, `google_*`, `ifttt.py`, `openhab.py`, `models.py`).
- Tests: `tests/` (`test_*.py`, uses pytest; doctests enabled via `pytest.ini`).
- Docs: `docs/` + `mkdocs.yml` (API docs built from docstrings via `scripts/build-docs.sh`).
- Scripts: `scripts/` (versioning, docs, requirements, local run helper).
- Private config: `amazon-dash-private/` (not committed; holds `settings.json`, `buttons.json`, credentials).

## Build, Test, and Development Commands
- `./activate.sh`: Create/activate local venv (Python 3.12) and install dev deps.
- `make help`: List available Make targets.
- `make check`: Run static checks (pre-commit/ruff/mypy via `sniff_check.py`).
- `python -m pytest -vv --cov=src tests/`: Run tests with coverage (CI mirrors this).
- `make docs` or `scripts/build-docs.sh`: Generate docs to `site/` and `docs/docstrings/`.
- Docker (Linux): `docker run --net host -v $PWD/../amazon-dash-private:/amazon-dash-private:ro andgineer/amazon-dash-button-hack`.
- Local run (Mac/Windows): `. ./activate.sh && sudo python src/amazon_dash.py`.

## Coding Style & Naming Conventions
- Python ≥ 3.10 (CI targets 3.10–3.12).
- Linting/formatting: `ruff` (line length ~100, double-quoted docstrings), run via pre-commit.
- Types: `mypy` (ignore_missing_imports; prefer precise annotations in `src/`).
- Naming: modules and functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-mock`, `freezegun`; doctests enabled.
- Naming: `tests/test_*.py`; keep tests deterministic and isolated.
- Coverage: Aim ≥85% (CI enforces green threshold). Run `pytest --cov=src` locally.

## Commit & Pull Request Guidelines
- Commits: short imperative descriptions (project history favors concise lowercase lines).
- Before PR: run `pre-commit run --all-files`, `pytest -vv --cov=src`, and `make docs` if APIs changed.
- PRs must include: clear description, linked issues, configuration notes (if touching `amazon-dash-private` formats), and screenshots/logs when relevant.
- Keep PRs small and focused; update `README.md`/`docs/` when behavior or settings change.

## Security & Configuration Tips
- Never commit secrets. Place `settings.json`, `buttons.json`, Google credentials, and IFTTT key under `amazon-dash-private/` and mount read-only in Docker.
- Validate settings with `src/models.py` schemas; use `bounce_delay` to avoid duplicate press events.
