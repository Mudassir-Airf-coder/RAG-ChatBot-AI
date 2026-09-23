# Contributing

## Setup

1. Install Python 3.11+, uv, and Docker.
2. Clone the repo.
3. `cd backend && uv sync --extra dev`
4. `cd backend && uv run pytest -q`

## Running locally

```bash
./run.sh
```

Open http://localhost:8000

## Code style

- **Python**: follow PEP 8. Run `uv run ruff check app/` before committing.
- **Frontend**: no framework, plain JS. Keep `index.html` self-contained.

## Testing

- All new code must have tests.
- Tests must pass without hitting real APIs. Use mocks.
- Run the full suite before opening a PR: `uv run pytest -q`

## Commit messages

Format: `<type>(<scope>): <summary>`

- **Types**: feat, fix, docs, test, chore, refactor, perf
- **Example**: `fix(parser): handle scanned PDFs with clear error`

## Reporting issues

Open a GitHub issue with:

- What you did
- What you expected
- What happened
- Steps to reproduce
